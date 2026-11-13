#!/usr/bin/env python3
"""Robot de mise à jour du marché.

Lit config/tickers.json et config/indices.json, puis écrit :
- data/market.json : chaque valeur suivie avec environ un an de clôtures, et les courbes des taux
  (Trésor américain et zone euro AAA de la BCE), aujourd'hui et il y a un mois ;
- data/heatmap.json : la variation du jour des valeurs des cartes de marché.

Sources :
- Yahoo Finance (yfinance) : actions, indices, devises, matières premières, crypto. Différé d'environ
  15 minutes, sans garantie. Chaque valeur est demandée séparément, et son dernier point est le dernier
  cours affiché par Yahoo, daté sur sa place de cotation.
- Trésor américain (home.treasury.gov) : courbe officielle des taux, publiée chaque jour ouvré vers 22 h (Paris).
- Banque centrale européenne (data-api.ecb.europa.eu) : courbe des emprunts d'État AAA de la zone euro et
  €STR, publiés chaque jour ouvré pour la veille.

Si une valeur ne répond pas, ses symboles de secours sont essayés, puis l'ancienne donnée est gardée et
signalée. Si rien ne répond, les fichiers ne sont pas touchés.
"""
import csv
import datetime as dt
import io
import json
import math
import os
import pathlib
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from zoneinfo import ZoneInfo

RACINE = pathlib.Path(__file__).resolve().parent.parent
PARIS = ZoneInfo("Europe/Paris")
ADRESSE_APP = "https://fayzzy11.github.io/Hub_Global/#/marche"
RESUME_DEFAUT = ["^FCHI", "^STOXX50E", "^GSPC", "^NDX", "^N225", "EURUSD=X", "^TNX", "GC=F", "BZ=F", "BTC-USD"]
OUVRIERS = 4  # valeurs demandées en parallèle à Yahoo

# Maturités affichées sur les courbes (libellé, durée en années)
MAT_TRESOR = [("1 Mo", "1M", 1 / 12), ("2 Mo", "2M", 2 / 12), ("3 Mo", "3M", .25), ("6 Mo", "6M", .5), ("1 Yr", "1A", 1), ("2 Yr", "2A", 2),
              ("3 Yr", "3A", 3), ("5 Yr", "5A", 5), ("7 Yr", "7A", 7), ("10 Yr", "10A", 10), ("20 Yr", "20A", 20), ("30 Yr", "30A", 30)]
MAT_BCE = [("SR_3M", "3M", .25), ("SR_6M", "6M", .5), ("SR_1Y", "1A", 1), ("SR_2Y", "2A", 2), ("SR_3Y", "3A", 3), ("SR_5Y", "5A", 5),
           ("SR_7Y", "7A", 7), ("SR_10Y", "10A", 10), ("SR_15Y", "15A", 15), ("SR_20Y", "20A", 20), ("SR_30Y", "30A", 30)]
CLE_BCE = "YC/B.U2.EUR.4F.G_N_A.SV_C_YM."


def lire(chemin, defaut):
    try:
        return json.loads((RACINE / chemin).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return defaut


def ecrire(chemin, objet):
    """Écriture atomique : le fichier n'est remplacé que s'il est complet."""
    cible = RACINE / chemin
    cible.parent.mkdir(parents=True, exist_ok=True)
    tmp = cible.with_suffix(".tmp")
    tmp.write_text(json.dumps(objet, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    os.replace(tmp, cible)


def arrondi(x):
    return round(x, 4 if abs(x) < 20 else 2)


# ---------------------------------------------------------------- Yahoo

def serie(symbole, jours):
    """Renvoie ([(date ISO, clôture), ...], heure ISO du dernier cours), ou None si Yahoo ne répond pas.
    « jours » : profondeur demandée en jours calendaires (une date de début passe partout, alors que
    certaines valeurs refusent les périodes toutes faites comme « 6mo »)."""
    import yfinance as yf

    debut = (dt.date.today() - dt.timedelta(days=jours)).isoformat()
    for essai in (1, 2, 3):
        try:
            valeur = yf.Ticker(symbole)
            histo = valeur.history(start=debut, interval="1d", auto_adjust=False)
            if histo is None or len(histo) < 2:  # certains contrats (gaz TTF…) répondent mieux à une période toute faite
                histo = valeur.history(period="1y" if jours > 30 else "1mo", interval="1d", auto_adjust=False)
            meta = valeur.history_metadata or {}
            break
        except Exception as e:  # réseau, quota, cache occupé : on réessaie, puis on abandonne cette valeur
            print(f"{symbole} : essai {essai} en échec ({e})", file=sys.stderr)
            time.sleep(2 * essai)
    else:
        return None
    points = []
    if histo is not None and not histo.empty and "Close" in histo:
        points = [(d.date().isoformat(), float(v)) for d, v in histo["Close"].dropna().items() if math.isfinite(float(v))]
    # Dernier cours affiché par Yahoo : il fait foi pour le dernier point (l'historique seul a parfois une séance de retard)
    prix, quand = meta.get("regularMarketPrice"), meta.get("regularMarketTime")
    heure = None
    try:
        if isinstance(quand, (int, float)):
            quand = dt.datetime.fromtimestamp(quand, ZoneInfo(meta.get("exchangeTimezoneName") or "UTC"))
        if quand is not None and prix is not None and math.isfinite(float(prix)) and float(prix) > 0:
            jour, heure = quand.date().isoformat(), quand.isoformat(timespec="minutes")
            if points and jour < points[-1][0]:  # dernier cours affiché plus ancien que l'historique : l'historique fait foi
                heure = None
            else:
                points = [p for p in points if p[0] < jour] + [(jour, float(prix))]
    except (TypeError, ValueError, KeyError) as e:
        print(f"{symbole} : dernier cours illisible ({e}), historique seul utilisé", file=sys.stderr)
    if len(points) < 2:
        print(f"{symbole} : réponse vide ou trop courte ({len(points)} point)", file=sys.stderr)
        return None
    return points, heure


def lire_valeur(symbole, secours, jours):
    """Essaie le symbole, puis ses symboles de secours. Renvoie (points, heure, symbole qui a répondu) ou None."""
    for s in [symbole, *secours]:
        r = serie(s, jours)
        if r:
            return r[0], r[1], s
    return None


# ---------------------------------------------------------------- Trésor américain et BCE

def telecharger(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (hub-robot)", "Accept": "text/csv,*/*"})
    for essai in (1, 2, 3):
        try:
            return urllib.request.urlopen(req, timeout=45).read().decode("utf-8", "replace")
        except Exception as e:
            print(f"{url[:90]} : essai {essai} en échec ({e})", file=sys.stderr)
            time.sleep(3 * essai)
    return None


def tresor():
    """Courbe officielle du Trésor américain : {colonne: [(date ISO, taux), ...]} sur l'année en cours et la précédente."""
    an, lignes = dt.date.today().year, []
    for a in (an - 1, an):
        t = telecharger(f"https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/{a}/all"
                        f"?type=daily_treasury_yield_curve&field_tdr_date_value={a}&page&_format=csv")
        if t:
            lignes += list(csv.DictReader(io.StringIO(t)))
    series = {}
    for l in lignes:
        try:
            m, j, a = l["Date"].split("/")
            d = f"{a}-{m}-{j}"
        except (KeyError, ValueError):
            continue
        for k, v in l.items():
            if k != "Date" and v not in (None, "", "N/A"):
                try:
                    series.setdefault(k, []).append((d, float(v)))
                except ValueError:
                    pass
    return {k: sorted(set(v)) for k, v in series.items()}


def bce(cles, jours):
    """Séries de la BCE : {clé « JEU/SÉRIE » : [(date ISO, valeur), ...]}. Une requête par jeu de données."""
    debut = (dt.date.today() - dt.timedelta(days=jours)).isoformat()
    par_jeu, sortie = {}, {}
    for c in cles:
        jeu, s = c.split("/", 1)
        par_jeu.setdefault(jeu, set()).add(s)
    for jeu, S in par_jeu.items():
        # Les séries d'un même jeu ne diffèrent que par leur dernier élément : on les regroupe avec « + »
        racines = {}
        for s in S:
            tete, _, fin = s.rpartition(".")
            racines.setdefault(tete, []).append(fin)
        for tete, fins in racines.items():
            t = telecharger(f"https://data-api.ecb.europa.eu/service/data/{jeu}/{tete}.{'+'.join(sorted(fins))}?startPeriod={debut}&format=csvdata")
            if not t:
                continue
            for l in csv.DictReader(io.StringIO(t)):
                try:
                    k = l["KEY"].split(".", 1)[1]
                    sortie.setdefault(f"{jeu}/{k}", []).append((l["TIME_PERIOD"], float(l["OBS_VALUE"])))
                except (KeyError, ValueError, IndexError):
                    pass
    return {k: sorted(v) for k, v in sortie.items()}


def courbe(nom, source, maturites, series):
    """Courbe du dernier jour connu et celle d'il y a environ un mois."""
    dates = sorted({d for m in maturites for d, _ in series.get(m[0], [])})
    if not dates:
        return None
    der = dates[-1]
    cible = (dt.date.fromisoformat(der) - dt.timedelta(days=30)).isoformat()
    avant = max([d for d in dates if d <= cible], default=None)

    def points(jour):
        P = []
        for cle, lib, ans in maturites:
            v = dict(series.get(cle, [])).get(jour)
            if v is not None:
                P.append({"m": lib, "a": round(ans, 4), "v": round(v, 3)})
        return P
    return {"nom": nom, "source": source, "date": der, "points": points(der), "date_mois": avant, "points_mois": points(avant) if avant else []}


# ---------------------------------------------------------------- Message Discord

def nombre(x):
    """Nombre à la française : 8 361,36."""
    return f"{x:,.{4 if abs(x) < 20 else 2}f}".replace(",", " ").replace(".", ",")


def creneau(iso):
    """Tranche de la journée (heure de Paris) : au plus un message Discord par tranche."""
    try:
        d = dt.datetime.fromisoformat(iso).astimezone(PARIS)
    except (TypeError, ValueError):
        return None
    return d.date().isoformat(), (0 if d.hour < 11 else 1 if d.hour < 15 else 2 if d.hour < 19 else 3)


def preparer_message(avant, maintenant, lignes, choix, rates):
    """Prépare le message Discord dans le fichier indiqué par MESSAGE_DISCORD (le workflow l'envoie après l'enregistrement).
    Un message par tranche de la journée : matin, midi, après-midi, soir."""
    cible = os.environ.get("MESSAGE_DISCORD")
    if not cible or (creneau(avant) == creneau(maintenant) and not os.environ.get("FORCER_MESSAGE")):
        return
    par = {l["symbole"]: l for l in lignes}

    def trait(l):
        if l["devise"] == "%":  # un taux : variation en points de base
            ecart = (l["cours"] - l["cloture_precedente"]) * 100
            return f"{l['nom']} **{l['cours']:.2f} %** ({'+' if ecart >= 0 else '−'}{abs(ecart):.0f} pb)".replace(".", ",")
        v = l["variation_pct"]
        return f"{l['nom']} **{nombre(l['cours'])}** ({'+' if v >= 0 else '−'}{f'{abs(v):.2f}'.replace('.', ',')} %)"

    cites = [trait(par[s]) for s in choix if s in par and par[s].get("cours") is not None and par[s].get("variation_pct") is not None and not par[s].get("erreur")]
    quand = dt.datetime.fromisoformat(maintenant)
    texte = f"**Marché mis à jour** · {quand:%d/%m} à {quand:%H:%M}\n" + "\n".join("• " + c for c in cites)
    if rates:
        texte += f"\nSans réponse : {', '.join(rates)}"
    texte += f"\n<{ADRESSE_APP}>"
    pathlib.Path(cible).write_text(json.dumps({"username": "Hub · Marché", "content": texte[:1900]}, ensure_ascii=False), encoding="utf-8")
    print("Message Discord préparé.")


# ---------------------------------------------------------------- Programme

def compacter(pts):
    """Historique compact : une date de départ, puis l'écart en jours et la clôture de chaque séance."""
    d0 = dt.date.fromisoformat(pts[0][0])
    return {"d0": pts[0][0], "j": [(dt.date.fromisoformat(d) - d0).days for d, _ in pts], "c": [arrondi(c) for _, c in pts]}


def main():
    debut_passage = time.time()
    cfg = lire("config/tickers.json", {})
    suivis = [t for t in cfg.get("tickers", []) if t.get("symbole")]
    indices = lire("config/indices.json", {}).get("indices", [])
    garde = int(cfg.get("historique_jours", 375))  # jours calendaires d'historique gardés (375 : un an et un peu plus)
    profondeur = garde + 5
    limite = (dt.date.today() - dt.timedelta(days=garde)).isoformat()
    maintenant = dt.datetime.now(PARIS).isoformat(timespec="minutes")

    # ---------- sources officielles des taux ----------
    T = tresor()  # sert aussi à la courbe des taux américains
    cles_bce = sorted({t["serie"] for t in suivis if t.get("source") == "bce"} | {CLE_BCE + m[0] for m in MAT_BCE})
    B = bce(cles_bce, profondeur)
    print(f"Trésor : {len(T)} maturités ; BCE : {len(B)} séries")

    # ---------- tableau : data/market.json ----------
    precedent = lire("data/market.json", {})
    ancien = {} if precedent.get("exemple") else {t["symbole"]: t for t in precedent.get("tickers", [])}  # les exemples fictifs ne sont jamais gardés

    def obtenir(t):
        src = t.get("source")
        if src == "tresor":
            pts = T.get(t.get("colonne", ""), [])
            return (pts, None, "Trésor américain") if len(pts) >= 2 else None
        if src == "bce":
            pts = B.get(t.get("serie", ""), [])
            return (pts, None, "BCE") if len(pts) >= 2 else None
        return lire_valeur(t["symbole"], t.get("secours", []), profondeur)

    with ThreadPoolExecutor(OUVRIERS) as pool:
        reponses = list(pool.map(obtenir, suivis))
    lignes, rates = [], []
    for t, r in zip(suivis, reponses):
        s = t["symbole"]
        base = {k: t[k] for k in ("symbole", "nom", "devise", "groupe", "sous_groupe", "court") if t.get(k)}
        if r:
            pts, heure, source = r
            pts = [p for p in pts if p[0] >= limite] or pts[-2:]
            dernier, avant = pts[-1][1], pts[-2][1]
            ligne = {**base, "cours": arrondi(dernier), "variation_pct": round((dernier / avant - 1) * 100, 2) if avant else None,
                     "cloture_precedente": arrondi(avant), "date_cours": pts[-1][0], "heure_cours": heure, "h": compacter(pts)}
            if source not in (s, None):
                ligne["source"] = source  # symbole de secours, Trésor ou BCE
            lignes.append(ligne)
        else:
            rates.append(s)
            if s in ancien:  # on garde la dernière donnée connue, en le signalant
                lignes.append({**ancien[s], **base, "erreur": "non rafraîchi"})
            else:
                lignes.append({**base, "cours": None, "variation_pct": None, "erreur": "indisponible"})
    if suivis and len(rates) == len(suivis):
        print("Aucune valeur n'a répondu : data/market.json est laissé tel quel.", file=sys.stderr)
        return 1
    courbes = {}
    cu = courbe("États-Unis · emprunts du Trésor", "Trésor américain", MAT_TRESOR, T)
    ce = courbe("Zone euro · emprunts d'État notés AAA", "BCE", [(CLE_BCE + c, l, a) for c, l, a in MAT_BCE], B)
    if cu:
        courbes["us"] = cu
    if ce:
        courbes["eur"] = ce
    if not courbes and precedent.get("courbes"):
        courbes = precedent["courbes"]  # garde les dernières courbes connues
    ecrire("data/market.json", {"derniere_maj": maintenant, "format": 2, "source": "Yahoo Finance (différé d'environ 15 minutes, non garanti), Trésor américain, BCE",
                                "tickers": lignes, "courbes": courbes})
    print(f"market.json : {len(suivis) - len(rates)} valeurs à jour sur {len(suivis)}" + (f" ; sans réponse : {', '.join(rates)}" if rates else ""))
    if rates:
        print(f"::warning::Valeurs sans réponse : {', '.join(rates)}")
    preparer_message(precedent.get("derniere_maj"), maintenant, lignes, cfg.get("notification") or RESUME_DEFAUT, rates)

    # ---------- cartes : data/heatmap.json ----------
    symboles = sorted({v["symbole"] for i in indices for v in i.get("valeurs", [])})
    with ThreadPoolExecutor(OUVRIERS) as pool:
        jour = {s: r[0] for s, r in zip(symboles, pool.map(lambda s: serie(s, 12), symboles)) if r}
    if symboles and not jour:
        print("Aucun constituant n'a répondu : data/heatmap.json est laissé tel quel.", file=sys.stderr)
        return 0
    manquants = [s for s in symboles if s not in jour]
    if manquants:
        print(f"::warning::Constituants sans réponse : {', '.join(manquants)}")
    cartes = []
    for i in indices:
        valeurs = []
        for v in i.get("valeurs", []):
            pts = jour.get(v["symbole"])
            valeurs.append({**v, "variation_pct": round((pts[-1][1] / pts[-2][1] - 1) * 100, 2) if pts and pts[-2][1] else None})
        cartes.append({"id": i["id"], "nom": i["nom"], "note": i.get("note", ""), "valeurs": valeurs})
    ecrire("data/heatmap.json", {"derniere_maj": maintenant, "source": "Yahoo Finance (différé, non garanti) ; poids indicatifs", "indices": cartes})
    print(f"heatmap.json : {len(jour)} constituants à jour sur {len(symboles)} ; passage en {time.time() - debut_passage:.0f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())

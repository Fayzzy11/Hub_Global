#!/usr/bin/env python3
"""Robot de mise à jour du marché.

Lit config/tickers.json et config/indices.json, récupère les cours avec yfinance,
puis écrit data/market.json (tableau et tendances) et data/heatmap.json (cartes).

À savoir : yfinance fournit des cours différés (environ 15 minutes), sans garantie.
Chaque valeur est demandée séparément, et son dernier point est le dernier cours
affiché par Yahoo (avec sa date sur sa place de cotation) : c'est ce qui garantit
que l'Asie, l'Europe et les États-Unis sont chacun à leur dernière séance.
Si une valeur ne répond pas, ses symboles de secours sont essayés, puis l'ancienne
donnée est gardée et signalée. Si rien ne répond, les fichiers ne sont pas touchés.
"""
import datetime as dt
import json
import math
import os
import pathlib
import sys
import time
from zoneinfo import ZoneInfo

RACINE = pathlib.Path(__file__).resolve().parent.parent
PARIS = ZoneInfo("Europe/Paris")
ADRESSE_APP = "https://fayzzy11.github.io/Hub_Global/#/marche"
# Valeurs citées dans le message Discord (modifiable dans config/tickers.json, clé "notification")
RESUME_DEFAUT = ["^FCHI", "^STOXX50E", "^GSPC", "^NDX", "^N225", "EURUSD=X", "^TNX", "GC=F", "BZ=F", "BTC-USD"]


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


def serie(symbole, jours):
    """Renvoie ([(date ISO, clôture), ...], heure ISO du dernier cours), ou None si Yahoo ne répond pas.
    « jours » : profondeur demandée, en jours calendaires (une date de début passe partout, alors que
    certaines valeurs refusent les périodes toutes faites comme « 6mo »)."""
    import yfinance as yf

    debut = (dt.date.today() - dt.timedelta(days=jours)).isoformat()
    for essai in (1, 2):
        try:
            valeur = yf.Ticker(symbole)
            histo = valeur.history(start=debut, interval="1d", auto_adjust=False)
            meta = valeur.history_metadata or {}
            break
        except Exception as e:  # réseau, quota : un second essai, puis on abandonne cette valeur
            print(f"{symbole} : essai {essai} en échec ({e})", file=sys.stderr)
            time.sleep(3)
    else:
        return None
    points = []
    if histo is not None and not histo.empty and "Close" in histo:
        points = [(d.date().isoformat(), float(v)) for d, v in histo["Close"].dropna().items()]
    # Dernier cours affiché par Yahoo : il fait foi pour le dernier point (l'historique seul a parfois une séance de retard)
    prix, quand = meta.get("regularMarketPrice"), meta.get("regularMarketTime")
    heure = None
    try:
        if isinstance(quand, (int, float)):
            quand = dt.datetime.fromtimestamp(quand, ZoneInfo(meta.get("exchangeTimezoneName") or "UTC"))
        if quand is not None and prix is not None and math.isfinite(float(prix)) and float(prix) > 0:
            jour, heure = quand.date().isoformat(), quand.isoformat(timespec="minutes")
            if points and jour < points[-1][0]:  # dernier cours affiché plus ancien que l'historique : l'historique fait foi
                print(f"{symbole} : dernier cours affiché daté du {jour}, plus ancien que l'historique ({points[-1][0]}) ; historique utilisé", file=sys.stderr)
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


def arrondi(x):
    return round(x, 4 if abs(x) < 20 else 2)


def nombre(x):
    """Nombre à la française : 8 361,36."""
    return f"{x:,.{4 if abs(x) < 20 else 2}f}".replace(",", "\u202f").replace(".", ",")


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


def main():
    cfg = lire("config/tickers.json", {})
    suivis = [t for t in cfg.get("tickers", []) if t.get("symbole")]
    indices = lire("config/indices.json", {}).get("indices", [])
    garde = int(cfg.get("historique_jours", 70))
    maintenant = dt.datetime.now(PARIS).isoformat(timespec="minutes")

    # ---------- tableau : data/market.json ----------
    precedent = lire("data/market.json", {})
    ancien = {} if precedent.get("exemple") else {t["symbole"]: t for t in precedent.get("tickers", [])}  # les exemples fictifs ne sont jamais gardés
    lignes, rates = [], []
    for t in suivis:
        s = t["symbole"]
        base = {k: t.get(k, "") for k in ("symbole", "nom", "devise", "groupe", "sous_groupe")}
        r = lire_valeur(s, t.get("secours", []), 190)
        if r:
            pts, heure, source = r
            pts = pts[-garde:]
            dernier, avant = pts[-1][1], pts[-2][1]
            ligne = {**base, "cours": arrondi(dernier), "variation_pct": round((dernier / avant - 1) * 100, 2) if avant else None,
                     "cloture_precedente": arrondi(avant), "date_cours": pts[-1][0], "heure_cours": heure, "historique": [{"d": d, "c": arrondi(c)} for d, c in pts]}
            if source != s:
                ligne["symbole_source"] = source  # c'est un symbole de secours qui a répondu
            lignes.append(ligne)
        else:
            rates.append(s)
            if s in ancien:  # on garde la dernière donnée connue, en le signalant
                lignes.append({**ancien[s], **base, "erreur": "non rafraîchi"})
            else:
                lignes.append({**base, "cours": None, "variation_pct": None, "historique": [], "erreur": "indisponible"})
    if suivis and len(rates) == len(suivis):
        print("Aucune valeur n'a répondu : data/market.json est laissé tel quel.", file=sys.stderr)
        return 1
    ecrire("data/market.json", {"derniere_maj": maintenant, "source": "yfinance (différé d'environ 15 minutes, non garanti)", "tickers": lignes})
    print(f"market.json : {len(suivis) - len(rates)} valeurs à jour sur {len(suivis)}" + (f" ; sans réponse : {', '.join(rates)}" if rates else ""))
    if rates:
        print(f"::warning::Valeurs sans réponse de Yahoo : {', '.join(rates)}")
    preparer_message(precedent.get("derniere_maj"), maintenant, lignes, cfg.get("notification") or RESUME_DEFAUT, rates)

    # ---------- cartes : data/heatmap.json ----------
    symboles = sorted({v["symbole"] for i in indices for v in i.get("valeurs", [])})
    jour = {}
    for s in symboles:
        r = serie(s, 12)
        if r:
            jour[s] = r[0]
    if symboles and not jour:
        print("Aucun constituant n'a répondu : data/heatmap.json est laissé tel quel.", file=sys.stderr)
        return 0
    manquants = [s for s in symboles if s not in jour]
    if manquants:
        print(f"::warning::Constituants sans réponse de Yahoo : {', '.join(manquants)}")
    cartes = []
    for i in indices:
        valeurs = []
        for v in i.get("valeurs", []):
            pts = jour.get(v["symbole"])
            valeurs.append({**v, "variation_pct": round((pts[-1][1] / pts[-2][1] - 1) * 100, 2) if pts and pts[-2][1] else None})
        cartes.append({"id": i["id"], "nom": i["nom"], "note": i.get("note", ""), "valeurs": valeurs})
    ecrire("data/heatmap.json", {"derniere_maj": maintenant, "source": "yfinance (différé, non garanti) ; poids indicatifs", "indices": cartes})
    print(f"heatmap.json : {len(jour)} constituants à jour sur {len(symboles)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

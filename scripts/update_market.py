#!/usr/bin/env python3
"""Robot de mise à jour du marché.

Lit config/tickers.json et config/indices.json, récupère les cours avec yfinance,
puis écrit data/market.json (tableau et tendances) et data/heatmap.json (cartes).

À savoir : yfinance fournit des cours différés (environ 15 minutes), sans garantie.
Si une valeur ne répond pas, l'ancienne donnée est gardée et signalée.
Si rien ne répond, les fichiers existants ne sont pas touchés.
"""
import datetime as dt
import json
import os
import pathlib
import sys
from zoneinfo import ZoneInfo

RACINE = pathlib.Path(__file__).resolve().parent.parent
LOT = 60  # nombre de symboles demandés à la fois


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


def clotures(symboles, periode):
    """Renvoie {symbole: [(date ISO, clôture), ...]} pour les symboles qui ont répondu."""
    import yfinance as yf

    resultat = {}
    for i in range(0, len(symboles), LOT):
        lot = symboles[i:i + LOT]
        try:
            df = yf.download(lot, period=periode, interval="1d", group_by="ticker", auto_adjust=False, progress=False, threads=True)
        except Exception as e:  # réseau, quota : on passe au lot suivant
            print(f"Lot {i // LOT + 1} en échec : {e}", file=sys.stderr)
            continue
        if df is None or df.empty:
            continue
        niveaux = getattr(df.columns, "nlevels", 1)
        for s in lot:
            try:
                serie = (df[s]["Close"] if niveaux > 1 else df["Close"]).dropna()
            except (KeyError, TypeError):
                continue
            points = [(d.date().isoformat(), float(v)) for d, v in serie.items()]
            if len(points) >= 2:
                resultat[s] = points
    return resultat


def arrondi(x):
    return round(x, 4 if abs(x) < 20 else 2)


def main():
    cfg = lire("config/tickers.json", {})
    suivis = [t for t in cfg.get("tickers", []) if t.get("symbole")]
    indices = lire("config/indices.json", {}).get("indices", [])
    garde = int(cfg.get("historique_jours", 70))
    maintenant = dt.datetime.now(ZoneInfo("Europe/Paris")).isoformat(timespec="minutes")

    # ---------- tableau : data/market.json ----------
    precedent = lire("data/market.json", {})
    ancien = {} if precedent.get("exemple") else {t["symbole"]: t for t in precedent.get("tickers", [])}  # les exemples fictifs ne sont jamais gardés
    cours = clotures([t["symbole"] for t in suivis], "6mo") if suivis else {}
    lignes, rates = [], []
    for t in suivis:
        s, pts = t["symbole"], cours.get(t["symbole"])
        base = {k: t.get(k, "") for k in ("symbole", "nom", "devise", "groupe", "sous_groupe")}
        if pts:
            pts = pts[-garde:]
            dernier, avant = pts[-1][1], pts[-2][1]
            lignes.append({**base, "cours": arrondi(dernier), "variation_pct": round((dernier / avant - 1) * 100, 2) if avant else None,
                           "cloture_precedente": arrondi(avant), "date_cours": pts[-1][0], "historique": [{"d": d, "c": arrondi(c)} for d, c in pts]})
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

    # ---------- cartes : data/heatmap.json ----------
    symboles = sorted({v["symbole"] for i in indices for v in i.get("valeurs", [])})
    jour = clotures(symboles, "5d") if symboles else {}
    if symboles and not jour:
        print("Aucun constituant n'a répondu : data/heatmap.json est laissé tel quel.", file=sys.stderr)
        return 0
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

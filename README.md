# Hub · Noah

Tableau de bord personnel sous forme d'application installable : quartier financier 3D, marché, cartes d'indices, cours, documents, réseau, briefs, bot.

## Comment c'est construit

- **Ce dépôt (public)** contient uniquement le code de l'application et les données de marché. Aucune donnée personnelle.
- **Les données personnelles** (fiches de projets, contacts, cours, briefs, documents) vivent dans un **dépôt privé séparé**. L'application les lit et les écrit avec un jeton GitHub personnel, saisi une fois par appareil et gardé dans le navigateur.
- Pas de serveur à gérer : GitHub Pages sert l'application, l'API de GitHub sert les données, GitHub Actions met le marché à jour.

## Mise en route

1. **Activer GitHub Pages** : Settings > Pages > Source « Deploy from a branch », branche `main`, dossier `/ (root)`.
   L'application est alors à l'adresse `https://<compte>.github.io/<dépôt>/`.
2. **Autoriser le robot du marché** : Settings > Actions > General > Workflow permissions > « Read and write permissions ».
   Puis onglet Actions > « Mise à jour du marché » > Run workflow pour un premier passage.
3. **Créer un dépôt privé** pour les données, par exemple `Hub_data`.
4. **Créer un jeton** : github.com/settings/personal-access-tokens/new (jeton « fine-grained »).
   Repository access : « Only select repositories », le dépôt privé. Permissions : `Contents` en lecture et écriture.
5. **Connecter l'application** : Réglages > Dépôt privé, coller le jeton, choisir un code de protection.
6. **Installer** : bouton « Installer » du navigateur (PC, Android) ou Partager > « Sur l'écran d'accueil » (iPhone).

## Marché

- `config/tickers.json` : valeurs suivies (indices, taux et obligations, matières premières, devises, volatilité, crypto, ETF). Symboles Yahoo Finance.
- `config/indices.json` : composition des cartes par indice, avec des poids indicatifs.
- `scripts/update_market.py` : récupère les cours avec yfinance et écrit `data/market.json` et `data/heatmap.json`.
- `.github/workflows/update.yml` : 4 passages par jour en semaine. La fréquence se change sur la ligne `cron`.

Les cours sont différés (environ 15 minutes) et non garantis. Les fichiers livrés au départ sont des exemples fictifs, signalés dans l'interface, remplacés au premier passage du robot.

## Organisation du dépôt privé

```
data/projects.json        fiches de contexte (projets, sites, outils, bot)
data/networking.json      contacts et modèles de messages
data/courses.json         base de cours
data/morning-brief.json   index des briefs
pdf/                      PDF des briefs
documents/                tous les autres fichiers, par dossier
```

## Limites à connaître

- 50 Mo par fichier envoyé depuis l'application ; GitHub recommande de garder un dépôt sous 1 Go.
- En cas de perte d'un appareil : supprimer le jeton sur GitHub coupe l'accès partout.

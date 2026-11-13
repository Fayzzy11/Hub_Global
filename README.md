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

## Univers 3D : le réseau de neurones

- La vue d'accueil montre le hub comme un réseau de neurones : chaque fiche est un neurone qui porte son logo, l'agent global est au centre, et les branches relient les fiches liées entre elles. Plus une fiche est récente, plus son neurone est gros.
- Tout est calculé dans le navigateur avec three.js (embarqué dans `assets/lib/`) : aucune image ni modèle à télécharger pour cette vue.
- Réglages > Décor de l'univers 3D permet de revenir au quartier de La Défense. Réglages > Qualité de la 3D : « Allégée » pour les appareils modestes, « Toujours en liste » pour désactiver la 3D.

## Calendrier

- La vue Calendrier permet d'ajouter, modifier et supprimer des événements directement dans l'app. Ils sont enregistrés dans le dépôt privé (`data/calendrier.json`, créé au premier enregistrement).
- Trois affichages : jour, semaine (grille horaire) et mois. Un clic dans une colonne crée un événement à cette heure.
- « Importer un emploi du temps SKEMA » : colle le texte de la page My Calendar, les séances sont ajoutées sans doublon.
- Chaque événement a une catégorie (couleur et pictogramme, modifiables), un rappel et une répétition éventuelle. Les examens de la base de cours et les relances du carnet réseau s'affichent automatiquement.
- Rappels : une app sans serveur ne peut pas notifier quand elle est fermée. Le bouton « Ajouter à mon agenda » envoie l'événement et son alarme dans l'agenda du téléphone ou de l'ordinateur (fichier `.ics`), qui se charge de la notification. Rien n'est publié dans le dépôt public.

## Quartier 3D (décor optionnel)

- Le quartier s'affiche avec three.js (embarqué dans `assets/lib/`, aucune dépendance à un serveur tiers).
- Les tours, la Grande Arche et le décor sont des modèles réalisés dans Blender, exportés en GLB compressé (`assets/modeles/`, 3,5 Mo au total). Chaque silhouette de tour existe en trois hauteurs : plus la fiche est récente, plus la tour est haute.
- Les scripts qui génèrent ces modèles sont dans `modelisation/`. Pour les régénérer : Python 3.11, `pip install bpy==5.0.1`, puis `python exporter_tours.py` et `python exporter_decor.py` (les fichiers sortent dans `modelisation/modeles/`, à recopier dans `assets/modeles/`).
- En qualité « Allégée », le quartier devient une ville simplifiée dessinée par le code.
- Licences : three.js (MIT, voir `assets/lib/LICENCE-three.txt`), décodeur Draco (Apache 2.0, Google).

## Marché

- `config/tickers.json` : valeurs suivies (indices, taux et obligations, matières premières, devises, volatilité, crypto, ETF). Symboles Yahoo Finance.
- `config/indices.json` : composition des cartes par indice, avec des poids indicatifs.
- `scripts/update_market.py` : récupère les cours avec yfinance et écrit `data/market.json` et `data/heatmap.json`.
- `.github/workflows/update.yml` : un passage par heure en semaine, de 6 h 17 à 21 h 17 UTC (GitHub lance souvent ces passages en retard et en saute certains ; en prévoir un par heure garde les données fraîches). La fréquence se change sur la ligne `cron`.
- Chaque valeur est demandée séparément ; son dernier point est le dernier cours affiché par Yahoo, daté sur sa place de cotation. Une valeur peut avoir des symboles de secours (clé `secours` dans `config/tickers.json`).
- **Message Discord** (facultatif) : ajoute le secret `DISCORD_WEBHOOK_URL` (Settings > Secrets and variables > Actions > New repository secret) avec l'adresse d'un webhook de ton salon. Le robot envoie alors un résumé par tranche de la journée (matin, midi, après-midi, soir) et à chaque lancement à la main. Les valeurs citées se règlent avec la clé `notification` de `config/tickers.json`.

Les cours sont différés (environ 15 minutes) et non garantis. Les fichiers livrés au départ sont des exemples fictifs, signalés dans l'interface, remplacés au premier passage du robot.

## Déposer beaucoup de fichiers

Glisse des fichiers ou des dossiers entiers n'importe où dans la fenêtre (ou utilise « Ajouter des fichiers » / « Ajouter un dossier entier »). Une fenêtre propose une place pour chaque fichier d'après son nom et son dossier : brief (PDF daté), cours, projet, dossier courant, sinon `documents/à trier`. Tu corriges si besoin, puis tout part en un seul enregistrement. Ce rangement suit des règles simples, sans IA. Limite : 50 Mo par fichier.

## Organisation du dépôt privé

```
data/projects.json        fiches de contexte (projets, sites, outils, bot)
data/networking.json      contacts et modèles de messages
data/courses.json         base de cours
data/morning-brief.json   index des briefs
documents/briefs/         PDF des briefs envoyés par « Ajouter le PDF du jour » (AAAA-MM-JJ.pdf)
pdf/                      PDF des briefs ajoutés à la main (ancien emplacement)
documents/cours/<cours>/   fichiers d'un cours
documents/projets/<fiche>/ fichiers d'un projet (bouton « Documents du projet » de la fiche)
documents/à trier/        fichiers sans place reconnue
documents/                tous les autres fichiers, par dossier
```

## Limites à connaître

- 50 Mo par fichier envoyé depuis l'application ; GitHub recommande de garder un dépôt sous 1 Go.
- En cas de perte d'un appareil : supprimer le jeton sur GitHub coupe l'accès partout.

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

## Networking du jour

- Chaque matin en semaine, la routine Claude « Daily Networking Checklist » écrit la checklist du jour dans le dépôt privé (`data/networking.json`, clé `jour`), avec l'état du tracker (contacts, statuts, échéances, compteurs).
- Accueil : une carte compacte montre les actions du jour, cochables, avec un bouton Claude qui ouvre la discussion networking du jour. Sur téléphone, la carte est repliée : touche-la pour la déplier.
- Vue Réseau : le détail de chaque action, les messages prêts à copier-coller (bouton Copier), les compteurs, les jours précédents et l'accès aux documents du tracker (`documents/networking/`).
- Ce que tu coches ou modifies dans l'app est gardé et repris par Claude au passage suivant (journal des modifications) ; la page Checklist réseau et le tracker du projet Claude restent la référence.
- Le script `scripts/hub_sync.py` du dépôt privé fait la conversion (tracker vers `networking.json` et documents).

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

### Dans l'application
- **Vue d'ensemble** : bandeau des chiffres clés, favoris, actions dans le monde (variations sur 1 jour, 1 semaine, 1 mois, 3 mois, depuis janvier, 1 an), plus fortes hausses et baisses, secteurs américains et européens, styles et facteurs, courbes des taux américaine et zone euro (aujourd'hui et il y a un mois, pentes 2-10 ans), devises, matières premières, volatilité et crypto, obligations et crédit.
- **Mes pages** : pages composées à la main, comme un écran de terminal. Panneaux au choix : bandeau, liste, tableau des performances, graphique (comparaison en base 100), classement en barres, plus fortes variations, courbes des taux, carte de marché. Favoris et pages sont enregistrés dans le dépôt privé (`data/marche-perso.json`) et suivent sur tous les appareils.
- **Fiche d'une valeur** (clic sur une valeur ou recherche) : graphique avec curseur, performances, plus haut et plus bas sur un an, étoile des favoris, ajout à une page.
- **Cartes** et **Tableau** : cartes de marché par indice (dont une carte des grandes valeurs de la zone euro) et tableau complet, colonnes au choix.

### Le robot
- `config/tickers.json` : valeurs suivies (symboles Yahoo Finance), classées par catégorie. Clés facultatives : `secours`, `court` (nom court), `source` (`tresor` ou `bce` pour les taux officiels).
- `config/indices.json` : composition des cartes par indice, avec des poids indicatifs.
- `scripts/update_market.py` : écrit `data/market.json` (environ un an de clôtures par valeur, en format compact, et les courbes des taux) et `data/heatmap.json`. Sources : Yahoo Finance (différé d'environ 15 minutes), Trésor américain et BCE (publiés une fois par jour ouvré).
- `.github/workflows/update.yml` : un passage par heure en semaine. **GitHub lance très mal ces passages programmés** (souvent avec des heures de retard, parfois jamais) : c'est pourquoi l'application peut relancer le robot elle-même.
- **Relance depuis l'application** : crée un jeton « fine-grained » limité à ce dépôt, avec la seule permission `Actions : Read and write`, et colle-le dans Réglages > Robot du marché (une fois par appareil). L'application relance alors le robot avec le bouton « Actualiser » et toute seule à l'ouverture quand les cours ont plus d'une heure (en semaine, de 8 h à 23 h, au plus une fois par demi-heure). Ce jeton ne peut ni lire ni modifier les données ou le code.
- **Message Discord** (facultatif) : ajoute le secret `DISCORD_WEBHOOK_URL` (Settings > Secrets and variables > Actions > New repository secret) avec l'adresse d'un webhook de ton salon. Le robot envoie alors un résumé par tranche de la journée (matin, midi, après-midi, soir) et à chaque lancement à la main. Les valeurs citées se règlent avec la clé `notification` de `config/tickers.json`.

Les cours sont différés et non garantis. Les fichiers livrés au départ sont des exemples fictifs, signalés dans l'interface, remplacés au premier passage du robot.

## Bibliothèque : recherche dans le texte des briefs

- À l'envoi d'un PDF (bouton « Ajouter le PDF du jour » ou dépôt de plusieurs PDF), l'application lit son texte dans le navigateur avec pdf.js (embarqué dans `assets/lib/`, licence Apache 2.0) et le range dans `data/briefs-texte.json` du dépôt privé. Le résumé (« The big picture ») et les sociétés citées sont remplis au passage.
- La recherche lit ce texte : taper « nvidia » montre les briefs qui en parlent, avec le nombre de mentions et les passages surlignés. Les sociétés des cartes de marché sont reconnues par leur nom et par leur symbole (« nvidia » et « NVDA »).
- Un bandeau propose de lire le texte des PDF déposés avant cette fonction. Les PDF scannés (images sans texte) ne sont pas lisibles.

## Déposer beaucoup de fichiers

Glisse des fichiers ou des dossiers entiers n'importe où dans la fenêtre (ou utilise « Ajouter des fichiers » / « Ajouter un dossier entier »). Une fenêtre propose une place pour chaque fichier d'après son nom et son dossier : brief (PDF daté), cours, projet, dossier courant, sinon `documents/à trier`. Tu corriges si besoin, puis tout part en un seul enregistrement. Ce rangement suit des règles simples, sans IA. Limite : 50 Mo par fichier.

## Organisation du dépôt privé

```
data/projects.json        fiches de contexte (projets, sites, outils, bot)
data/networking.json      contacts, checklist du jour, compteurs et modèles de messages (écrit par la routine Claude)
documents/networking/     documents du tracker networking (checklists, état des contacts, fichiers du projet Claude)
scripts/hub_sync.py       conversion du tracker vers l'app (utilisé par Claude)
data/courses.json         base de cours
data/morning-brief.json   index des briefs
data/briefs-texte.json    texte des briefs, pour la recherche
data/marche-perso.json    favoris et pages du Marché
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

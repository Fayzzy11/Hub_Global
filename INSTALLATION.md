# Créer ton propre Hub

Le Hub est une application web installable (ordinateur et téléphone) : accueil du jour, univers de
tes projets, marché, bibliothèque de briefs, cours, documents, calendrier, carnet réseau, offres
d'emploi, patrimoine. L'application est publique et ne contient **aucune donnée personnelle** : tout
ce qui est à toi vit dans **ton propre dépôt GitHub privé**, que l'app lit avec un jeton que tu
saisis toi-même sur ton appareil. Personne d'autre (pas même l'auteur de l'app) ne voit tes données.

## Le plus simple : demander à Claude

Dans l'app : **Réglages › Créer ton propre Hub › Copier le prompt d'installation**, puis colle-le
dans une nouvelle conversation Claude. Le prompt ci-dessous est le même ; dans l'app, l'adresse de
l'application y est déjà remplie.

Compte environ 20 minutes. Il te faut un compte GitHub (gratuit).

<!-- DEBUT DU PROMPT -->
```
Tu vas m'aider à installer mon propre « Hub », une application web personnelle open source. Adresse de l'application : {ADRESSE_APP} (code source : {DEPOT_APP}). L'application est publique et ne contient aucune donnée ; mes données iront dans un dépôt GitHub PRIVÉ à moi, que l'application lit avec un jeton que je saisis moi-même dans l'application.

Fonctionnement attendu :
- Réponds dans ma langue, simplement, une étape à la fois. Attends que je te confirme qu'une étape est faite avant de passer à la suivante.
- Ne me demande JAMAIS de coller un jeton, un mot de passe ou un code dans la conversation. Le jeton se colle uniquement dans l'application (Réglages › Dépôt privé).
- Ne mets jamais de donnée personnelle dans un dépôt public.
- N'invente rien sur moi. Si tu as accès à ma mémoire ou à mes projets Claude, propose de t'en servir pour personnaliser, et montre-moi ce que tu comptes écrire avant de l'écrire. Sinon, pose-moi des questions courtes.
- Si tu as un outil GitHub avec droit d'écriture sur mon compte (connecteur GitHub, gh), tu peux créer le dépôt et y écrire les fichiers à ma place, après mon accord. Sinon, guide-moi clic par clic et donne-moi les fichiers à télécharger.

Étapes :

1. Compte GitHub. Vérifie que j'en ai un ; sinon guide-moi sur https://github.com/signup. Note mon identifiant GitHub (le nom du compte, pas l'e-mail).

2. Choix de l'adresse de l'application. Deux options, explique-les-moi en deux phrases et laisse-moi choisir :
   a) utiliser directement {ADRESSE_APP} (rien à installer ; les cours du marché affichés sont ceux suivis par cette instance ; je dépends des mises à jour de son auteur) ;
   b) ma propre copie : sur la page du code source, bouton « Fork » ; puis dans ma copie : Settings › Pages › « Deploy from a branch », branche main, dossier / (root) ; Settings › Actions › General › Workflow permissions › « Read and write permissions » ; onglet Actions › activer les workflows, puis lancer « Mise à jour du marché » une fois. Mon adresse sera https://MON-IDENTIFIANT.github.io/NOM-DE-LA-COPIE/ (quelques minutes après). Je peux choisir mes valeurs suivies dans config/tickers.json de ma copie.

3. Dépôt privé de données. Sur https://github.com/new : nom « Hub_data », visibilité « Private », cocher « Add a README file », créer. (Si tu as l'outil GitHub, crée-le pour moi.)

4. Jeton d'accès. Sur https://github.com/settings/personal-access-tokens/new :
   - Token name : « Hub » ; Expiration : 1 an (je noterai la date pour le renouveler) ;
   - Repository access : « Only select repositories » › Hub_data ;
   - Permissions › Repository permissions › Contents : « Read and write » (rien d'autre) ;
   - « Generate token », puis je copie le jeton (il commence par github_pat_) SANS te l'envoyer.

5. Connexion. J'ouvre l'adresse de l'étape 2 › Réglages › Dépôt privé : compte GitHub = mon identifiant, dépôt = Hub_data, branche = main, je colle le jeton et je choisis un code de protection (il me sera demandé à l'ouverture). L'application me souhaite la bienvenue et me demande mon prénom, mon école (facultatif), l'import d'emploi du temps et le dépôt d'un éventuel bot de veille : elle crée data/profil.json toute seule. Pour l'installer comme une app : sur ordinateur, bouton « Installer » de la barre d'adresse ; sur iPhone, Partager › « Sur l'écran d'accueil ».

6. Personnalisation. Pose-moi une courte série de questions (ou appuie-toi sur ma mémoire et mes projets Claude, avec mon accord) : mes projets en cours, mes cours et examens, mes objectifs, ma recherche de stage ou d'emploi, mes contacts à suivre, mes rendez-vous récurrents. Puis prépare ces fichiers en JSON valide (UTF-8), exactement aux formats décrits plus bas, et montre-moi un résumé avant :
   - data/projects.json : une fiche par projet (et les fiches « outil » standard listées plus bas) ;
   - data/courses.json : une fiche par cours ;
   - data/networking.json : mes contacts et 2 ou 3 modèles de messages dans mon style ;
   - data/calendrier.json : mes catégories et mes événements récurrents.
   Ensuite, soit tu les écris dans mon dépôt Hub_data (si tu as l'outil GitHub), soit tu me donnes le contenu de chaque fichier et je le dépose : sur GitHub, dans Hub_data, « Add file › Create new file », nom « data/projects.json » (le « / » crée le dossier data), je colle le contenu, puis « Commit changes » ; et ainsi de suite pour chaque fichier. N'écris jamais data/profil.json par-dessus celui que l'application a créé, sauf si je te le demande.

7. Vérification. Je recharge l'application (Réglages › Recharger, ou fermer et rouvrir). Demande-moi ce que je vois sur l'Accueil, dans Univers, Cours, Réseau et Calendrier, et corrige les fichiers si quelque chose cloche.

8. Facultatif, si mon Claude peut créer des tâches planifiées : propose-moi une tâche qui, chaque soir, met à jour mes fiches de projets à partir de mes notes de projets Claude. Une tâche planifiée ne peut pas cloner mon dépôt : elle doit utiliser l'outil GitHub pour lire data/projects.json et le réécrire (ou déposer un fichier que traite un robot GitHub Actions). Ne la crée qu'après mon accord.

Formats des fichiers (respecte les noms de champs ; les dates au format AAAA-MM-JJ) :

data/projects.json
{"version": 1, "projets": [
  {"id": "mon-projet", "nom": "Mon projet", "type": "projet Claude", "statut": "actif",
   "objectif": "Une phrase.", "resume": "2 à 4 phrases sur l'état du projet.",
   "decisions": ["…"], "points_ouverts": ["…"], "prochaines_actions": ["…"],
   "fichiers_cles": [], "tags": ["…"], "liens_projets": ["autre-id"],
   "liens": {"projet_claude": "https://claude.ai/project/…", "depot": "", "site": ""},
   "derniere_maj": "2026-01-31"}]}
type : « projet Claude », « site », « bot » ou « outil ». Un bot de veille d'offres = une fiche de type « bot » avec liens.depot = l'adresse GitHub de son dépôt.
Fiches « outil » standard à ajouter (type « outil », statut « actif », champ « vue » égal à l'id) : marche (Marché), bibliotheque (Bibliothèque), cours (Cours), reseau (Carnet réseau), calendrier (Calendrier), chacune avec un objectif d'une phrase.

data/courses.json
{"version": 1, "cours": [
  {"id": "nom-du-cours", "nom": "Nom du cours", "programme": "…", "professeur": "", "sessions": 6,
   "statut": "en cours", "evaluation": "…", "examen": {"date": "", "format": ""},
   "resume": "", "chapitres": [], "notes": [], "documents": [], "liens": {"projet_claude": ""}, "tags": []}]}
statut : « à venir », « en cours » ou « terminé ».

data/networking.json
{"version": 1, "contacts": [
  {"id": "prenom-nom", "nom": "Prénom Nom", "entreprise": "…", "poste": "…", "ville": "…",
   "statut": "À contacter", "canal": "LinkedIn", "notes": "", "prochaine_relance": ""}],
 "modeles": [{"id": "m1", "titre": "Prise de contact", "texte": "Bonjour {prenom}, … {entreprise} … {poste} …"}]}
statut : « À contacter », « Envoyé », « Relance faite », « Répondu », « Call fait », « Remercié », « En attente », « À confirmer » ou « Clos ».

data/calendrier.json
{"version": 1,
 "categories": [{"nom": "Cours", "couleur": "#2B5FA8", "icone": "auto"}],
 "evenements": [{"id": "e1", "titre": "…", "date": "2026-01-31", "debut": "09:00", "fin": "12:00",
   "categorie": "Cours", "icone": "auto", "rappel": "30 minutes avant", "repetition": "Chaque semaine", "lieu": "", "notes": ""}]}
rappel : « Aucun », « À l'heure », « 10 minutes avant », « 30 minutes avant », « 1 heure avant », « 2 heures avant », « La veille », « 2 jours avant » ou « 1 semaine avant ». repetition : « Aucune », « Chaque semaine », « Chaque mois » ou « Chaque année ».

Commence par l'étape 1.
```
<!-- FIN DU PROMPT -->

## Ce que voit quelqu'un d'autre

- Sans dépôt privé, l'application est en **mode démonstration** : données fictives, aucun nom.
- Une fois relié à **son** dépôt, chacun ne voit que **ses** données. Le jeton reste sur son appareil
  (chiffré par son code) ; il ne passe jamais par l'application publique ni par son auteur.
- Pour couper l'accès d'un appareil perdu : supprimer le jeton sur GitHub.

## Bon à savoir

- Utiliser l'adresse de quelqu'un d'autre revient à lui faire confiance pour le code de
  l'application. Si tu préfères ne dépendre de personne, fais ta propre copie (étape 2 b).
- Onglet Offres : il lit un « bot de veille » (dépôt GitHub qui écrit `data/jobs.json`). Sans bot,
  masque l'onglet dans Réglages › Vues.
- Import d'emploi du temps : seul le format de la page « My Calendar » de SKEMA est reconnu pour
  l'instant (à choisir dans le profil).

# 🌟 NutriStep

Application web de suivi de bien-être personnel avec authentification, suivi du poids, des repas et des activités.

## 🚀 Déploiement sur Render.com (GRATUIT)

### Étape 1 : Préparer le projet

Tous les fichiers sont déjà prêts ! Voici la structure :

```
wellness-tracker/
├── app.py                 # Application Flask principale
├── requirements.txt       # Dépendances Python
├── templates/             # Templates HTML
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── weight.html
│   ├── meals.html
│   └── activities.html
└── README.md             # Ce fichier
```

### Étape 2 : Créer un compte GitHub (si pas déjà fait)

1. Va sur https://github.com
2. Crée un compte gratuit
3. Confirme ton email

### Étape 3 : Créer un dépôt GitHub

1. Une fois connecté sur GitHub, clique sur le "+" en haut à droite
2. Clique sur "New repository"
3. Nomme-le "nutristep"
4. Laisse-le en "Public"
5. Ne coche RIEN d'autre
6. Clique sur "Create repository"

### Étape 4 : Uploader les fichiers sur GitHub

**Méthode simple (sans ligne de commande) :**

1. Sur la page de ton nouveau dépôt, clique sur "uploading an existing file"
2. Glisse-déposse TOUS les fichiers du projet (app.py, requirements.txt, et le dossier templates/)
3. En bas, clique sur "Commit changes"

### Étape 5 : Déployer sur Render.com

1. Va sur https://render.com et connecte-toi (avec ton compte GitHub si possible)
2. Clique sur "New +" en haut à droite
3. Choisis "Web Service"
4. Connecte ton compte GitHub si demandé
5. Sélectionne le dépôt "nutristep"
6. Remplis les champs :
   - **Name** : nutristep (ou ce que tu veux)
   - **Region** : Frankfurt (le plus proche de la France)
   - **Branch** : main
   - **Runtime** : Python 3
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `gunicorn app:app`
   - **Instance Type** : Free

7. Clique sur "Advanced" et ajoute ces variables d'environnement :
   - Clique sur "Add Environment Variable"
   - **Key** : `SECRET_KEY`
   - **Value** : `ta-cle-secrete-super-longue-et-aleatoire-123456789`
   
8. Clique sur "Create Web Service"

### Étape 6 : Créer la base de données PostgreSQL

1. Toujours sur Render.com, clique sur "New +" → "PostgreSQL"
2. Remplis :
   - **Name** : nutristep-db
   - **Database** : nutristep
   - **User** : nutristep_user
   - **Region** : Frankfurt (même région que le web service)
   - **Instance Type** : Free
3. Clique sur "Create Database"

### Étape 7 : Connecter la base de données à l'application

1. Une fois la base créée, va dans l'onglet "Info"
2. Copie l'**Internal Database URL** (commence par `postgres://`)
3. Retourne sur ton Web Service
4. Va dans "Environment"
5. Ajoute une nouvelle variable :
   - **Key** : `DATABASE_URL`
   - **Value** : Colle l'URL que tu as copiée
6. Clique sur "Save Changes"

L'application va redémarrer automatiquement !

### Étape 8 : Accéder à ton application

1. En haut de la page de ton Web Service, tu verras une URL comme : `https://nutristep-xxxx.onrender.com`
2. Clique dessus ou copie-la dans ton navigateur
3. **PREMIER COMPTE** : Clique sur "S'inscrire" et crée ton compte
4. Tu peux maintenant utiliser l'application !

---

## 📱 Utilisation de l'application

### Fonctionnalités disponibles :

✅ **Dashboard** : Vue d'ensemble avec graphique d'évolution du poids  
✅ **Suivi du poids** : Enregistre tes pesées quotidiennes  
✅ **Suivi des repas** : Note tes repas et calories  
✅ **Suivi des activités** : Enregistre tes exercices et calories brûlées  

---

## 🔐 Passage au login Google (PLUS TARD)

Pour ajouter le login Google après, il faudra :

1. **Créer un projet Google Cloud Console**
   - Aller sur https://console.cloud.google.com
   - Créer un nouveau projet
   - Activer Google+ API
   - Créer des identifiants OAuth 2.0

2. **Modifier le code**
   - Je te fournirai les lignes exactes à modifier dans `app.py`
   - Ajouter `google-auth` dans `requirements.txt`
   - Créer un bouton "Se connecter avec Google"

3. **Mettre à jour sur Render**
   - Push les changements sur GitHub
   - Render mettra à jour automatiquement

📝 **Note** : Je te ferai un guide détaillé quand tu seras prêt !

---

## ⚙️ Variables d'environnement importantes

- `SECRET_KEY` : Clé secrète pour les sessions (OBLIGATOIRE en production)
- `DATABASE_URL` : URL de connexion PostgreSQL (fournie par Render)

---

## 🆘 Dépannage

**L'application ne démarre pas ?**
- Vérifie que la `DATABASE_URL` est bien configurée
- Regarde les logs dans Render (onglet "Logs")

**Je ne peux pas me connecter ?**
- Assure-toi d'avoir créé un compte via "S'inscrire"
- Le premier utilisateur doit s'inscrire manuellement

**La base de données est vide ?**
- C'est normal ! Elle se crée automatiquement au premier lancement
- Crée ton compte et commence à ajouter des données

---

## 🎉 C'est tout !

Ton application est maintenant en ligne et accessible 24h/24 gratuitement !

L'URL de ton application : Tu la trouveras en haut de la page Render de ton Web Service.

**Profite bien de ton tracker de bien-être ! 💪**

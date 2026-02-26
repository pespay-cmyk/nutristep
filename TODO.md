# 📋 TODO - NutriStep

*Dernière mise à jour : 26/02/2026*

---

## 🔧 **EN COURS - BUGS À CORRIGER**

### 🍔 Menu Hamburger Mobile
- [ ] **BUG** : Menu hamburger - Les liens du menu sont en bas de l'écran au lieu d'être collés sous le logo
  - Problème : Grand espace vide entre logo NutriStep et premier menu (Dashboard)
  - À investiguer : conflits CSS entre base.html et responsive.css

---

## 🚀 **PRIORITÉ 1 - À FAIRE MAINTENANT**

### 🍽️ Fonctionnalités Repas
- [ ] 📋 **Repas types prédéfinis**
  - Créer des templates de repas récurrents
  - Ex: "Petit-déj standard" = Jus d'orange + Café + 2 tranches pain complet + Confiture
  - Bouton "Utiliser un repas type" dans modal
  - Gestion des templates dans paramètres profil
  - Pouvoir créer/modifier/supprimer ses templates

### 📸 Photos avant/après
- [ ] 📸 **Système de photos mensuelles**
  - Demande automatique 1x par mois
  - 5 angles : Visage / Ventre face / Ventre profil / Cuisses / Dos
  - Stockage filesystem (migration BDD plus tard)
  - Galerie de progression avec comparaison avant/après
  - Compression automatique
  - TODO : Floutage visage (idées plus tard)
  - TODO : Partage social (idées plus tard)

### 📏 Mesures Corporelles
- [x] ✅ **Page Mesures complète créée !**
  - 3 mesures essentielles : Taille / Hanches / Cuisse
  - 3 mesures secondaires activables : Bras / Poitrine / Mollet
  - Schéma anatomique SVG avec points de mesure numérotés
  - Calcul automatique ratio taille/hanches
  - Graphique d'évolution multi-lignes
  - Activation dans paramètres profil
  - Navbar conditionnelle (entre Poids et Repas)

### 💾 Sauvegarde & Maintenance
- [ ] 💾 **Sauvegarde automatique BDD**
  - Script cron quotidien (3h du matin)
  - Export SQLite → Google Drive via API
  - Conserver 30 dernières sauvegardes (rotation auto)
  - Notification email en cas d'échec
  
- [ ] ⚠️ **Gestion expiration PythonAnywhere**
  - **LIMITATION** : Pas d'API pour détecter l'expiration automatiquement
  - **LIMITATION** : Impossible de prolonger automatiquement (anti-abus volontaire)
  - **SOLUTION MANUELLE** :
    - ⏰ Créer alerte calendrier récurrente tous les 25 jours
    - 📝 Cliquer manuellement sur "Run until 1 month from today" dans PythonAnywhere
    - ⚠️ NE PAS OUBLIER sous peine de perdre l'accès à l'app !

---

## 📈 **PRIORITÉ 2 - BIENTÔT**

### 📲 Import Garmin Connect
- [x] ✅ Import CSV activités (fonctionne !)
- [x] ✅ Validation manuelle ligne par ligne
- [x] ✅ Mapping types activités FR/EN
- [x] ✅ Bouton "Importer depuis Garmin" déplacé dans page Activités
- [ ] 🔮 **À RÉFLÉCHIR** : Solution pour import automatique des pas quotidiens
- [ ] 🔮 **À RÉFLÉCHIR** : Auto-hébergement derrière box avec mini PC (pour connexions externes)

### 📧 Rappels & Encouragements
- [ ] ✅ Rappel si pas pesé depuis 7 jours
- [ ] ✅ Messages d'encouragement automatiques (baisse de poids, objectifs atteints, etc.)

### 🏆 Badges & Achievements
- [ ] ✅ Système de badges (si pas trop complexe à implémenter)
- [ ] ✅ Exemples de badges :
  - "7 jours consécutifs de pesée"
  - "Premier -5kg"
  - "1 mois sans exception"
  - "10 000 pas pendant 7 jours"

### 🎯 Challenges 30 jours
- [ ] ✅ Mode challenge optionnel
- [ ] ✅ Suivi quotidien pendant le challenge
- [ ] ✅ Rapport de fin avec statistiques

---

## 🔮 **PRIORITÉ 3 - PLUS TARD**

### 👥 Fonctionnalités Sociales
- [ ] ✅ Système d'amis
- [ ] ✅ Partage sélectif (choisir quoi partager : activités, repas, poids, etc.)
- [ ] ✅ **Partage d'activités** :
  - Ami A partage activité → apparaît chez Ami B comme "non validée"
  - Mention "avec [Nom ami]"
  - Ami B peut valider/modifier/ajuster
- [ ] ✅ **Partage de repas** :
  - Même principe avec validation/ajustement
  - Mention "avec [Nom ami]"

### 👨‍⚕️ Compte Nutritionniste
- [ ] ✅ Type de compte "Pro"
- [ ] ✅ Liste de patients
- [ ] ✅ Demande d'accès (patient doit accepter)
- [ ] ✅ Vue consultation : dashboard + récap du patient
- [ ] ✅ Notes privées du nutritionniste
- [ ] ✅ Historique des consultations
- [ ] ✅ Export PDF personnalisé (sécu/mutuelles)

---

## 💡 **IDÉES EN RÉFLEXION**

- Planning repas (à voir)
- Notes & journal quotidien
- Objectifs de poids avec jalons
- Mode suivi strict
- Floutage visage sur photos
- Partage social des photos/progression

---

## ✅ **TERMINÉ**

### Phase 0 - Infrastructure
- [x] Synchronisation Git (GitHub ↔ PythonAnywhere)
- [x] Login Google OAuth uniquement
- [x] PWA (Progressive Web App) avec service worker

### Phase 1 - Design
- [x] Design moderne avec 3 thèmes (Healthy Green, Ocean Blue, Sunset Pink)
- [x] Sauvegarde thème en BDD
- [x] **Logo NutriStep** : N avec flèche descendante + balance
  - Icône app (favicon + icône mobile)
  - Logo navbar
  - Identité visuelle cohérente
- [x] Icônes SVG modernes (remplacement emojis)
- [x] Favicon pour raccourci mobile

### Phase 2 - Poids
- [x] Page Poids améliorée
  - Messages d'encouragement
  - Blocage si déjà saisi aujourd'hui
  - Alerte si pas saisi depuis X jours
  - Graphique avec périodes personnalisables (1/2/3/8 mois)

### Phase 3 - Repas
- [x] Système repas complet
  - 5 types de repas (Petit-déj, Encas matin, Déjeuner, Goûter, Dîner)
  - Vue calendrier mensuelle
  - Option "rien mangé"
  - Qualification (Normal/Exception/Compensation)
  - Badges colorés dans calendrier
  - Autocomplétion personnalisée
  - Modal de saisie dynamique
  - **Accordéon** : Repas repliés par défaut, déplient au clic
  - **Qualification** : Icônes SVG colorées (✓ bleu normal, ⚠️ orange exception, 🥗 vert compensation)
  - **Bordures** : Entoure l'icône sélectionnée dynamiquement

### Phase 4 - Récap
- [x] Vue récap mensuelle (repas + activités fusionnés)
- [x] Colonnes dynamiques (encas/goûter apparaissent seulement si utilisés)
- [x] Statistiques : Exceptions + Compensations
- [x] ❌ Retrait : "Jours avec repas", "Repas complets", scrollbar survol

### Phase 5 - Activités
- [x] Page Activités sportives
- [x] Types : Marche, Course, Vélo, Natation, Musculation, Yoga, Ski, **Pas quotidiens**, Autre
- [x] Champs : Durée, Calories, Pas (selon type)
- [x] Statistiques : Total activités, semaine, pas cumulés, calories brûlées
- [x] Import CSV Garmin Connect avec validation

### Phase 6 - Dashboard
- [x] Vue résumée : Poids actuel + IMC
- [x] Évolution poids (graphique 30 jours)
- [x] Repas du jour avec emojis/icônes + qualification
- [x] **Activités du mois** (même période que graphique poids)
- [x] **Graphique nombre de pas** sur 1 mois avec :
  - Ligne de pas moyen
  - Icônes activités sur chaque jour
  - Tooltip au survol (type + détails)
- [x] ❌ Retrait : Calories brûlées, Calories consommées, Activités du jour

### Phase 7 - Profil
- [x] Informations personnelles (nom, prénom, date naissance, taille, sexe, poids cible)
- [x] Activation modules : Repas, Activités, Mesures, Import Garmin
- [x] **Statistiques IMC** avec jauge visuelle dégradée
- [x] **Statistiques perte** :
  - Perte totale
  - Perte moyenne par semaine
  - Perte moyenne par mois
  - Temps estimé pour objectif
- [x] Choix du thème
- [x] Personnalisation couleurs navbar

### Phase 8 - Responsive Mobile
- [x] **Menu Hamburger** : Bouton ☰ en haut à gauche, menu slide
- [x] **H1 décalé à droite** pour ne pas être masqué par burger
- [x] **Tableaux compacts** : Date verticale, colonnes réduites
- [x] **Pastilles uniformes** : Gap 12px partout
- [x] **Boutons icônes seuls** : "+" et "🗑️" sans texte sur mobile
- [x] **Activities** : Colonne Note masquée sur mobile
- [x] **Weight** : Badge "AUJOURD'HUI" masqué, table compacte
- [x] **Measurements** : Headers numérotés ①②③④⑤⑥, date verticale
- [x] **Meals Recap** : Headers icônes 🌅🍽️🌙🏃, pastilles centrées
- [x] **Meals** : Accordéon, qualification 4 icônes inline

### Phase 9 - Mesures Corporelles
- [x] **Page complète** avec schéma anatomique
- [x] **3 mesures essentielles** : Taille, Hanches, Cuisse (toujours visibles)
- [x] **3 mesures secondaires** : Bras, Poitrine, Mollet (activables)
- [x] **Calcul ratio taille/hanches** avec indicateur santé
- [x] **Graphique évolution** multi-lignes
- [x] **Responsive mobile** : Headers numérotés, table compacte
- [x] **Intégration dashboard** : Graphique mesures (si activé)

---

## 📊 **RÉSUMÉ PAGES**

✅ **Dashboard** - Vue d'ensemble (poids, IMC, repas du jour, activités du mois, graph pas)  
✅ **Poids** - Saisie + historique + graphique multi-périodes  
✅ **Mesures** - Mensurations corporelles + graphique évolution  
✅ **Repas** - Calendrier mensuel + saisie par modal accordéon  
✅ **Récap** - Tableau fusion repas + activités  
✅ **Activités** - Saisie sport + pas + import Garmin CSV  
✅ **Profil** - Infos perso + stats IMC/perte + activation modules + thème  

---

**Prochaine étape :** Corriger bug menu hamburger + Repas types prédéfinis 🚀

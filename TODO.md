# 📋 TODO - NutriStep

*Dernière mise à jour : 16/02/2026*

---

## 🚀 **À FAIRE MAINTENANT**

### 🏠 Dashboard
- [x] ❌ Retirer pastille "Calories brûlées"
- [x] ❌ Retirer pastille "Calories consommées"
- [x] ❌ Retirer section "Activités du jour"
- [x] ✅ Améliorer affichage "Repas du jour" (style propre comme page meals avec emojis)
- [x] ✅ Ajouter section "Activités du mois" (même période que graphique poids)
- [x] ✅ Ajouter graphique "Nombre de pas" sur 1 mois
  - Ligne de pas moyen
  - Petites icônes pour chaque activité (🏃🚴💪 etc.)
  - Au survol de l'icône → tooltip avec type + détails
- [ ] 🎨 **FIGNOLAGE** : Améliorer affichage icônes activités sur graph (si besoin)

### 📊 Page Récap
- [x] ❌ Retirer scrollbar bizarre qui apparaît au survol
- [x] ❌ Retirer stat "Jours avec repas"
- [x] ❌ Retirer stat "Repas complets"
- [x] ✅ Garder uniquement : Exceptions + Équilibrages
- [ ] 🎨 **FIGNOLAGE** : Aligner pastilles du haut avec le tableau

### 🎨 Design Général
- [x] ✅ Remplacer emojis par icônes SVG modernes
- [x] ✅ Favicon pour raccourci mobile

---

## 📸 **TRÈS BIENTÔT** (juste après "maintenant")

### Photos avant/après
- [ ] ✅ Demande de photos 1x par mois (automatique)
  - Visage
  - Ventre
  - Cuisses
- [ ] ✅ Sauvegarde en BDD
- [ ] ✅ Galerie de progression (comparaison avant/après)

### 📲 Import Garmin Connect
- [x] ✅ Import CSV activités (fonctionne !)
- [x] ✅ Validation manuelle ligne par ligne
- [x] ✅ Mapping types activités FR/EN
- [ ] 🔮 **À RÉFLÉCHIR** : Solution pour import automatique des pas quotidiens
- [ ] 🔮 **À RÉFLÉCHIR** : Auto-hébergement derrière box avec mini PC (pour connexions externes)

---

## 📈 **PRIORITÉ 2**

### 👤 Profil Utilisateur
- [x] ✅ Ajouter dans le profil :
  - Date de naissance
  - Taille
  - Sexe
  - Poids cible

### 📊 Statistiques Avancées
- [x] ✅ **IMC** (calcul automatique avec jauge visuelle dégradée)
- [x] ✅ **Perte moyenne** :
  - Par semaine
  - Par mois
- [x] ✅ **Perte totale** depuis le début
- [x] ✅ **Temps estimé** pour atteindre l'objectif
- [ ] ❌ Corrélation pas/poids (graphique - à faire plus tard)
- [ ] ❌ Tendance générale (courbe lissée - à faire plus tard)

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

## 🔮 **PLUS TARD**

### 🎨 Design & UX
- [ ] 🎨 **Logo NutriStep** : Créer un vrai logo moderne (actuellement juste texte)
- [ ] 🎨 **Fignolage graph activités** : Améliorer affichage icônes sur le graphique des pas
- [ ] 🎨 **Fignolage récap** : Aligner pastilles stats avec le tableau

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

---

## ✅ **TERMINÉ**

### Phase 0
- [x] Synchronisation Git (GitHub ↔ PythonAnywhere)

### Phase 1
- [x] Design moderne avec 3 thèmes (Healthy Green, Ocean Blue, Sunset Pink)
- [x] Sauvegarde thème en BDD

### Phase 2
- [x] Page Poids améliorée
  - Messages d'encouragement
  - Blocage si déjà saisi aujourd'hui
  - Alerte si pas saisi depuis X jours
  - Graphique avec périodes personnalisables (1/2/3/8 mois)

### Phase 3
- [x] Système repas complet
  - 5 types de repas
  - Vue calendrier mensuelle
  - Option "rien"
  - Qualification (Normal/Exception/Équilibrage)
  - Badges dans calendrier
  - Autocomplétion personnalisée
  - Modal de saisie dynamique

### Phase 4
- [x] Login Google uniquement

### Phase B1
- [x] Vue mensuelle des repas
- [x] Masquage repas "rien" dans calendrier

### Phase B2
- [x] Récap général (repas + activités fusionnés)
- [x] Colonnes dynamiques (encas/goûter)

### Activités
- [x] Type "Pas quotidiens"
- [x] Statistiques améliorées
- [x] Responsive mobile

---

**Prochaine étape :** Dashboard amélioré 🚀

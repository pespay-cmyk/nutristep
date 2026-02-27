# 📋 TODO - NutriStep

*Dernière mise à jour : 27/02/2026*

---

## 🔧 EN COURS - BUGS À CORRIGER

- [ ] **Qualification jour vs repas** — la qualification Normal/Exception/Compensation est actuellement au niveau de chaque repas individuel, alors qu'elle devrait être au niveau de la **journée entière**. À revoir en profondeur (modèle BDD + UI).

---

## 🚀 PRIORITÉ 1 - À FAIRE MAINTENANT

### 🍽️ Repas types prédéfinis
- [ ] Créer des templates de repas récurrents (ex: "Petit-déj standard")
- [ ] Bouton "Utiliser un repas type" dans le modal de saisie
- [ ] Gestion des templates dans les paramètres profil (créer / modifier / supprimer)

### 💾 Sauvegarde automatique
- [ ] Script cron quotidien (3h du matin)
- [ ] Zip BDD SQLite + dossier photos utilisateurs → Google Drive via API
- [ ] Conserver 30 dernières sauvegardes (rotation auto)
- [ ] Notification email en cas d'échec

### ⚠️ Expiration PythonAnywhere (plan gratuit)
> Rappel manuel obligatoire tous les 25 jours : cliquer "Run until 1 month from today"
> Pas d'API disponible pour automatiser — risque de coupure si oublié !
- [ ] Créer alerte calendrier récurrente tous les 25 jours

---

## 📈 PRIORITÉ 2 - BIENTÔT

### 📲 Import Garmin
- [ ] Solution pour import automatique des pas quotidiens
- [ ] Réflexion : auto-hébergement sur mini PC derrière box perso

### 📧 Rappels & Encouragements
- [ ] Rappel si pas pesé depuis 7 jours
- [ ] Messages d'encouragement automatiques (objectifs atteints, baisse de poids…)

### 🏆 Badges & Achievements
- [ ] "7 jours consécutifs de pesée"
- [ ] "Premier -5kg"
- [ ] "1 mois sans exception"
- [ ] "10 000 pas pendant 7 jours"

### 🎯 Challenge 30 jours
- [ ] Mode challenge optionnel avec suivi quotidien + rapport de fin

---

## 🔮 PRIORITÉ 3 - PLUS TARD

### 👥 Fonctionnalités sociales
- [ ] Système d'amis + partage sélectif (activités, repas, poids)
- [ ] Partage d'activités/repas avec validation par l'ami

### 👨‍⚕️ Compte Nutritionniste
- [ ] Type de compte "Pro" avec liste de patients
- [ ] Vue consultation + notes privées + export PDF

---

## 💡 IDÉES EN RÉFLEXION

- Planning repas
- Notes & journal quotidien
- Objectifs de poids avec jalons intermédiaires
- Mode suivi strict
- Floutage visage sur photos de progression
- Partage social des photos/progression
- Gestion de la traduction (i18n)

---

## ✅ TERMINÉ

### Phase 0 - Infrastructure
- [x] Synchronisation Git (GitHub ↔ PythonAnywhere)
- [x] Login Google OAuth uniquement
- [x] PWA avec service worker

### Phase 1 - Design
- [x] 3 thèmes (Healthy Green, Ocean Blue, Sunset Pink), sauvegarde BDD
- [x] Logo NutriStep + icônes SVG modernes + favicon

### Phase 2 - Poids
- [x] Messages d'encouragement, blocage doublon, alerte inactivité
- [x] Graphique multi-périodes (1/2/3/8 mois)

### Phase 3 - Repas
- [x] 5 types de repas, calendrier mensuel, option "rien mangé"
- [x] Qualification Normal/Exception/Compensation, accordéon, autocomplétion

### Phase 4 - Récap
- [x] Vue mensuelle repas + activités fusionnés, colonnes dynamiques

### Phase 5 - Activités
- [x] Page activités, types multiples, import CSV Garmin avec validation

### Phase 6 - Dashboard initial
- [x] Poids + IMC + graphique 30j + repas du jour + graph pas

### Phase 7 - Profil
- [x] Infos perso, activation modules, stats IMC/perte, choix thème

### Phase 8 - Responsive Mobile
- [x] Menu hamburger, tableaux compacts, boutons icônes seuls sur mobile

### Phase 9 - Mesures Corporelles
- [x] 3 mesures essentielles + 3 secondaires activables
- [x] Ratio taille/hanches, graphique évolution, responsive

### Phase 10 - Refonte Dashboard
- [x] Stats IMC/perte/tendances déplacées depuis profil vers dashboard
- [x] Graphique pas déplacé dans page Activités
- [x] Bouton "Ajouter poids du jour" conditionnel
- [x] Bug menu hamburger corrigé

### Phase 11 - Photos de progression
- [x] 3 angles : Visage / Ventre (profil) / Silhouette
- [x] Guides illustrés, upload caméra direct mobile, compression Pillow
- [x] Stockage sécurisé, remplacement auto, pastille "✓ Prise"
- [x] Galerie chronologique, comparaison avant/après, lightbox
- [x] Rappel mensuel dashboard, option profil

---

## 📊 RÉSUMÉ PAGES

✅ **Dashboard** — Poids + IMC + stats évolution + tendances + repas du jour + mesures
✅ **Poids** — Saisie + historique + graphique multi-périodes
✅ **Mesures** — Mensurations corporelles + graphique évolution
✅ **Repas** — Calendrier mensuel + saisie modal accordéon
✅ **Récap** — Tableau fusion repas + activités
✅ **Activités** — Saisie sport + pas + graphique + import Garmin CSV
✅ **Photos** — Progression mensuelle + comparaison avant/après + galerie
✅ **Profil** — Infos perso + activation modules + thème

---

**Prochaine étape :** Repas types prédéfinis 🚀

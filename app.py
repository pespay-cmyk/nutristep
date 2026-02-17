from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from authlib.integrations.flask_client import OAuth
from datetime import datetime, timedelta
import os
from functools import wraps
from dotenv import load_dotenv
import json

# Charger les variables d'environnement depuis .env
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///wellness.db')

# Fix pour Render.com qui utilise postgres:// au lieu de postgresql://
if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres://'):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

print("CLIENT_ID =", repr(os.environ.get("GOOGLE_CLIENT_ID")))
print("SECRET    =", repr(os.environ.get("GOOGLE_CLIENT_SECRET")))

# Configuration OAuth avec authlib
oauth = OAuth(app)

# IMPORTANT: Remplace ces valeurs par tes vraies clés Google
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')

google = oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

db = SQLAlchemy(app)

# ========================================
# MODÈLES DE BASE DE DONNÉES
# ========================================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)  # Nullable pour les comptes Google
    google_id = db.Column(db.String(255), unique=True, nullable=True)  # ID Google
    theme = db.Column(db.String(20), default='green')  # Thème préféré de l'utilisateur
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relations
    weight_entries = db.relationship('WeightEntry', backref='user', lazy=True, cascade='all, delete-orphan')
    meal_entries = db.relationship('MealEntry', backref='user', lazy=True, cascade='all, delete-orphan')
    activity_entries = db.relationship('ActivityEntry', backref='user', lazy=True, cascade='all, delete-orphan')

class WeightEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class MealEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Nouveau: 5 types de repas
    meal_type = db.Column(db.String(20), nullable=False)
    # Valeurs: breakfast, snack_morning, lunch, snack_afternoon, dinner

    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)

    # Nouveau: aliments (liste JSON)
    foods = db.Column(db.Text)  # Stocké comme JSON ["yaourt", "pomme", ...]

    # Nouveau: qualification
    qualification = db.Column(db.String(20), default='normal')  # normal, exception, equilibrage

    # Nouveau: si "rien" pour ce repas
    is_none = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_foods_list(self):
        """Retourne la liste des aliments"""
        import json
        if self.foods:
            return json.loads(self.foods)
        return []

    def set_foods_list(self, foods_list):
        """Définit la liste des aliments"""
        import json
        self.foods = json.dumps(foods_list)

class ActivityEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity_type = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # en minutes
    steps = db.Column(db.Integer, nullable=True)  # Nombre de pas (pour type "Pas")
    calories_burned = db.Column(db.Integer)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ========================================
# DÉCORATEUR POUR PROTÉGER LES ROUTES
# ========================================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Veuillez vous connecter pour accéder à cette page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ========================================
# ROUTES D'AUTHENTIFICATION GOOGLE
# ========================================

@app.route('/login/google')
def google_login():
    redirect_uri = url_for('google_authorized', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/login/google/authorized')
def google_authorized():
    try:
        token = google.authorize_access_token()
        user_info = token.get('userinfo')

        if not user_info:
            flash('Impossible de récupérer les informations depuis Google.', 'danger')
            return redirect(url_for('login'))

        google_id = user_info['sub']
        email = user_info['email']
        name = user_info.get('name', email.split('@')[0])

        # Chercher si l'utilisateur existe déjà
        user = User.query.filter_by(google_id=google_id).first()

        if not user:
            # Chercher par email (au cas où l'utilisateur a créé un compte classique avant)
            user = User.query.filter_by(email=email).first()
            if user:
                # Lier le compte existant à Google
                user.google_id = google_id
            else:
                # Créer un nouveau compte
                # Générer un username unique
                base_username = name.lower().replace(' ', '')
                username = base_username
                counter = 1
                while User.query.filter_by(username=username).first():
                    username = f"{base_username}{counter}"
                    counter += 1

                user = User(
                    username=username,
                    email=email,
                    google_id=google_id,
                    password_hash=None  # Pas de mot de passe pour les comptes Google
                )
                db.session.add(user)

            db.session.commit()

        # Connecter l'utilisateur
        session['user_id'] = user.id
        session['username'] = user.username
        flash(f'Bienvenue {user.username} !', 'success')
        return redirect(url_for('dashboard'))

    except Exception as e:
        flash(f'Erreur lors de la connexion avec Google: {str(e)}', 'danger')
        return redirect(url_for('login'))

# ========================================
# ROUTES D'AUTHENTIFICATION CLASSIQUES
# ========================================

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login')
def login():
    # Si déjà connecté, rediriger vers le dashboard
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    # Afficher la page de login Google uniquement
    return render_template('login.html', theme='green')



"""
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')

        if password != password_confirm:
            flash('Les mots de passe ne correspondent pas.', 'danger')
            return render_template('register.html', theme='green')

        if User.query.filter_by(username=username).first():
            flash('Ce nom d\'utilisateur existe déjà.', 'danger')
            return render_template('register.html', theme='green')

        if User.query.filter_by(email=email).first():
            flash('Cet email est déjà utilisé.', 'danger')
            return render_template('register.html', theme='green')

        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Compte créé avec succès ! Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', theme='green')
"""
@app.route('/logout')
def logout():
    session.clear()
    flash('Vous êtes déconnecté.', 'info')
    return redirect(url_for('login'))

@app.route('/api/change-theme', methods=['POST'])
@login_required
def change_theme():
    data = request.get_json()
    theme = data.get('theme', 'green')

    # Valider le thème
    if theme not in ['green', 'ocean', 'sunset']:
        return jsonify({'error': 'Invalid theme'}), 400

    # Mettre à jour le thème de l'utilisateur
    user = User.query.get(session['user_id'])
    user.theme = theme
    db.session.commit()

    return jsonify({'success': True})

# ========================================
# ROUTES PRINCIPALES
# ========================================

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    user = User.query.get(user_id)

    today = datetime.utcnow().date()
    thirty_days_ago = today - timedelta(days=30)

    # Poids actuel
    latest_weight = WeightEntry.query.filter_by(user_id=user_id).order_by(WeightEntry.date.desc()).first()

    # Repas d'aujourd'hui
    today_meals = MealEntry.query.filter_by(user_id=user_id, date=today).all()

    # Activités du mois (30 derniers jours)
    month_activities = ActivityEntry.query.filter(
        ActivityEntry.user_id == user_id,
        ActivityEntry.date >= thirty_days_ago
    ).order_by(ActivityEntry.date.desc()).all()

    # Historique poids (30 derniers jours)
    weight_history = WeightEntry.query.filter(
        WeightEntry.user_id == user_id,
        WeightEntry.date >= thirty_days_ago
    ).order_by(WeightEntry.date).all()

    # ========================================
    # DONNÉES POUR LE GRAPHIQUE DES PAS
    # ========================================

    # Récupérer toutes les activités "Pas" des 30 derniers jours
    steps_activities = ActivityEntry.query.filter(
        ActivityEntry.user_id == user_id,
        ActivityEntry.activity_type == 'Pas',
        ActivityEntry.date >= thirty_days_ago
    ).order_by(ActivityEntry.date).all()

    # Créer un dictionnaire date -> steps
    steps_by_date = {}
    for activity in steps_activities:
        steps_by_date[activity.date] = activity.steps or 0

    # Générer toutes les dates des 30 derniers jours
    steps_dates = []
    steps_values = []
    current_date = thirty_days_ago

    while current_date <= today:
        steps_dates.append(current_date.strftime('%d/%m'))
        steps_values.append(steps_by_date.get(current_date, 0))
        current_date += timedelta(days=1)

    steps_data = {
        'dates': steps_dates,
        'steps': steps_values
    }

    # Calculer la moyenne des pas (jours avec au moins 1 pas)
    total_steps = sum(steps_values)
    days_with_steps = sum(1 for s in steps_values if s > 0)
    average_steps = total_steps / days_with_steps if days_with_steps > 0 else 0

    steps_stats = {
        'total': total_steps,
        'average': average_steps
    }

    # ========================================
    # ACTIVITÉS PAR DATE (pour le tooltip du graph)
    # ========================================

    # Récupérer toutes les activités (sauf "Pas") des 30 derniers jours
    other_activities = ActivityEntry.query.filter(
        ActivityEntry.user_id == user_id,
        ActivityEntry.activity_type != 'Pas',
        ActivityEntry.date >= thirty_days_ago
    ).order_by(ActivityEntry.date).all()

    # Organiser par date
    activities_by_date = {}
    for activity in other_activities:
        date_key = activity.date.strftime('%d/%m')
        if date_key not in activities_by_date:
            activities_by_date[date_key] = []
        activities_by_date[date_key].append({
            'type': activity.activity_type,
            'duration': activity.duration,
            'calories': activity.calories_burned
        })

    return render_template('dashboard.html',
                         latest_weight=latest_weight,
                         today_meals=today_meals,
                         month_activities=month_activities,
                         weight_history=weight_history,
                         steps_data=steps_data,
                         steps_stats=steps_stats,
                         activities_by_date=activities_by_date,
                         theme=user.theme)

# ========================================
# ROUTES POIDS
# ========================================

@app.route('/weight')
@login_required
def weight():
    user_id = session['user_id']
    user = User.query.get(user_id)
    today = datetime.utcnow().date()

    # Récupérer toutes les entrées
    entries = WeightEntry.query.filter_by(user_id=user_id).order_by(WeightEntry.date.desc()).all()

    # Vérifier si déjà saisi aujourd'hui
    weight_today = WeightEntry.query.filter_by(user_id=user_id, date=today).first()

    # Récupérer le dernier poids pour le pré-remplir
    last_weight = entries[0].weight if entries else None

    # Calculer le nombre de jours depuis la dernière saisie
    days_since_last_entry = None
    if entries and not weight_today:
        last_entry_date = entries[0].date
        days_since_last_entry = (today - last_entry_date).days

    # Message d'encouragement basé sur l'évolution
    weight_evolution_message = None
    weight_evolution_style = None

    if len(entries) >= 2:
        latest_weight = entries[0].weight
        previous_weight = entries[1].weight
        diff = latest_weight - previous_weight

        if diff < -0.2:  # Baisse significative
            weight_evolution_message = f"🎉 Bravo ! Tu as perdu {abs(diff):.1f} kg depuis ta dernière pesée ! Continue comme ça ! 💪"
            weight_evolution_style = "background: linear-gradient(135deg, #dcfce7, #bbf7d0); border-left: 4px solid #10b981; color: #065f46"
        elif diff > 0.2:  # Hausse
            weight_evolution_message = f"💙 Pas de panique ! +{diff:.1f} kg, ça arrive. L'important c'est de continuer, tu vas y arriver ! 🌟"
            weight_evolution_style = "background: linear-gradient(135deg, #dbeafe, #bfdbfe); border-left: 4px solid #3b82f6; color: #1e3a8a"
        elif abs(diff) <= 0.2:  # Stable
            weight_evolution_message = f"✨ Poids stable ! C'est bien, tu maintiens le cap. Continue tes efforts ! 🎯"
            weight_evolution_style = "background: linear-gradient(135deg, #fef3c7, #fde68a); border-left: 4px solid #f59e0b; color: #92400e"

    # Préparer les données pour le graphique (toutes les données)
    all_entries = WeightEntry.query.filter_by(user_id=user_id).order_by(WeightEntry.date).all()
    all_dates = [entry.date.strftime('%d/%m') for entry in all_entries]
    all_weights = [entry.weight for entry in all_entries]

    return render_template('weight.html',
                         entries=entries,
                         weight_today=weight_today,
                         last_weight=last_weight,
                         days_since_last_entry=days_since_last_entry,
                         weight_evolution_message=weight_evolution_message,
                         weight_evolution_style=weight_evolution_style,
                         all_dates=all_dates,
                         all_weights=all_weights,
                         today=today,
                         theme=user.theme)

@app.route('/weight/add', methods=['POST'])
@login_required
def add_weight():
    user_id = session['user_id']
    today = datetime.utcnow().date()

    # Vérifier si déjà saisi aujourd'hui
    existing_entry = WeightEntry.query.filter_by(user_id=user_id, date=today).first()
    if existing_entry:
        flash('Tu as déjà enregistré ton poids aujourd\'hui !', 'warning')
        return redirect(url_for('weight'))

    weight = float(request.form.get('weight'))

    # Validation
    if weight < 30 or weight > 300:
        flash('Le poids doit être entre 30 et 300 kg.', 'danger')
        return redirect(url_for('weight'))

    new_entry = WeightEntry(
        user_id=user_id,
        weight=weight,
        date=today,
        note=None  # Plus de notes
    )
    db.session.add(new_entry)
    db.session.commit()

    flash('Poids enregistré avec succès ! 🎉', 'success')
    return redirect(url_for('weight'))

@app.route('/weight/delete/<int:id>')
@login_required
def delete_weight(id):
    entry = WeightEntry.query.get_or_404(id)
    if entry.user_id != session['user_id']:
        flash('Action non autorisée.', 'danger')
        return redirect(url_for('weight'))

    db.session.delete(entry)
    db.session.commit()
    flash('Entrée supprimée.', 'info')
    return redirect(url_for('weight'))

# ========================================
# ROUTES REPAS
# ========================================

@app.route('/meals')
@login_required
def meals():
    user_id = session['user_id']
    user = User.query.get(user_id)

    # Gérer l'offset de mois (navigation)
    month_offset = int(request.args.get('month_offset', 0))

    # Calculer le mois à afficher
    today = datetime.utcnow().date()

    # Premier jour du mois actuel + offset
    first_day_current_month = today.replace(day=1)

    # Ajouter l'offset de mois
    target_month = first_day_current_month.month + month_offset
    target_year = first_day_current_month.year

    while target_month > 12:
        target_month -= 12
        target_year += 1
    while target_month < 1:
        target_month += 12
        target_year -= 1

    first_day_month = first_day_current_month.replace(year=target_year, month=target_month, day=1)

    # Dernier jour du mois
    if target_month == 12:
        last_day_month = first_day_month.replace(year=target_year + 1, month=1, day=1) - timedelta(days=1)
    else:
        last_day_month = first_day_month.replace(month=target_month + 1, day=1) - timedelta(days=1)

    # Trouver le lundi avant le 1er du mois (pour la grille)
    days_since_monday = first_day_month.weekday()
    grid_start = first_day_month - timedelta(days=days_since_monday)

    # Trouver le dimanche après la fin du mois
    days_until_sunday = 6 - last_day_month.weekday()
    grid_end = last_day_month + timedelta(days=days_until_sunday)

    # Préparer les données pour chaque jour de la grille
    month_days = []
    current_date = grid_start

    while current_date <= grid_end:
        # Récupérer les repas de ce jour
        day_meals = MealEntry.query.filter_by(
            user_id=user_id,
            date=current_date
        ).all()

        # Organiser par type de repas
        meals_by_type = {
            'breakfast': None,
            'snack_morning': None,
            'lunch': None,
            'snack_afternoon': None,
            'dinner': None
        }

        for meal in day_meals:
            meals_by_type[meal.meal_type] = {
                'foods': meal.get_foods_list(),
                'qualification': meal.qualification,
                'is_none': meal.is_none
            }

        # Critère VERT : Les 3 repas principaux (breakfast, lunch, dinner) sont remplis
        main_meals = ['breakfast', 'lunch', 'dinner']
        main_meals_filled = all(meals_by_type[t] is not None for t in main_meals)
        is_complete = main_meals_filled

        # A des repas = au moins un repas rempli
        has_meals = any(meals_by_type[t] is not None for t in meals_by_type)

        # Compter les exceptions et équilibrages
        exception_count = sum(1 for m in day_meals if m.qualification == 'exception')
        equilibrage_count = sum(1 for m in day_meals if m.qualification == 'equilibrage')

        month_days.append({
            'date': current_date,
            'is_today': current_date == today,
            'other_month': current_date.month != target_month,
            'meals': meals_by_type,
            'is_complete': is_complete,
            'has_meals': has_meals,
            'exception_count': exception_count,
            'equilibrage_count': equilibrage_count
        })

        current_date += timedelta(days=1)

    # Récupérer l'historique des aliments pour l'autocomplétion
    all_user_meals = MealEntry.query.filter_by(user_id=user_id).all()
    food_history = set()
    for meal in all_user_meals:
        if meal.foods:
            food_history.update(meal.get_foods_list())

    # Noms des mois en français
    month_names = ['', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                   'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']

    return render_template('meals.html',
                         month_days=month_days,
                         month_name=month_names[target_month],
                         year=target_year,
                         month_offset=month_offset,
                         food_history=list(food_history),
                         theme=user.theme)

@app.route('/meals/recap')
@login_required
def meals_recap():
    user_id = session['user_id']
    user = User.query.get(user_id)

    # Récupérer les dates depuis les paramètres (par défaut: 2 dernières semaines)
    today = datetime.utcnow().date()
    default_start = today - timedelta(days=14)

    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    if start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    else:
        start_date = default_start

    if end_date_str:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    else:
        end_date = today

    # Récupérer tous les repas de la période
    all_meals = MealEntry.query.filter(
        MealEntry.user_id == user_id,
        MealEntry.date >= start_date,
        MealEntry.date <= end_date
    ).all()

    # Organiser par jour
    meals_by_date = {}
    for meal in all_meals:
        if meal.date not in meals_by_date:
            meals_by_date[meal.date] = {}
        meals_by_date[meal.date][meal.meal_type] = {
            'foods': meal.get_foods_list(),
            'qualification': meal.qualification,
            'is_none': meal.is_none
        }

    # Préparer les données jour par jour
    days_data = []
    current_date = start_date
    day_names_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']

    while current_date <= end_date:
        day_meals = meals_by_date.get(current_date, {})

        # Organiser par type
        meals_organized = {
            'breakfast': day_meals.get('breakfast'),
            'snack_morning': day_meals.get('snack_morning'),
            'lunch': day_meals.get('lunch'),
            'snack_afternoon': day_meals.get('snack_afternoon'),
            'dinner': day_meals.get('dinner')
        }

        days_data.append({
            'date': current_date,
            'day_name': day_names_fr[current_date.weekday()],
            'is_today': current_date == today,
            'meals': meals_organized
        })

        current_date += timedelta(days=1)

    # Calculer les statistiques
    days_with_meals = sum(1 for day in days_data if any(day['meals'].values()))

    complete_days = 0
    for day in days_data:
        main_meals = ['breakfast', 'lunch', 'dinner']
        if all(day['meals'][t] is not None for t in main_meals):
            complete_days += 1

    total_exceptions = sum(1 for meal in all_meals if meal.qualification == 'exception')
    total_equilibrages = sum(1 for meal in all_meals if meal.qualification == 'equilibrage')

    # Détecter si on a des encas ou goûters AVEC DES ALIMENTS (pas juste "rien")
    has_snack_morning = any(
        meal.meal_type == 'snack_morning' and not meal.is_none and meal.foods
        for meal in all_meals
    )
    has_snack_afternoon = any(
        meal.meal_type == 'snack_afternoon' and not meal.is_none and meal.foods
        for meal in all_meals
    )

    # ========================================
    # RÉCUPÉRER LES ACTIVITÉS ET LES ORGANISER PAR JOUR
    # ========================================
    activities = ActivityEntry.query.filter(
        ActivityEntry.user_id == user_id,
        ActivityEntry.date >= start_date,
        ActivityEntry.date <= end_date
    ).order_by(ActivityEntry.date).all()

    # Organiser les activités par date
    activities_by_date = {}
    for activity in activities:
        if activity.date not in activities_by_date:
            activities_by_date[activity.date] = []
        activities_by_date[activity.date].append({
            'activity_type': activity.activity_type,
            'duration': activity.duration,
            'steps': activity.steps or 0,
            'calories_burned': activity.calories_burned,
            'note': activity.note
        })

    # Ajouter les activités dans days_data
    for day in days_data:
        day['activities'] = activities_by_date.get(day['date'], [])

    # Statistiques activités
    activities_stats = {
        'total_count': len(activities),
        'total_steps': sum(a.steps or 0 for a in activities),
        'total_calories': sum(a.calories_burned or 0 for a in activities)
    }

    stats = {
        'days_with_meals': days_with_meals,
        'complete_days': complete_days,
        'total_exceptions': total_exceptions,
        'total_equilibrages': total_equilibrages
    }

    return render_template('meals_recap.html',
                         days_data=days_data,
                         start_date=start_date,
                         end_date=end_date,
                         stats=stats,
                         has_snack_morning=has_snack_morning,
                         has_snack_afternoon=has_snack_afternoon,
                         activities_stats=activities_stats,
                         theme=user.theme)


@app.route('/api/get-day-meals')
@login_required
def get_day_meals():
    user_id = session['user_id']
    date_str = request.args.get('date')
    date = datetime.strptime(date_str, '%Y-%m-%d').date()

    # Récupérer les repas de ce jour
    day_meals = MealEntry.query.filter_by(
        user_id=user_id,
        date=date
    ).all()

    # Organiser par type
    meals_by_type = {
        'breakfast': {'foods': [], 'qualification': 'normal', 'is_none': False},
        'snack_morning': {'foods': [], 'qualification': 'normal', 'is_none': False},
        'lunch': {'foods': [], 'qualification': 'normal', 'is_none': False},
        'snack_afternoon': {'foods': [], 'qualification': 'normal', 'is_none': False},
        'dinner': {'foods': [], 'qualification': 'normal', 'is_none': False}
    }

    for meal in day_meals:
        meals_by_type[meal.meal_type] = {
            'foods': meal.get_foods_list(),
            'qualification': meal.qualification,
            'is_none': meal.is_none
        }

    return jsonify({
        'date': date_str,
        'meals': meals_by_type
    })

@app.route('/meals/save-day', methods=['POST'])
@login_required
def save_day_meals():
    user_id = session['user_id']
    date_str = request.form.get('date')
    date = datetime.strptime(date_str, '%Y-%m-%d').date()

    meal_types = ['breakfast', 'snack_morning', 'lunch', 'snack_afternoon', 'dinner']

    # Supprimer les anciens repas de ce jour
    MealEntry.query.filter_by(user_id=user_id, date=date).delete()

    # Sauvegarder les nouveaux repas
    for meal_type in meal_types:
        # Vérifier si "rien"
        is_none = request.form.get(f'{meal_type}_none') == 'on'

        # Récupérer les aliments
        foods = request.form.getlist(f'{meal_type}_food[]')
        foods = [f.strip() for f in foods if f.strip()]

        # Récupérer la qualification
        qualification = request.form.get(f'{meal_type}_qualification', 'normal')

        # Créer l'entrée seulement si "rien" OU au moins un aliment
        if is_none or len(foods) > 0:
            meal_entry = MealEntry(
                user_id=user_id,
                meal_type=meal_type,
                date=date,
                is_none=is_none,
                qualification=qualification
            )
            meal_entry.set_foods_list(foods)
            db.session.add(meal_entry)

    db.session.commit()

    return jsonify({'success': True})


# ========================================
# ROUTES ACTIVITÉS
# ========================================

@app.route('/activities')
@login_required
def activities():
    user_id = session['user_id']
    user = User.query.get(user_id)
    today = datetime.utcnow().date()

    entries = ActivityEntry.query.filter_by(user_id=user_id).order_by(
        ActivityEntry.date.desc(),
        ActivityEntry.created_at.desc()
    ).all()

    # Calculer des statistiques
    week_ago = today - timedelta(days=7)
    week_count = ActivityEntry.query.filter(
        ActivityEntry.user_id == user_id,
        ActivityEntry.date >= week_ago
    ).count()

    total_steps = sum(entry.steps or 0 for entry in entries)
    total_calories = sum(entry.calories_burned or 0 for entry in entries)

    stats = {
        'week_count': week_count,
        'total_steps': total_steps,
        'total_calories': total_calories
    }

    return render_template('activities.html',
                         entries=entries,
                         today=today,
                         stats=stats,
                         theme=user.theme)

@app.route('/activities/add', methods=['POST'])
@login_required
def add_activity():
    user_id = session['user_id']
    activity_type = request.form.get('activity_type')
    date_str = request.form.get('date')
    note = request.form.get('note', '')

    date = datetime.strptime(date_str, '%Y-%m-%d').date()

    # Pour le type "Pas"
    if activity_type == 'Pas':
        steps = int(request.form.get('steps', 0))
        duration = 0
        calories_burned = None

        new_entry = ActivityEntry(
            user_id=user_id,
            activity_type=activity_type,
            duration=duration,
            steps=steps,
            calories_burned=calories_burned,
            date=date,
            note=note
        )
    else:
        # Pour les autres activités
        duration = int(request.form.get('duration', 0))
        calories_burned = request.form.get('calories_burned')

        new_entry = ActivityEntry(
            user_id=user_id,
            activity_type=activity_type,
            duration=duration,
            steps=None,
            calories_burned=int(calories_burned) if calories_burned else None,
            date=date,
            note=note
        )

    db.session.add(new_entry)
    db.session.commit()

    flash('Activité enregistrée !', 'success')
    return redirect(url_for('activities'))

@app.route('/activities/delete/<int:id>')
@login_required
def delete_activity(id):
    entry = ActivityEntry.query.get_or_404(id)
    if entry.user_id != session['user_id']:
        flash('Action non autorisée.', 'danger')
        return redirect(url_for('activities'))

    db.session.delete(entry)
    db.session.commit()
    flash('Activité supprimée.', 'info')
    return redirect(url_for('activities'))

# ========================================
# API POUR LES GRAPHIQUES
# ========================================

@app.route('/api/weight-data')
@login_required
def weight_data():
    user_id = session['user_id']
    days = int(request.args.get('days', 30))

    start_date = datetime.utcnow().date() - timedelta(days=days)
    entries = WeightEntry.query.filter(
        WeightEntry.user_id == user_id,
        WeightEntry.date >= start_date
    ).order_by(WeightEntry.date).all()

    data = {
        'dates': [entry.date.strftime('%Y-%m-%d') for entry in entries],
        'weights': [entry.weight for entry in entries]
    }

    return jsonify(data)

# ========================================
# INITIALISATION DE LA BASE DE DONNÉES
# ========================================

@app.before_request
def create_tables():
    if not hasattr(app, 'tables_created'):
        db.create_all()
        app.tables_created = True

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

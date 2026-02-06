from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from authlib.integrations.flask_client import OAuth
from datetime import datetime, timedelta
import os
from functools import wraps
from dotenv import load_dotenv

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
    meal_type = db.Column(db.String(20), nullable=False)  # breakfast, lunch, dinner, snack
    description = db.Column(db.Text, nullable=False)
    calories = db.Column(db.Integer)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ActivityEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity_type = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # en minutes
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.password_hash and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash(f'Bienvenue {user.username} !', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Identifiants incorrects.', 'danger')

    return render_template('login.html', theme='green')

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

    # Récupérer les dernières données
    latest_weight = WeightEntry.query.filter_by(user_id=user_id).order_by(WeightEntry.date.desc()).first()
    today_meals = MealEntry.query.filter_by(user_id=user_id, date=datetime.utcnow().date()).all()
    today_activities = ActivityEntry.query.filter_by(user_id=user_id, date=datetime.utcnow().date()).all()

    # Statistiques
    total_calories_today = sum(meal.calories or 0 for meal in today_meals)
    total_calories_burned = sum(activity.calories_burned or 0 for activity in today_activities)

    # Poids des 30 derniers jours pour le graphique
    thirty_days_ago = datetime.utcnow().date() - timedelta(days=30)
    weight_history = WeightEntry.query.filter(
        WeightEntry.user_id == user_id,
        WeightEntry.date >= thirty_days_ago
    ).order_by(WeightEntry.date).all()

    user = User.query.get(session['user_id'])
    return render_template('dashboard.html',
                         latest_weight=latest_weight,
                         today_meals=today_meals,
                         today_activities=today_activities,
                         total_calories_today=total_calories_today,
                         total_calories_burned=total_calories_burned,
                         weight_history=weight_history,
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
    entries = MealEntry.query.filter_by(user_id=user_id).order_by(MealEntry.date.desc(), MealEntry.created_at.desc()).all()
    user = User.query.get(session['user_id'])
    return render_template('meals.html', entries=entries, theme=user.theme)

@app.route('/meals/add', methods=['POST'])
@login_required
def add_meal():
    user_id = session['user_id']
    meal_type = request.form.get('meal_type')
    description = request.form.get('description')
    calories = request.form.get('calories')
    date_str = request.form.get('date')

    date = datetime.strptime(date_str, '%Y-%m-%d').date()

    new_entry = MealEntry(
        user_id=user_id,
        meal_type=meal_type,
        description=description,
        calories=int(calories) if calories else None,
        date=date
    )
    db.session.add(new_entry)
    db.session.commit()

    flash('Repas enregistré !', 'success')
    return redirect(url_for('meals'))

@app.route('/meals/delete/<int:id>')
@login_required
def delete_meal(id):
    entry = MealEntry.query.get_or_404(id)
    if entry.user_id != session['user_id']:
        flash('Action non autorisée.', 'danger')
        return redirect(url_for('meals'))

    db.session.delete(entry)
    db.session.commit()
    flash('Repas supprimé.', 'info')
    return redirect(url_for('meals'))

# ========================================
# ROUTES ACTIVITÉS
# ========================================

@app.route('/activities')
@login_required
def activities():
    user_id = session['user_id']
    entries = ActivityEntry.query.filter_by(user_id=user_id).order_by(ActivityEntry.date.desc(), ActivityEntry.created_at.desc()).all()
    user = User.query.get(session['user_id'])
    return render_template('activities.html', entries=entries,theme=user.theme)

@app.route('/activities/add', methods=['POST'])
@login_required
def add_activity():
    user_id = session['user_id']
    activity_type = request.form.get('activity_type')
    duration = int(request.form.get('duration'))
    calories_burned = request.form.get('calories_burned')
    date_str = request.form.get('date')
    note = request.form.get('note', '')

    date = datetime.strptime(date_str, '%Y-%m-%d').date()

    new_entry = ActivityEntry(
        user_id=user_id,
        activity_type=activity_type,
        duration=duration,
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

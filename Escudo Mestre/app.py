import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime

app = Flask(__name__)

# Configuração do Banco de Dados e Segurança
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SECRET_KEY'] = 'mestre-do-rpg-secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'rpg.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# Tabelas
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Personagem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    classe = db.Column(db.String(100))
    hp = db.Column(db.Integer)
    status = db.Column(db.String(20), default="Vivo")

class Cronica(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(20))
    texto = db.Column(db.Text)

with app.app_context():
    db.create_all()
    # Garante um usuário para você entrar
    if not User.query.filter_by(username='Mestre').first():
        db.session.add(User(username='Mestre', password='123'))
        db.session.commit()

# --- ROTAS DE ACESSO ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and user.password == request.form.get('password'):
            login_user(user)
            return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- SUAS ROTAS ORIGINAIS (PROTEGIDAS) ---
@app.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        if 'texto_cronica' in request.form:
            nova = Cronica(data=datetime.now().strftime("%d/%m/%Y"), texto=request.form.get('texto_cronica'))
            db.session.add(nova)
        else:
            novo = Personagem(nome=request.form.get('nome'), classe=request.form.get('classe'), hp=request.form.get('hp'))
            db.session.add(novo)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('index.html', herois=Personagem.query.all(), sessoes=Cronica.query.order_by(Cronica.id.desc()).all())

@app.route('/status_p/<int:id>')
@login_required
def status_p(id):
    p = Personagem.query.get(id)
    if p:
        if p.status == "Vivo":
            p.status = "Morto"
            relato = f"O herói {p.nome} ({p.classe}) tombou em combate."
            nova = Cronica(data=datetime.now().strftime("%d/%m/%Y"), texto=relato)
            db.session.add(nova)
        else:
            p.status = "Vivo"
        db.session.commit()
    return redirect(url_for('home'))

@app.route('/editar_p/<int:id>', methods=['POST'])
@login_required
def editar_p(id):
    p = Personagem.query.get(id)
    if p:
        p.nome = request.form.get('nome')
        p.classe = request.form.get('classe')
        p.hp = request.form.get('hp')
        db.session.commit()
    return redirect(url_for('home'))

@app.route('/editar_c/<int:id>', methods=['POST'])
@login_required
def editar_c(id):
    c = Cronica.query.get(id)
    if c:
        c.texto = request.form.get('texto_cronica')
        db.session.commit()
    return redirect(url_for('home'))

@app.route('/del_p/<int:id>')
@login_required
def del_p(id):
    p = Personagem.query.get(id)
    if p:
        db.session.delete(p)
        db.session.commit()
    return redirect(url_for('home'))

@app.route('/del_c/<int:id>')
@login_required
def del_c(id):
    c = Cronica.query.get(id)
    if c:
        db.session.delete(c)
        db.session.commit()
    return redirect(url_for('home'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

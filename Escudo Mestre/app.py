import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Configuração do Banco de Dados
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'rpg.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Tabelas
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

@app.route('/', methods=['GET', 'POST'])
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
def editar_p(id):
    p = Personagem.query.get(id)
    if p:
        p.nome = request.form.get('nome')
        p.classe = request.form.get('classe')
        p.hp = request.form.get('hp')
        db.session.commit()
    return redirect(url_for('home'))

@app.route('/del_p/<int:id>')
def del_p(id):
    p = Personagem.query.get(id)
    if p:
        db.session.delete(p)
        db.session.commit()
    return redirect(url_for('home'))

@app.route('/del_c/<int:id>')
def del_c(id):
    c = Cronica.query.get(id)
    if c:
        db.session.delete(c)
        db.session.commit()
    return redirect(url_for('home'))

# ... (mantenha todo o seu código anterior de rotas e tabelas igual)

if __name__ == '__main__':
    # O Render define a porta pela variável de ambiente PORT. 
    # Se não houver, ele usa a 5000 (local).
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    app.run(debug=True)

# Mantenha suas rotas acima...

if __name__ == '__main__':
    # Isso é para rodar localmente no seu PC
    app.run(debug=True)

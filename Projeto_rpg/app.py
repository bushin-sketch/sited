from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
# Aqui entrariam as bibliotecas de Banco de Dados (SQLAlchemy)

app = Flask(__name__)
app.secret_key = "lumini_luxo_real"

# Agora temos dois tipos de usuários no sistema:
# 1. O DONO: Pode mudar seu próprio e-mail/senha no painel.
# 2. O CLIENTE: Tem seu perfil, favoritos e lista de pedidos.

@app.route('/perfil-cliente')
def perfil():
    if 'user_id' not in session: return redirect(url_for('login_cliente'))
    # Busca histórico de compras e favoritos no banco de dados
    return render_template('perfil.html')

@app.route('/favoritos/add/<int:prod_id>')
def add_favorito(prod_id):
    # Lógica para salvar o produto na lista de desejos do cliente
    return redirect(url_for('index'))

@app.route('/config-dono', methods=['POST'])
def configurar_dono():
    # Permite que o dono altere seu e-mail, nome e senha
    novo_email = request.form['email']
    nova_senha = request.form['senha']
    # Salva no banco de dados
    return redirect(url_for('admin'))
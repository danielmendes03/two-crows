import os
import bleach
import re
from datetime import datetime
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

# --- CONFIGURAÇÃO DA APLICAÇÃO ---
# Usamos instance_relative_config=True para que o Flask procure o db na pasta 'instance'
app = Flask(__name__, instance_relative_config=True)

# Garante que a pasta 'instance' exista. É onde o nosso banco de dados ficará.
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

# --- GERAÇÃO RANDÔMICA DA SECRET_KEY ---
app.config['SECRET_KEY'] = os.urandom(24)


# --- CONFIGURAÇÃO DO BANCO DE DADOS (SEM CRIPTOGRAFIA) ---
# O caminho do banco agora aponta para a pasta 'instance', que será persistida pelo Docker.
db_path = os.path.join(app.instance_path, 'database.db')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicialização do banco de dados
db = SQLAlchemy(app)


# --- VALIDAÇÃO COM REGEX ---
# Define o padrão de caracteres permitidos para o nome.
VALID_NAME_REGEX = re.compile(r"^[a-zA-Z0-9À-ÖØ-öø-ÿ.@ ]+$")


# --- MODELO DO BANCO DE DADOS ---
class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    interest = db.Column(db.String(50), nullable=False)
    enthusiasm = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Submission {self.name} - {self.email}>'


# --- ROTAS DA APLICAÇÃO ---
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # 1. Limpeza e Sanitização da Entrada (Proteção contra XSS)
        name = bleach.clean(request.form.get('name'))
        email = bleach.clean(request.form.get('email'))
        interest = bleach.clean(request.form.get('interest'))
        enthusiasm = request.form.get('enthusiasm')

        # --- VALIDAÇÃO DE NOME (REGEX) ---
        if not name or not VALID_NAME_REGEX.match(name):
            flash('O nome contém caracteres inválidos. Apenas letras, números, espaços, "." e "@" são permitidos.', 'error')
            return redirect(url_for('home') + '#contact')
        # ----------------------------------------

        # 2. Verificação de E-mail Único
        existing_submission = Submission.query.filter_by(email=email).first()

        if existing_submission:
            flash('Este e-mail já foi cadastrado em nosso sistema. Obrigado!', 'error')
        else:
            # 3. Criação e Inserção do Novo Registro
            new_submission = Submission(
                name=name,
                email=email,
                interest=interest,
                enthusiasm=int(enthusiasm)
            )
            db.session.add(new_submission)
            db.session.commit()
            flash('Obrigado pelo seu feedback! Ele foi registrado com sucesso.', 'success')
        
        return redirect(url_for('home') + '#contact')

    return render_template('index.html')

# Comando para criar o banco de dados via terminal
# ATENÇÃO: Para criar o banco dentro do container, use o comando:
# docker-compose exec web flask init-db
@app.cli.command('init-db')
def init_db_command():
    """Cria as tabelas do banco de dados."""
    db.create_all()
    print('Banco de dados inicializado.')
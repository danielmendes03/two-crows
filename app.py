import os
import bleach
import re
from datetime import datetime
from flask import Flask, render_template, request, flash, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy

# --- CONFIGURAÇÃO DA APLICAÇÃO ---
app = Flask(__name__)

# Chave secreta para sessões e mensagens flash
app.config['SECRET_KEY'] = os.urandom(24)

# Chave secreta para a nossa página de administração (guarde esta chave em segurança!)
ADMIN_SECRET_KEY = os.environ.get('ADMIN_SECRET_KEY')

# Configuração da base de dados (caminho para o volume persistente do Docker)
db_path = os.path.join('/app/instance', 'database.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicialização da base de dados
db = SQLAlchemy(app)

# --- VALIDAÇÃO COM REGEX ---
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
        name = bleach.clean(request.form.get('name'))
        email = bleach.clean(request.form.get('email'))
        interest = bleach.clean(request.form.get('interest'))
        enthusiasm = request.form.get('enthusiasm')

        if not name or not VALID_NAME_REGEX.match(name):
            flash('O nome contém caracteres inválidos.', 'error')
            return redirect(url_for('home') + '#contact')

        existing_submission = Submission.query.filter_by(email=email).first()

        if existing_submission:
            flash('Este e-mail já foi registado. Obrigado!', 'error')
        else:
            new_submission = Submission(name=name, email=email, interest=interest, enthusiasm=int(enthusiasm))
            db.session.add(new_submission)
            db.session.commit()
            flash('Obrigado pelo seu feedback! Foi registado com sucesso.', 'success')
        
        return redirect(url_for('home') + '#contact')

    return render_template('index.html')

# --- NOVA ROTA DE ADMINISTRAÇÃO ---
@app.route('/admin-view/<secret_key>')
def admin_view(secret_key):
    # 1. Verifica se a chave secreta no URL está correta
    if secret_key != ADMIN_SECRET_KEY:
        # Se a chave estiver errada, retorna um erro "Não encontrado" para não revelar que a página existe.
        abort(404)
    
    # 2. Consulta todos os registos da base de dados, ordenados do mais recente para o mais antigo
    all_submissions = Submission.query.order_by(Submission.timestamp.desc()).all()
    
    # 3. Renderiza o novo template 'admin.html', passando os dados
    return render_template('admin.html', submissions=all_submissions)

# Comando para criar a base de dados via terminal
@app.cli.command('init-db')
def init_db_command():
    """Cria as tabelas da base de dados."""
    db.create_all()
    print('Base de dados inicializada.')

# --- INICIALIZAÇÃO DO SERVIDOR ---
# (Este bloco é usado pelo Gunicorn dentro do Docker)
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)


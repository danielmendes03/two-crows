import os
import bleach
import re
from datetime import datetime
from flask import Flask, render_template, request, flash, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy

# --- CONFIGURAÇÃO DA APLICAÇÃO ---
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24))
ADMIN_SECRET_KEY = os.environ.get('ADMIN_SECRET_KEY')

# --- Configuração da Base de Dados PostgreSQL ---
db_uri = os.environ.get('DATABASE_URL')
if db_uri and db_uri.startswith("postgres://"):
    db_uri = db_uri.replace("postgres://", "postgresql://", 1)

# Fallback para SQLite local se a DATABASE_URL não estiver definida
if not db_uri:
    basedir = os.path.abspath(os.path.dirname(__file__))
    instance_path = os.path.join(basedir, 'instance')
    os.makedirs(instance_path, exist_ok=True)
    db_path = os.path.join(instance_path, 'database.db')
    db_uri = 'sqlite:///' + db_path

app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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

# --- ATUALIZADO: Inicializa a base de dados ao arrancar ---
# Este bloco de código será executado quando a aplicação for iniciada no Render.
# Ele cria as tabelas na base de dados PostgreSQL se elas ainda não existirem.
with app.app_context():
    db.create_all()
# ---------------------------------------------------------

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

@app.route('/admin-view/<secret_key>')
def admin_view(secret_key):
    if secret_key != ADMIN_SECRET_KEY:
        abort(404)
    
    all_submissions = Submission.query.order_by(Submission.timestamp.desc()).all()
    
    return render_template('admin.html', submissions=all_submissions)

# --- Comando init-db (ainda útil para desenvolvimento local) ---
@app.cli.command('init-db')
def init_db_command():
    """Cria as tabelas da base de dados."""
    db.create_all()
    print('Base de dados inicializada e tabelas criadas.')

# --- INICIALIZAÇÃO DO SERVIDOR (para desenvolvimento local) ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)


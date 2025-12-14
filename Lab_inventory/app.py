from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import date
import os
from werkzeug.utils import secure_filename 

# --- Configurações da Aplicação ---
app = Flask(__name__)

# Configuração da Chave Secreta: Lendo da variável de ambiente para produção.
app.secret_key = os.environ.get('SECRET_KEY', 'default-secret-key-MUDAR-DEPOIS')

# Configuração do Banco de Dados (PostgreSQL para Render, SQLite para Local)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Boa prática para Flask-SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

# Se não houver variável de ambiente, usa SQLite como fallback (para desenvolvimento local)
if not app.config['SQLALCHEMY_DATABASE_URI']:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    
# Correção do prefixo para PostgreSQL (compatibilidade com versões antigas do SQLAlchemy)
if app.config['SQLALCHEMY_DATABASE_URI'].startswith("postgres://"):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace(
        "postgres://", "postgresql://", 1
    )

app.config['UPLOAD_FOLDER'] = 'static/uploads'
db = SQLAlchemy(app)

# --- Criação das Tabelas do Banco de Dados (NOVA CORREÇÃO) ---
# Este bloco garante que as tabelas sejam criadas no PostgreSQL quando o Gunicorn iniciar o app.
with app.app_context():
    try:
        db.create_all()
        # Não é necessário imprimir no console do Render, mas ajuda no log
        print("Tabelas do banco de dados verificadas/criadas com sucesso.")
    except Exception as e:
        print(f"Erro ao criar tabelas no PostgreSQL: {e}")


# --- Modelos do Banco de Dados ---

class Equipment(db.Model):
    __tablename__ = 'equipment' 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(100))
    model = db.Column(db.String(100))
    purpose = db.Column(db.String(200))
    quantity = db.Column(db.Integer)
    image = db.Column(db.String(200))
    reservations = db.relationship('Reservation', backref='equipment', lazy=True, cascade="all, delete-orphan")

class Reservation(db.Model):
    __tablename__ = 'reservation' 
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    user_name = db.Column(db.String(100), nullable=False)
    institution = db.Column(db.String(100))
    role = db.Column(db.String(100))
    date = db.Column(db.String(20), nullable=False)


# --- Rotas Públicas ---

@app.route('/')
def index():
    # Estas informações podem ser editadas ou lidas de uma tabela de configurações no futuro
    coordenator_info = {
        'name': 'Nome do Coordenador',
        'email': 'email@institucional'
    }
    return render_template('index.html', info=coordenator_info)

@app.route('/inventory')
def inventory():
    # Esta consulta estava falhando por causa da falta de tabelas
    equipments = Equipment.query.all()
    return render_template('inventory.html', equipments=equipments)

@app.route('/reserve/<int:id>', methods=['GET','POST'])
def reserve(id):
    equipment = Equipment.query.get_or_404(id)
    
    if request.method == 'POST':
        if equipment.quantity <= 0:
            return f"O equipamento {equipment.name} não está disponível para reserva no momento.", 400

        r = Reservation(
            equipment_id=id,
            user_name=request.form.get('name'),
            institution=request.form.get('institution'),
            role=request.form.get('role'),
            date=request.form.get('date')
        )
        
        if not all([r.user_name, r.institution, r.role, r.date]):
             return "Todos os campos da reserva devem ser preenchidos.", 400

        db.session.add(r)
        db.session.commit()
        return redirect(url_for('inventory'))
    
    return render_template('reserve.html', equipment=equipment)

# --- Rotas de Autenticação e Admin ---

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        if request.form.get('user') == 'admin' and request.form.get('password') == 'admin123':
            session['admin'] = True
            return redirect(url_for('admin'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

@app.route('/admin', methods=['GET','POST'])
def admin():
    if not session.get('admin'):
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        try:
            # 1. Processamento da Imagem
            f = request.files.get('image')
            
            if f and f.filename != '':
                filename = secure_filename(f.filename) 
                path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                if not os.path.exists(app.config['UPLOAD_FOLDER']):
                    os.makedirs(app.config['UPLOAD_FOLDER'])
                    
                f.save(path)
            else:
                filename = None

            # 2. Cadastro do Equipamento
            quantity = int(request.form.get('quantity', 0))
            if quantity < 0:
                 raise ValueError("A quantidade não pode ser negativa.")

            e = Equipment(
                name=request.form.get('name'),
                brand=request.form.get('brand'),
                model=request.form.get('model'),
                purpose=request.form.get('purpose'),
                quantity=quantity,
                image=filename
            )
            
            db.session.add(e)
            db.session.commit()
            return redirect(url_for('admin'))
            
        except ValueError as ve:
            return f"Erro na entrada de dados: {ve}", 400
        except Exception as e:
            return f"Erro ao cadastrar: {e}", 500
            
    # GET: Exibe a interface de admin
    equipments = Equipment.query.all()
    reservations = Reservation.query.all()
    
    return render_template('admin.html', equipments=equipments, reservations=reservations)


@app.route('/delete/<int:id>', methods=['POST'])
def delete_equipment(id):
    if not session.get('admin'):
        return redirect(url_for('login'))
        
    equipment = Equipment.query.get_or_404(id)
    
    try:
        # As reservas relacionadas serão excluídas automaticamente devido ao cascade="all, delete-orphan"
        db.session.delete(equipment)
        db.session.commit()
        
        # Excluir imagem
        if equipment.image:
            img_path = os.path.join(app.config['UPLOAD_FOLDER'], equipment.image)
            if os.path.exists(img_path):
                os.remove(img_path)
                
    except Exception as e:
        db.session.rollback()
        return f"Erro ao excluir o equipamento: {e}", 500
            
    return redirect(url_for('admin'))


@app.route('/delete_reservation/<int:id>', methods=['POST'])
def delete_reservation(id):
    if not session.get('admin'):
        return redirect(url_for('login'))
        
    reservation = Reservation.query.get_or_404(id)
    
    try:
        db.session.delete(reservation)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return f"Erro ao excluir a reserva: {e}", 500
    
    return redirect(url_for('admin'))


# --- Inicialização da Aplicação ---
# O Gunicorn usará o objeto 'app' diretamente, executando o código acima,
# incluindo o bloco db.create_all() que agora está fora do if __name__.

if __name__ == '__main__':
    # Usado apenas para rodar em ambiente local de desenvolvimento
    port = int(os.environ.get('PORT', 5000))
    # Note que db.create_all() já foi chamado acima.
    app.run(host='0.0.0.0', port=port, debug=True)

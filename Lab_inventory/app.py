from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import date
import os

# --- Configurações ---
app = Flask(__name__)
# Mude isso para uma string aleatória longa e complexa para produção!
app.secret_key = os.environ.get('SECRET_KEY', 'default-secret-key-MUDAR-DEPOIS')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db = SQLAlchemy(app)

# --- Modelos do Banco de Dados ---
class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(100))
    model = db.Column(db.String(100))
    purpose = db.Column(db.String(200))
    quantity = db.Column(db.Integer)
    image = db.Column(db.String(200))

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer)
    user_name = db.Column(db.String(100), nullable=False)
    institution = db.Column(db.String(100))
    role = db.Column(db.String(100))
    date = db.Column(db.String(20)) # Armazena a data como string YYYY-MM-DD

# --- Rotas Públicas ---

@app.route('/')
def index():
    # O coordenador pode editar estes dados através da rota /admin (não implementado neste exemplo, mas
    # pode ser simulado ou hardcoded para o propósito de identificação inicial)
    coordenator_info = {
        'name': 'Nome do Coordenador',
        'email': 'email@institucional'
    }
    return render_template('index.html', info=coordenator_info)

@app.route('/inventory')
def inventory():
    # Exibe todos os equipamentos
    equipments = Equipment.query.all()
    # Para a lógica de reserva, precisamos saber quantos estão reservados em determinada data.
    # A implementação completa para verificar disponibilidade é complexa. Aqui,
    # vamos checar apenas se a quantidade total é maior que zero.
    return render_template('inventory.html', equipments=equipments)

@app.route('/reserve/<int:id>', methods=['GET','POST'])
def reserve(id):
    equipment = Equipment.query.get_or_404(id)
    
    if request.method == 'POST':
        # Simples checagem de disponibilidade: impede reserva se a quantidade total for 0.
        if equipment.quantity <= 0:
            # Em uma aplicação real, você deve renderizar uma mensagem de erro.
            return f"O equipamento {equipment.name} não está disponível para reserva no momento.", 400

        # Implementação de Reserva: Registra o pedido de reserva.
        r = Reservation(
            equipment_id=id,
            user_name=request.form['name'],
            institution=request.form['institution'],
            role=request.form['role'],
            date=request.form['date']
        )
        db.session.add(r)
        db.session.commit()
        return redirect(url_for('inventory'))
    
    # Passa o equipamento para o template para exibir o nome na página de reserva
    return render_template('reserve.html', equipment=equipment)

# --- Rotas de Autenticação e Admin ---

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        # Usando credenciais fixas (ADMIN/ADMIN123) conforme seu código original. 
        # ATENÇÃO: Mude isso para um sistema de hashing e um DB de usuários em produção!
        if request.form['user'] == 'admin' and request.form['password'] == 'admin123':
            session['admin'] = True
            return redirect(url_for('admin'))
    return render_template('login.html')

@app.route('/admin', methods=['GET','POST'])
def admin():
    # Proteção: Se não for admin na sessão, redireciona para o login
    if not session.get('admin'):
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        try:
            # 1. Processamento da Imagem
            f = request.files['image']
            if f.filename == '':
                filename = None
            else:
                # Segurança: Sanitizar o nome do arquivo para evitar Path Traversal (Ainda recomendado usar 
                # uma biblioteca como werkzeug.utils.secure_filename em produção)
                filename = f.filename.replace('..', '').replace('/', '\\')
                path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                # Garante que a pasta 'uploads' exista
                if not os.path.exists(app.config['UPLOAD_FOLDER']):
                    os.makedirs(app.config['UPLOAD_FOLDER'])
                f.save(path)

            # 2. Cadastro do Equipamento
            e = Equipment(
                name=request.form['name'],
                brand=request.form['brand'],
                model=request.form['model'],
                purpose=request.form['purpose'],
                # CORREÇÃO: Converte a quantidade para Integer
                quantity=int(request.form['quantity']), 
                image=filename
            )
            db.session.add(e)
            db.session.commit()
            return redirect(url_for('admin'))
            
        except ValueError:
            # Captura erro se quantity não for um número inteiro
            return "Erro: A quantidade deve ser um número inteiro.", 400
        except Exception as e:
            return f"Erro ao cadastrar: {e}", 500
            
    # GET: Exibe a interface de admin com a lista de equipamentos e reservas
    equipments = Equipment.query.all()
    reservations = Reservation.query.all()
    
    return render_template('admin.html', equipments=equipments, reservations=reservations)


@app.route('/delete/<int:id>', methods=['POST'])
def delete_equipment(id):
    if not session.get('admin'):
        return redirect(url_for('login'))
        
    equipment = Equipment.query.get_or_404(id)
    
    # 1. Excluir o registro do banco de dados
    db.session.delete(equipment)
    db.session.commit()
    
    # 2. (Opcional) Excluir a imagem do sistema de arquivos
    if equipment.image:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], equipment.image))
        except FileNotFoundError:
            # Ignora se o arquivo não existir
            pass
            
    return redirect(url_for('admin'))


@app.route('/delete_reservation/<int:id>', methods=['POST'])
def delete_reservation(id):
    if not session.get('admin'):
        return redirect(url_for('login'))
        
    reservation = Reservation.query.get_or_404(id)
    db.session.delete(reservation)
    db.session.commit()
    
    return redirect(url_for('admin'))


# --- Inicialização ---

if __name__ == '__main__':
    # Usado para configurar o DB na primeira execução
    with app.app_context():
        db.create_all()
        
    # Configuração para deploy no Render
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
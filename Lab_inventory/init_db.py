from app import app, db
import sys

# Script simples para criar as tabelas no banco de dados.
# Este script será executado pelo Render no passo de build, 
# garantindo que o PostgreSQL esteja pronto antes de iniciar o servidor Gunicorn.

try:
    with app.app_context():
        # Cria as tabelas que não existirem
        db.create_all() 
        print("Tabelas do banco de dados criadas/verificadas com sucesso.")
    sys.exit(0) # Sair com sucesso (código 0)
    
except Exception as e:
    # Saída de erro caso a conexão ou criação falhe
    print(f"ERRO CRÍTICO ao inicializar o banco de dados: {e}", file=sys.stderr)
    sys.exit(1) # Sair com erro (código 1)

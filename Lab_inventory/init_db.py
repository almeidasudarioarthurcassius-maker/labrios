from app import app, db
import sys

# Script simples para criar as tabelas no banco de dados.
# Usado no processo de build do Render.

try:
    with app.app_context():
        # Cria as tabelas que não existirem
        db.create_all() 
        print("Tabelas do banco de dados criadas/verificadas com sucesso.")
    sys.exit(0) # Sair com sucesso
    
except Exception as e:
    print(f"ERRO CRÍTICO ao inicializar o banco de dados: {e}", file=sys.stderr)
    sys.exit(1) # Sair com erro

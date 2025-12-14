from app import app, db, LabInfo # Import LabInfo agora
import sys

# Script para criar as tabelas no banco de dados e preencher a LabInfo inicial.

try:
    with app.app_context():
        # Cria as tabelas (incluindo as novas: LabInfo e Reservation atualizada)
        db.create_all() 
        print("Tabelas do banco de dados criadas/verificadas com sucesso.")
        
        # POPULAR INFORMAÇÕES DO LABORATÓRIO (LabInfo)
        if LabInfo.query.count() == 0:
            initial_info = LabInfo(
                lab_name='LABORATÓRIO DE ANÁLISE DE ÁGUA DO BAIXO AMAZONAS – LABRIOS/CESP',
                affiliation='Mestado Profissional em Gestão e Regulação de Recursos Hidricos – ProfÁgua.',
                coordinator_name='Rafael Jovito Souza',
                coordinator_email='rjovito@uea.edu.br',
                coordinator_lattes='https://lattes.cnpq.br/8383334374831950',
                location='CENTRO DE ESTUDOS SUPERIORES DE PARINTINS',
                address='BLOCO DE LABORATÓRIOS DO CESP/UEA, Odovaldo Novo, 0, Djard Vieira, CEP: 69152470 Andar: 1'
            )
            db.session.add(initial_info)
            db.session.commit()
            print("Informações iniciais do laboratório cadastradas.")
        
    sys.exit(0)
    
except Exception as e:
    print(f"ERRO CRÍTICO ao inicializar o banco de dados: {e}", file=sys.stderr)
    sys.exit(1)

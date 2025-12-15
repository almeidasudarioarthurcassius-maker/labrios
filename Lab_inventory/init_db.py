from app import app, db, LabInfo
import sys

try:
    with app.app_context():
        # CORREÇÃO: recria o banco para sincronizar colunas
        db.drop_all()
        db.create_all()

        print("Tabelas recriadas com sucesso.")

        if LabInfo.query.count() == 0:
            initial_info = LabInfo(
                lab_name='LABORATÓRIO DE ANÁLISE DE ÁGUA DO BAIXO AMAZONAS – LABRIOS/CESP',
                affiliation='Mestrado Profissional em Gestão e Regulação de Recursos Hídricos – ProfÁgua',
                coordinator_name='Rafael Jovito Souza',
                coordinator_email='rjovito@uea.edu.br',
                coordinator_lattes='https://lattes.cnpq.br/8383334374831950',
                location='CENTRO DE ESTUDOS SUPERIORES DE PARINTINS',
                address='Bloco de Laboratórios do CESP/UEA'
            )
            db.session.add(initial_info)
            db.session.commit()

        sys.exit(0)

except Exception as e:
    print(f"ERRO AO INICIALIZAR BANCO: {e}", file=sys.stderr)
    sys.exit(1)

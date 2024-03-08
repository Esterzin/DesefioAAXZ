import pandas as pd

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configurações iniciais, puxando a planilha com as abas, id e células
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SPREADSHEET_ID = '1Rm__aeUvFpPANdIZlRfan5HYb7H-VPzFZSuPilp6FX8'
RANGE_VENDAS = 'Vendas!A1:F35'
RANGE_PAGAMENTOS = 'Pagamentos!A1:C14'

# Autenticação e token da API
creds = None
if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("credentials.json", SCOPES)
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
    with open("token.json", "w") as token:
        token.write(creds.to_json())

service = build("sheets", "v4", credentials=creds)

# Ler dados da planilha
sheet = service.spreadsheets()
result_vendas = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_VENDAS).execute()
rows_vendas = result_vendas.get('values', [])

result_pagamentos = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_PAGAMENTOS).execute()
rows_pagamentos = result_pagamentos.get('values', [])

df_vendas = pd.DataFrame(vendas_data)
df_pagamentos = pd.DataFrame(pagamentos_data)

# Calcular comissões, cada vendedor recebe 10% de cada venda.
comissoes = {}
def calcular_comissao(vendas):
    vendas['Comissão'] = vendas['Valor da Venda'] * 0.10
    vendas['Comissão Final'] = vendas.apply(lambda x: x['Comissão'] * 0.80 if x['Canal'] == 'Online' else x['Comissão'], axis=1)
    vendas['Comissão Final'] = vendas['Comissão Final'].apply(lambda x: x * 0.90 if x >= 1500 else x)
    return vendas.groupby('Vendedor')['Comissão Final'].sum().reset_index()

# Função para validar pagamentos
def validar_pagamentos(comissoes, pagamentos):
    pagamentos_errados = pd.merge(comissoes, pagamentos, on='Vendedor', how='left', suffixes=('_comissao', '_pagamento'))
    pagamentos_errados['Diferença'] = pagamentos_errados['Comissão Final'] - pagamentos_errados['Valor Pago']
    return pagamentos_errados[pagamentos_errados['Diferença'] != 0][['Vendedor', 'Valor Pago', 'Comissão Final']]
    # Calcular comissões
    comissoes = calcular_comissao(df_vendas)

    # Validar pagamentos
    pagamentos_incorretos = validar_pagamentos(comissoes, df_pagamentos)

    # Exibir resultados
    print("Comissões calculadas:")
    print(comissoes)
    print("\nPagamentos incorretos:")
    print(pagamentos_incorretos)

    except HttpError as err:
        print(err)

if __name__ == "__main__":
    main()


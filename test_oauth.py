import requests
import json
from datetime import datetime
from urllib.parse import urlencode

# Configurações
BASE_URL = 'http://localhost:8000'
CLIENT_ID = 'Oj0LfmO5f4Nj7m4Gc8sdlozyhH2ww0nde9y2jAYx'
CLIENT_SECRET = 'gJru2XlOXQIFbOpHPf3gZLUJIlh7xB33n1SLsi20ldWrHhtOFSXNhcmFK1Gn2C48QA9SlOTE41STUt9R9umZiJY1vBtIY0njNi6CEM2juFGJLzmLR6dTZMdYY3NhREjM'

def obter_token():
    """Obtém um token de acesso usando o fluxo client_credentials"""
    url = f'{BASE_URL}/o/token/'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    form_data = {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'scope': 'read write'
    }
    
    # Codifica os dados no formato application/x-www-form-urlencoded
    encoded_data = urlencode(form_data)
    
    response = requests.post(url, data=encoded_data, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro ao obter token: {response.status_code}")
        print(response.text)
        return None

def testar_endpoint_protegido(access_token):
    """Testa um endpoint protegido usando o token de acesso"""
    url = f'{BASE_URL}/api/books/'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print("\nResposta do endpoint protegido:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"\nErro ao acessar endpoint protegido: {response.status_code}")
        print(response.text)

def main():
    print("Testando autenticação OAuth 2.0 com client_credentials")
    print("=" * 50)
    
    # 1. Obter token inicial
    print("\n1. Obtendo token de acesso...")
    tokens = obter_token()
    if not tokens:
        return
    
    print("\nToken obtido com sucesso!")
    print(f"Access Token: {tokens['access_token'][:20]}...")
    print(f"Expira em: {tokens['expires_in']} segundos")
    
    # 2. Testar endpoint protegido
    print("\n2. Testando endpoint protegido...")
    # testar_endpoint_protegido(tokens['access_token'])

if __name__ == '__main__':
    main() 
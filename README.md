# API Game of Thrones

API simples para consulta de informações sobre Game of Thrones.

## Como rodar

### Com Docker (Recomendado)

1. Instale o Docker e Docker Compose
2. Clone o repositório
3. Execute:
```bash
docker-compose up --build
```

### Sem Docker

1. Instale o Python 3.9
2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```
3. Instale as dependências:
```bash
pip install -r requirements.txt
```
4. Execute o servidor:
```bash
python manage.py runserver
```

## Endpoints

- `/api/books/` - Lista de livros
- `/api/characters/` - Lista de personagens
- `/api/houses/` - Lista de casas

## Documentação

Acesse a documentação em:
- Swagger UI: `http://localhost:8000/swagger/`
- ReDoc: `http://localhost:8000/redoc/`

## Autenticação

A API usa OAuth2 para autenticação. Para obter um token:

1. Acesse `/o/applications/` e crie uma aplicação
2. Use as credenciais para obter um token em `/o/token/`
3. Use o token no header: `Authorization: Bearer <seu_token>` 
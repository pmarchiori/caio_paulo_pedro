# Customer Support Ticket - Projeto de Bloco (TP1)

## Objetivo do Projeto

Este projeto tem como objetivo analisar o dataset **Customer Support Ticket Dataset** (Kaggle) e construir a estrutura base de uma API em FastAPI com autenticação JWT, que futuramente vai servir um sistema de atendimento ao cliente baseado em IA.

O trabalho está dividido em duas partes:
- **EDA (Análise Exploratória de Dados)**: entendimento, limpeza e análise inicial do dataset de tickets de suporte.
- **API (FastAPI)**: estrutura modular com autenticação JWT, contendo as rotas `/health`, `/auth/token` e `/predict`.

## Estrutura de Pastas

```text
├── data/            # Dataset em .csv usado na análise
├── eda/             # Notebook (.ipynb) com a análise exploratória dos dados
├── fastapi/         # Código-fonte da API (main.py, routes, models, security)
├── others/          # DFD (Data Flow Diagram) da API em .png
├── README.md
└── requirements.txt # Dependências da API
```


## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/pmarchiori/caio_paulo_pedro.git
cd caio_paulo_pedro
```

Crie e ative um ambiente virtual:
```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Linux/Mac
```

Instale as dependências da API:
``` bash
pip install -r requirements.txt
```

Para rodar o notebook de EDA, instale também:
```bash
pip install pandas matplotlib seaborn numpy scipy jupyter
```
### Execução
## Rodando a API
Entre na pasta fastapi/ e suba o servidor:
```bash
cd fastapi
uvicorn main:app --reload
```

A API vai ficar disponível em http://127.0.0.1:8000. A documentação interativa (Swagger) fica em http://127.0.0.1:8000/docs.

### Executando os testes

Entre na pasta `fastapi/` e execute o pytest:

```bash
cd fastapi
pytest -v
```

### Rotas disponíveis:

*GET /health* - verifica se a API está no ar.
*POST /auth/token* - autentica e retorna um token JWT.
*POST /predict* - recebe um texto e retorna uma intenção simulada (rota protegida, exige token).

### Rodando o EDA
Abra o notebook: 
**eda/Caio_Pereira_Paulo_Dias_Pedro_Araujo_PB_TP1.ipynb**

# Customer Support Ticket - Projeto de Bloco (TP2)

### Rotas disponíveis:

*POST /auth/signup - Faz o cadastro do usuário na aplicação.
*POST /auth/signin - Faz o login do usuário na aplicação.

*OBS: Endpoint /auth/token fica disponível apenas para o uso interno do swagger.

# Auditoria final de segurança (TP3)

### Correções aplicadas
- `/me` não expõe mais `hashed_password` (rota duplicada em `main.py` removida; vale a de `routes/router.py`, com `UserRead`).
- `/docs` agora serve o Swagger UI **localmente** (`fastapi/static/swagger/`, swagger-ui-dist 5.17.14), sem CDN e sem script inline. A CSP estrita (`script-src 'self'`, `style-src 'self'`) vale para todas as rotas. `/redoc` foi desabilitado. Isso elimina os 3 findings Medium do ZAP (CSP `script-src`/`style-src` com `unsafe-inline` e SRI ausente).
- Rate limiting em `/auth/signin` (10/min), `/auth/signup` (5/min), `/auth/token` (10/min) e `/predict` (30/min).
- Validação de entrada: `username` 3-50 (letras, números, `_ . -`), `password` 8-72, `text` 1-2000.
- OpenAPI documentado (`summary`, `description`, `responses`, tags, exemplos).

### Preparação para pentest
```bash
cp .env.example .env     # troque o SECRET_KEY por um valor aleatório
cd fastapi
uvicorn main:app --host 0.0.0.0 --port 8000
```
- Docs: `http://<IP>:8000/docs`
- Usuários de teste (criados pelo seed): `alice`/`alice123`, `bruno`/`bruno123`
- Testes: `cd fastapi && pytest tests/ -v`

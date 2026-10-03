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
├── fastapi/         # Código-fonte da API (main.py, routers, models, security)
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
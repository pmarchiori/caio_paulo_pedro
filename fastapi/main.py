from contextlib import asynccontextmanager

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from database.seed import seed
from middlewares import configure_middlewares
from rate_limit import configure_rate_limiting
from routes import api_router, oauth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    seed()
    yield

STATIC_DIR = Path(__file__).resolve().parent / "static"

# [ZAP Finding 1, 2 e 3 - CSP com 'unsafe-inline' e SRI ausente (Medium)]
# CORRIGIDO: o Swagger UI do FastAPI carregava JS/CSS de CDN com script inline.
# Agora docs_url=None desliga a página padrão, os assets ficam em /static
# (mesma origem) e o /docs abaixo usa um init.js externo, sem script inline.
# Com isso a CSP estrita vale para todas as rotas e não há recurso de terceiros.
# redoc_url=None remove o /redoc, que também usava CDN.


app = FastAPI(
    title="API de Atendimento ao Cliente",
    version="1.0.0",
    description=(
        "API do Projeto de Bloco: classifica a intenção de textos de atendimento ao cliente.\n\n"
        "**Autenticação:** clique em **Authorize** e informe usuário e senha (o Swagger usa "
        "`POST /auth/token`). Por cliente HTTP, use `POST /auth/signin` e envie o "
        "`access_token` no header `Authorization: Bearer <token>`. "
        "Usuários de teste (seed): `alice`/`alice123` e `bruno`/`bruno123`."
    ),
    openapi_tags=[
        {"name": "sistema", "description": "Saúde da API."},
        {"name": "auth", "description": "Cadastro e login (JWT)."},
        {"name": "usuários", "description": "Dados do usuário autenticado."},
        {"name": "predições", "description": "Classificação de intenção e histórico (isolado por usuário)."},
    ],
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
configure_middlewares(app)
configure_rate_limiting(app)

# [ZAP Finding 4 - Vulnerable JS Library: DOMPurify 3.1.4 (Medium)]
# CORRIGIDO: static/swagger/ usa swagger-ui-dist 5.33.2 (antes 5.17.14).
# Ao atualizar o Swagger, o ZAP e o retire.js deixaram de reportar a vulnerabilidade.

@app.get("/docs", include_in_schema=False)
def swagger_docs() -> HTMLResponse:
    return HTMLResponse(
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        "<title>API - Docs</title>"
        "<link rel='stylesheet' href='/static/swagger/swagger-ui.css'>"
        "</head><body><div id='swagger-ui'></div>"
        "<script src='/static/swagger/swagger-ui-bundle.js'></script>"
        "<script src='/static/swagger/init.js'></script>"
        "</body></html>"
    )

app.include_router(api_router)
app.include_router(oauth_router)
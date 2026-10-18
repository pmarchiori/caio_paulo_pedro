from contextlib import asynccontextmanager

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from database.seed import seed
from middlewares import configure_middlewares
from rate_limit import configure_rate_limiting
from routers import api_router, oauth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    seed()
    yield

STATIC_DIR = Path(__file__).resolve().parent / "static"

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
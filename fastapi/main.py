from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

from database.seed import seed
from middlewares import configure_middlewares
from rate_limit import configure_rate_limiting
from routers import api_router, oauth_router
from security import get_current_user


@asynccontextmanager
async def lifespan(app: FastAPI):
    seed()
    yield

app = FastAPI(lifespan=lifespan)
configure_middlewares(app)
configure_rate_limiting(app)

@app.get("/me")
async def read_current_user(current_user: dict = Depends(get_current_user)):
    return current_user

app.include_router(api_router)
app.include_router(oauth_router)

from fastapi import FastAPI, Depends
from routers import api_router
from security import get_current_user
from routers import oauth_router


app = FastAPI()

@app.get("/me")
async def read_current_user(current_user: dict = Depends(get_current_user)):
    return current_user

app.include_router(api_router)
app.include_router(oauth_router)

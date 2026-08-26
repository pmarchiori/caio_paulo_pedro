from fastapi import APIRouter, Depends, HTTPException, status
from security import create_access_token, verify_password, hash_password
from fastapi.security import OAuth2PasswordRequestForm

oauth_router = APIRouter(prefix="/auth", tags=["auth"])

FAKE_USERS_DB = {
    "user1": {
        "username": "user1",
        "hashed_password": hash_password("senha123"),
    }
}


@oauth_router.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = FAKE_USERS_DB.get(form_data.username)

    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user["username"]})

    return {"access_token": access_token, "token_type": "bearer"}


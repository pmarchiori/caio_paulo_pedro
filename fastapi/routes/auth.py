from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from database import SessionDep
from models import SigninRequest, TokenResponse, User, UserCreate, UserRead
from rate_limit import limiter
from security import create_access_token, hash_password, verify_password

oauth_router = APIRouter(prefix="/auth", tags=["auth"])


def authenticate(session: SessionDep, username: str, password: str) -> TokenResponse:
    user = session.exec(select(User).where(User.username == username)).first()

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenResponse(access_token=create_access_token(data={"sub": user.username}))


@oauth_router.post(
    "/signup",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastra um novo usuário",
    description="Cria a conta. A senha é armazenada apenas como hash bcrypt. Limite: 5/minuto por IP.",
    responses={409: {"description": "Nome de usuário já existe."},
               422: {"description": "Dados inválidos."},
               429: {"description": "Limite de requisições excedido."}},
)
@limiter.limit("5/minute")
def signup(request: Request, payload: UserCreate, session: SessionDep):
    if session.exec(select(User).where(User.username == payload.username)).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Nome de usuário já existe")

    user = User(username=payload.username, hashed_password=hash_password(payload.password))
    session.add(user)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Nome de usuário já existe")
    session.refresh(user)
    return user


@oauth_router.post(
    "/signin",
    response_model=TokenResponse,
    summary="Autentica e retorna um token JWT",
    description="Login por JSON. Limite: 10/minuto por IP.",
    responses={401: {"description": "Usuário ou senha incorretos."},
               429: {"description": "Limite de requisições excedido."}},
)
@limiter.limit("10/minute")
def signin(request: Request, payload: SigninRequest, session: SessionDep):
    return authenticate(session, payload.username, payload.password)


@oauth_router.post(
    "/token",
    response_model=TokenResponse,
    summary="Login via formulário (uso interno do botão Authorize do Swagger)",
    responses={401: {"description": "Usuário ou senha incorretos."},
               429: {"description": "Limite de requisições excedido."}},
)
@limiter.limit("10/minute")
def login_for_access_token(
    request: Request,
    session: SessionDep,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    return authenticate(session, form_data.username, form_data.password)
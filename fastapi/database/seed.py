from sqlmodel import Session, select

from .sqlite_database import create_db_and_tables, engine
from models import Prediction, User
from security import hash_password

SEED_USERS = [
    {"username": "alice", "password": "alice123"},
    {"username": "bruno", "password": "bruno123"},
]

SEED_PREDICTIONS = {
    "alice": [
        ("Olá, tudo bem?", "saudacao", 0.97),
        ("Meu pedido chegou com defeito", "reclamacao", 0.91),
    ],
    "bruno": [
        ("Esse produto tem garantia?", "duvida_produto", 0.88),
        ("Obrigado, até mais!", "despedida", 0.95),
    ],
}


def seed() -> None:
    create_db_and_tables()

    with Session(engine) as session:
        users: dict[str, User] = {}

        for data in SEED_USERS:
            user = session.exec(
                select(User).where(User.username == data["username"])
            ).first()
            if user is None:
                user = User(
                    username=data["username"],
                    hashed_password=hash_password(data["password"]),
                )
                session.add(user)
                session.commit()
                session.refresh(user)
            users[user.username] = user

        for username, items in SEED_PREDICTIONS.items():
            owner = users[username]
            already = session.exec(
                select(Prediction).where(Prediction.owner_id == owner.id)
            ).first()
            if already is not None:
                continue
            for text, intent, confidence in items:
                session.add(
                    Prediction(
                        text=text,
                        intent=intent,
                        confidence=confidence,
                        owner_id=owner.id,
                    )
                )
        session.commit()


if __name__ == "__main__":
    seed()
    print("Seed concluído.")
from sqlmodel import Session, SQLModel, create_engine

import config

engine = create_engine(config.DATABASE_URL, echo=False)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    return Session(engine)

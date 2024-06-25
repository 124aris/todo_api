from fastapi import FastAPI, Depends
from app import settings
from sqlmodel import SQLModel, Field, create_engine, Session, select
from contextlib import asynccontextmanager
from typing import Annotated

class Todo(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: str

connection_string: str = str(settings.DATABASE_URL).replace("postgresql", "postgresql+psycopg")
engine = create_engine(connection_string)

def create_db_tables():
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_tables()
    yield

todo_api: FastAPI = FastAPI(lifespan = lifespan)

def get_session():
    with Session(engine) as session:
        yield session

@todo_api.get("/")
def hello():
    return {"Hello": "World"}

@todo_api.get("/db")
def db_var():
    return {"DB": settings.DATABASE_URL, "Connection": connection_string}

@todo_api.post("/todo")
def create_todo(todo_data: Todo, session: Annotated[Session, Depends(get_session)]):
    session.add(todo_data)
    session.commit()
    session.refresh(todo_data)
    return todo_data

@todo_api.get("/todo")
def get_all_todos(session: Annotated[Session, Depends(get_session)]):
    query = select(Todo)
    all_Todos = session.exec(query).all()
    return all_Todos


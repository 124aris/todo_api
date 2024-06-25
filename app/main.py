from fastapi import FastAPI, Depends
from app import settings
from sqlmodel import SQLModel, Field, create_engine, Session, select
from contextlib import asynccontextmanager
from typing import Annotated, Optional

class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str = Field(index=True)
    description: str

connection_string: str = str(settings.DATABASE_URL).replace("postgresql", "postgresql+psycopg")
engine = create_engine(connection_string, connect_args = {"sslmode": "require"}, pool_recycle = 300)

def create_db_tables():
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_tables()
    yield

todo_api = FastAPI(lifespan = lifespan, title = "Todo API", 
    version = "0.0.1",
    servers = [
        {
            "url": "http://127.0.0.1:8000",
            "description": "Development Server"
        }
    ]
)

def get_session():
    with Session(engine) as session:
        yield session

@todo_api.get("/")
def hello():
    return {"Hello": "World"}

@todo_api.post("/todo", response_model = Todo)
def create_todo(todo_data: Todo, session: Annotated[Session, Depends(get_session)]):
    session.add(todo_data)
    session.commit()
    session.refresh(todo_data)
    return todo_data

@todo_api.get("/todo", response_model = list[Todo])
def get_all_todos(session: Annotated[Session, Depends(get_session)]):
    query = select(Todo)
    all_Todos = session.exec(query).all()
    return all_Todos
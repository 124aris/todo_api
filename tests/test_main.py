from fastapi.testclient import TestClient
from app.main import todo_api, get_session
from sqlmodel import Session, SQLModel, create_engine
from app import settings

client = TestClient(app = todo_api)
connection_string = str(settings.DATABASE_URL).replace("postgresql", "postgresql+psycopg")
engine = create_engine(connection_string, connect_args = {"sslmode": "require"}, pool_recycle = 300)

def test_hello():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}

def test_create_todo():
    SQLModel.metadata.create_all(engine)  
    with Session(engine) as session:  
        def get_session_override():  
            return session  
        todo_api.dependency_overrides[get_session] = get_session_override
        todo_content = "buy bread"
        response = client.post("/todos", json = {"content": todo_content})
        data = response.json()
        assert response.status_code == 200
        assert data["content"] == todo_content

def test_get_all_todos():
    SQLModel.metadata.create_all(engine)  
    with Session(engine) as session:  
        def get_session_override():  
                return session  
        todo_api.dependency_overrides[get_session] = get_session_override 
        response = client.get("/todos")
        assert response.status_code == 200
import sys
import types
from unittest.mock import MagicMock

def create_mock_module(name, attrs=None):
    mod = types.ModuleType(name)
    if attrs:
        for attr_name, attr_value in attrs.items():
            setattr(mod, attr_name, attr_value)
    return mod

#Основные модули и их важные атрибуты/классы для моков
mocks = {
    # "torch": None,
    # "torch.nn": {"Module": MagicMock(name="Module")},
    # "torch.cuda": None,
    # "torchvision": None,
    # 'torch.nn.functional': None,
    # "torchvision.transforms": {
    #     "Compose": MagicMock(name="Compose"),
    #     "ToTensor": MagicMock(name="ToTensor"),
    #     "Normalize": MagicMock(name="Normalize"),
    #     "Resize": MagicMock(name="Resize"),
    #     "CenterCrop": MagicMock(name="CenterCrop"),
    #     "RandomHorizontalFlip": MagicMock(name="RandomHorizontalFlip")
    # },
    # "celery": {
    #     "Celery": MagicMock(name="Celery"),
    #     "shared_task": MagicMock(name="shared_task"),
    # },
    # "celery.result": {
    #     "AsyncResult": MagicMock(name="AsyncResult")
    # },
    "clearml": {
        "Task": MagicMock(name="Task"),
        "automation": create_mock_module("clearml.automation"),
        "backend_interface": create_mock_module("clearml.backend_interface", {
            "metrics": create_mock_module("clearml.backend_interface.metrics")
        })
    }
}

for mod_name, attrs in mocks.items():
    sys.modules[mod_name] = create_mock_module(mod_name, attrs)

nested_modules = [
    "clearml.automation",
    "clearml.backend_interface",
    "clearml.backend_interface.metrics",
    # "celery.result",
    # "torchvision.transforms",
    # "torch.nn",
    # "torch.cuda",
]

for nested_mod in nested_modules:
    if nested_mod not in sys.modules:
        sys.modules[nested_mod] = types.ModuleType(nested_mod)


import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool
from worker.celery_app import celery_app
import worker.tasks
print("Celery tasks:", celery_app.tasks.keys())
assert "worker.tasks.process_cnn_data_task" in celery_app.tasks
from main import app
from database.database import get_session

@pytest.fixture(scope="session", autouse=True)
def celery_eager():
    celery_app.conf.update(
        task_always_eager=True,
        task_eager_propagates=True,
    )

@pytest.fixture(name="session")
def session_fixture():
    """
    Фикстура создаёт отдельный in-memory SQLite-движок,
    сбрасывает и создаёт все таблицы, затем отдаёт Session.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """
    Фикстура создаёт TestClient(app), но переопределяет две зависимости:
      • get_session → возвращает нашу фикстурную in-memory-сессию
      • authenticate  → всегда возвращает "user@test.ru"
    """
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client

    app.dependency_overrides.clear()

from enum import Enum
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Response, status
from pydantic import BaseModel, Field


app = FastAPI(
    title="TaskFlow QA Target API",
    description="A synthetic REST API built specifically for an API QA and Postman portfolio demonstration.",
    version="1.0.0",
)

DEMO_TOKEN = "demo-token-qa-2026"
USERS = [
    {"id": 1, "name": "Samira El Idrissi", "email": "samira@example.test", "role": "admin"},
    {"id": 2, "name": "Omar Benali", "email": "omar@example.test", "role": "member"},
    {"id": 3, "name": "Nora Amrani", "email": "nora@example.test", "role": "member"},
]


class LoginRequest(BaseModel):
    email: str
    password: str = Field(min_length=8)


class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class TaskCreate(BaseModel):
    title: str = Field(min_length=3, max_length=80)
    priority: Priority = Priority.medium


class TaskResponse(BaseModel):
    id: int
    title: str
    priority: Priority
    status: str


def require_token(authorization: Annotated[str | None, Header()] = None) -> str:
    if authorization != f"Bearer {DEMO_TOKEN}":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing token")
    return authorization


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok", "version": app.version}


@app.post("/auth/login", tags=["authentication"])
def login(payload: LoginRequest) -> dict[str, str]:
    if payload.email != "qa@example.test" or payload.password != "qa-demo-2026":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return {"access_token": DEMO_TOKEN, "token_type": "bearer"}


@app.get("/users", dependencies=[Depends(require_token)], tags=["users"])
def list_users(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=50)] = 2,
) -> dict:
    start = (page - 1) * page_size
    end = start + page_size
    return {
        "items": USERS[start:end],
        "pagination": {"page": page, "page_size": page_size, "total": len(USERS)},
    }


@app.get("/users/{user_id}", dependencies=[Depends(require_token)], tags=["users"])
def get_user(user_id: int) -> dict:
    user = next((item for item in USERS if item["id"] == user_id), None)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@app.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_token)],
    tags=["tasks"],
)
def create_task(payload: TaskCreate) -> TaskResponse:
    return TaskResponse(id=101, title=payload.title, priority=payload.priority, status="open")


@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_token)],
    tags=["tasks"],
)
def delete_task(task_id: int) -> Response:
    if task_id != 101:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


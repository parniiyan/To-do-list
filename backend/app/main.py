from fastapi import FastAPI
from app.database import engine, Base
from app.routers import tasks, tags, auth

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Todo API",
    description="Backend API for Todo List Application",
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(tags.router)


@app.get("/")
def root():
    return {"message": "Todo API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}

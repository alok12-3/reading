# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Alembic: For production, you'd use Alembic to manage database migrations.
# For development, you might have a script or command to create tables initially.
# from .database import engine, create_db_and_tables # SQLModel.metadata.create_all(engine)
# The line above is commented out as per subtask requirements:
# "The main.py will rely on Alembic for table creation, not SQLModel.metadata.create_all(engine)."

from .api import passages, questions, vocab # Import your API routers
from .config import settings # If any settings are needed at app startup

# For development: Create tables if they don't exist.
# This is often handled by migration tools like Alembic in production.
# However, for simple local development or testing, it can be useful.
# The subtask states to rely on Alembic, so this should NOT be active by default.
# def lifespan(app: FastAPI):
#     print("FastAPI app startup: Checking/creating database tables...")
#     # create_db_and_tables() # This would create tables based on SQLModel definitions
#     # print("Database tables checked/created.")
#     yield
#     print("FastAPI app shutdown.")
# app = FastAPI(lifespan=lifespan) # Use lifespan for startup/shutdown events

app = FastAPI(
    title="Passage Analyzer API",
    description="API for managing passages, generating questions, and defining vocabulary.",
    version="0.1.0"
)

# CORS (Cross-Origin Resource Sharing) Middleware
# Allows requests from your frontend (running on a different port/domain)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Replace with your frontend URL in production for security
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"], # Allows all headers
)

# Include API routers
app.include_router(passages.router, prefix="/api/v1/passages", tags=["Passages"])
app.include_router(questions.router, prefix="/api/v1/questions", tags=["Questions & Answers"])
app.include_router(vocab.router, prefix="/api/v1/vocab", tags=["Vocabulary"])


@app.get("/api/v1/health", tags=["Health Check"])
async def health_check():
    """
    Simple health check endpoint.
    """
    return {"status": "ok", "message": "API is running"}

# Note on database initialization:
# The subtask specified that `main.py` will rely on Alembic for table creation.
# This means you should run `alembic upgrade head` (or similar) independently
# to set up your database schema before running the FastAPI application,
# especially in staging or production environments.
# The `create_db_and_tables()` function call (if it were active) would be
# more for initial local development convenience where migrations might be overkill
# for rapid prototyping.
#
# To run this application (after installing dependencies like uvicorn, fastapi, etc.):
# uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
#
# And ensure your .env file is correctly set up for DATABASE_URL and GOOGLE_API_KEY.

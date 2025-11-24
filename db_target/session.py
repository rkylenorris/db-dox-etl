from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
db_url_prefix = os.getenv("DB_URL_PREFIX")
db_username = os.getenv("DB_USERNAME")
db_password = os.getenv("DB_PASSWORD")
db_server = os.getenv("DB_SERVER")
db_name = os.getenv("DB_NAME")

# create connection string
CONNECTION_STRING = (
    f"{db_url_prefix}{db_username}:{db_password}@{db_server}/{db_name}"
    "?driver=ODBC+Driver+17+for+SQL+Server"
    "&TrustServerCertificate=yes"
)

# Create the SQLAlchemy engine and session factory
engine = create_engine(CONNECTION_STRING, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


# function to expose for getting a database session
def get_db_session() -> Session:
    """Get a new database session.
    Returns:
        Session: A new SQLAlchemy session.
    """
    return SessionLocal()

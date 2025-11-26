from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
db_url_prefix = os.getenv("DOX_DB_URL_PREFIX")
db_username = os.getenv("DOX_DB_USERNAME")
db_password = os.getenv("DOX_DB_PASSWORD")
db_server = os.getenv("DOX_DB_SERVER")
db_name = os.getenv("DOX_DB_NAME")
db_driver = os.getenv("DOX_DB_DRIVER")

# create connection string
CONNECTION_STRING = (
    f"{db_url_prefix}{db_username}:{db_password}@{db_server}/{db_name}"
    f"?driver={db_driver}"
    "&Encrypt=no&TrustServerCertificate=yes"
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


if __name__ == "__main__":
    with engine.connect() as connection:
        print("Database connection successful.")
        print(connection.execute(text("SELECT DB_NAME()")).scalar_one())

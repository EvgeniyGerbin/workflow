import dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from os import getenv
from dotenv import load_dotenv

# Load environment variables from a .env file.
load_dotenv()

# Construct the database URL from environment variables.

# SQLALCHEMY_DATABASE_URL = f"postgresql://{getenv('USERNAME')}:{getenv('PASSWORD')}@{getenv('HOST')}/{getenv('DATABASE')}"

SQLALCHEMY_DATABASE_URL = "postgresql://user:password@db/dbname"

# Create the SQLAlchemy engine with the database URL.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
)

# Create a session factory bound to the engine.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for declarative class definitions.
Base = declarative_base()

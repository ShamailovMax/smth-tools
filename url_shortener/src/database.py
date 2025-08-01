import os
from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, text
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv


load_dotenv()

DB_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

Base.metadata.schema = f"{os.getenv('DB_SCHEMA')}"

class URL(Base):
    __tablename__ = "urls"
    
    id = Column(Integer, primary_key=True)
    original_url = Column(Text, nullable=False)
    short_code = Column(String(10), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    clicks = Column(Integer, default=0)

def init_db():
    with engine.connect() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {os.getenv('DB_SCHEMA')}"))
        conn.commit()

        Base.metadata.create_all(engine)

if __name__ == '__main__':
    init_db()
    print("Database initialized!")
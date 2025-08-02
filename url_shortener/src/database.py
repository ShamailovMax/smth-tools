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

class URL(Base):
    __tablename__ = "urls"
    __table_args__ = {'schema': os.getenv('DB_SCHEMA')}
    
    id = Column(Integer, primary_key=True)
    original_url = Column(Text, nullable=False)
    short_code = Column(String(10), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    clicks = Column(Integer, default=0, nullable=False)

def init_db():
    with engine.connect() as conn:
        schema_name = os.getenv('DB_SCHEMA')
        if schema_name:
            conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
            conn.commit()

        Base.metadata.create_all(engine)

def fix_existing_data():
    with engine.connect() as conn:
        schema_name = os.getenv('DB_SCHEMA')
        table_name = f"{schema_name}.urls" if schema_name else "urls"
        
        conn.execute(text(f"UPDATE {table_name} SET clicks = 0 WHERE clicks IS NULL"))
        conn.commit()
        print("Fixed existing NULL clicks values")

if __name__ == '__main__':
    init_db()
    fix_existing_data()
    print("Database initialized and fixed!")
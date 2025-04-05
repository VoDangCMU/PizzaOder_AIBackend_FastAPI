from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.models import PizzaSale  
from dotenv import load_dotenv
import os

load_dotenv()

pg_user = os.getenv("PG_USER")
pg_password = os.getenv("PG_PASSWORD")
pg_host = os.getenv("PG_HOST")
pg_port = os.getenv("PG_PORT")
pg_database = os.getenv("PG_DATABASE")

DATABASE_URL = f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_database}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_select():
    db = SessionLocal()
    
    try:
        result = db.query(PizzaSale).limit(5).all()
        
        for row in result:
            print(f"Order ID: {row.order_id}, Pizza Name: {row.pizza_name}, Quantity: {row.quantity}, Total Price: {row.total_price}")
    except Exception as e:
        print(f"Error during select: {e}")
    finally:
        db.close()

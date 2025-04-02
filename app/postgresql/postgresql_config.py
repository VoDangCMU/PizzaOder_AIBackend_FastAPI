# app/models/postgresql_config.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.models import PizzaSale  # Đảm bảo bạn đang import đúng
from dotenv import load_dotenv
import os

# Tải các biến môi trường từ file .env
load_dotenv()

# Cấu hình kết nối PostgreSQL
pg_user = os.getenv("PG_USER")
pg_password = os.getenv("PG_PASSWORD")
pg_host = os.getenv("PG_HOST")
pg_port = os.getenv("PG_PORT")
pg_database = os.getenv("PG_DATABASE")

# Cấu hình URL kết nối PostgreSQL
DATABASE_URL = f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_database}"

# Khởi tạo kết nối và session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Hàm test SELECT
def test_select():
    # Tạo session để truy vấn dữ liệu từ PostgreSQL
    db = SessionLocal()
    
    try:
        # Truy vấn 5 dòng đầu tiên từ bảng pizza_sales
        result = db.query(PizzaSale).limit(5).all()
        
        # In kết quả
        for row in result:
            print(f"Order ID: {row.order_id}, Pizza Name: {row.pizza_name}, Quantity: {row.quantity}, Total Price: {row.total_price}")
    except Exception as e:
        print(f"Error during select: {e}")
    finally:
        # Đóng session sau khi truy vấn xong
        db.close()

# app/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class PizzaSale(Base):
    __tablename__ = "pizza_sales"

    order_id = Column(Integer, primary_key=True, index=True)
    pizza_name_id = Column(String, index=True)  # ID pizza
    pizza_name = Column(String)  # Tên pizza
    pizza_category = Column(String)  # Danh mục pizza
    pizza_ingredients = Column(String)  # Thành phần pizza
    order_date = Column(DateTime)  # Ngày đặt hàng
    order_time = Column(String)  # Thời gian đặt hàng
    quantity = Column(Float)  # Số lượng pizza
    unit_price = Column(Float)  # Giá đơn vị
    total_price = Column(Float)  # Tổng tiền
    pizza_size = Column(String)  # Kích thước pizza

    def __repr__(self):
        return f"<PizzaSale(order_id={self.order_id}, pizza_name={self.pizza_name}, quantity={self.quantity}, total_price={self.total_price})>"


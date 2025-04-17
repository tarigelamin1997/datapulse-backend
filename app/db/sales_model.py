from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(Date)
    item_name = Column(String)
    quantity = Column(Integer)
    unit_price = Column(Float)
    cost_price = Column(Float)

    user = relationship("User", back_populates="sales")

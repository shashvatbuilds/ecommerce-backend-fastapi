from app.database import Base
from sqlalchemy import Column,Integer,String,DateTime,Float
from sqlalchemy.orm import relationship
from datetime import datetime,timezone
from app.models.associations import product_categories

class Product(Base):
    __tablename__ ="products"
    id =Column(Integer,primary_key=True,index=True)
    name =Column(String,nullable=False,index=True)
    description =Column(String,nullable=True)
    price =Column(Float,nullable=False)
    stock = Column(Integer, nullable=False)
    created_at =Column(DateTime,default=lambda:datetime.now(timezone.utc))
    categories =relationship(
        "Category",
        secondary=product_categories,
        back_populates="products"
    )
    image_url = Column(String, nullable=True)


from sqlalchemy import (
    Column, Integer, String, Date, DateTime, Boolean, ForeignKey
)
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    login_id = Column(String(30), unique=True, nullable=False)
    username = Column(String(30), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    notification = Column(Boolean, nullable=False, default=True)

    items = relationship("Item", back_populates="user", cascade="all, delete-orphan")

class Item(Base):
    __tablename__ = "items"
    item_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.category_id", ondelete="CASCADE"), primary_key=True, index=True)
    item_name = Column(String(50), nullable=False)
    expiry_date = Column(Date)
    created_at = Column(DateTime, default=datetime, nullable=False)

    user = relationship("User", back_populates="items")
    category = relationship("Category", back_populates="items")

class Category(Base):
    __tablename__ = "categories"
    category_id = Column(Integer, primary_key=True, index=True)
    category_major_name = Column(String(30), nullable=False)
    category_sub_name = Column(String(30), nullable=False)

    items = relationship("Item", back_populates="categpru", cascade="all, delete-orphan")
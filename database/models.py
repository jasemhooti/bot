from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    balance = Column(Float, default=0)
    is_admin = Column(Boolean, default=False)
    is_banned = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    referrer_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    configs = relationship("Config", back_populates="user")
    tickets = relationship("Ticket", back_populates="user")
    games = relationship("Game", back_populates="user")

class Config(Base):
    __tablename__ = 'configs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String)
    link = Column(String)
    volume = Column(Integer)  # حجم به گیگابایت
    expiry_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="configs")
    usage_logs = relationship("UsageLog", back_populates="config")

class UsageLog(Base):
    __tablename__ = 'usage_logs'
    
    id = Column(Integer, primary_key=True)
    config_id = Column(Integer, ForeignKey('configs.id'))
    usage = Column(Float)  # مصرف به گیگابایت
    date = Column(DateTime, default=datetime.utcnow)
    
    config = relationship("Config", back_populates="usage_logs")

class Ticket(Base):
    __tablename__ = 'tickets'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    subject = Column(String)
    status = Column(String)  # open, closed
    created_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)
    
    user = relationship("User", back_populates="tickets")
    messages = relationship("TicketMessage", back_populates="ticket")

class TicketMessage(Base):
    __tablename__ = 'ticket_messages'
    
    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey('tickets.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    ticket = relationship("Ticket", back_populates="messages")

class Game(Base):
    __tablename__ = 'games'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    type = Column(String)  # single, multi
    bet_amount = Column(Float)
    result = Column(String)  # win, lose, draw
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="games")

class Plan(Base):
    __tablename__ = 'plans'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    volume = Column(Integer)  # حجم به گیگابایت
    duration = Column(Integer)  # مدت زمان به روز
    price = Column(Float)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Discount(Base):
    __tablename__ = 'discounts'
    
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True)
    percentage = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expiry_date = Column(DateTime, nullable=True) 
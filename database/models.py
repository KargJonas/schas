# models.py
from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(String(64), primary_key=True)               # We'll use Discord user ID as primary key
    calendar_link = Column(String(512), nullable=False)     # Link to the user's .ical file
    calendar_cache = Column(String(10000), nullable=True)   # Adjust size based on your needs
    cached_at = Column(DateTime, nullable=True)             # Date when the calendar was last cached

    def __repr__(self):
        return f'<User {self.id}>'

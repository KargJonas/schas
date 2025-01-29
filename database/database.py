from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.models import Base


class DatabaseManager:
    def __init__(self, db_url="sqlite:///database.db"):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        return self.Session()

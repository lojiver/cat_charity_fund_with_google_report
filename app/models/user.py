from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable

from app.core.db import Base
from sqlalchemy.orm import relationship


class User(SQLAlchemyBaseUserTable[int], Base):
    donations = relationship('Donation', cascade='delete')
from sqlalchemy import Column, String, Text

from app.core.db import PreProjectDonation
from sqlalchemy.orm import validates


class CharityProject(PreProjectDonation):
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text(1024), nullable=False)

    def __repr__(self):
        return (f'CharityProject(name={self.name}, '
                f'full_amount={self.full_amount})')

    @validates('description')
    def validate_description(self, key, desc):
        if len(desc) < 1:
            raise ValueError('Описание должно содержать не менее 1 символа')
        return desc

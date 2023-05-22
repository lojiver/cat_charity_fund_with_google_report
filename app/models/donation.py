from sqlalchemy import Column, ForeignKey, Integer, Text

from app.core.db import PreProjectDonation


class Donation(PreProjectDonation):
    user_id = Column(Integer, ForeignKey('user.id'))
    comment = Column(Text(1024))

    def __repr__(self):
        return (f'Donation(full_amount={self.full_amount}, '
                f'invested_amount={self.invested_amount})')

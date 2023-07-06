import typing as t

from db import db


class SubordinateModel(db.Model):
    __tablename__ = "subordinates"

    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.ForeignKey('users.account'), nullable=False)
    subordinate = db.Column(db.ForeignKey('users.account'), nullable=False)
    exist = db.Column(db.Boolean, nullable=False, default=True)

    dateUpdate = db.Column(db.DateTime, default=db.func.current_timestamp())

    @classmethod
    def find_by_account(cls, account: str) -> t.List['SubordinateModel']:
        return cls.query.filter_by(account=account).order_by().all()

    @classmethod
    def find_by_account_and_subordinate(cls, account: str, subordinate: str) -> 'SubordinateModel':
        return cls.query.filter_by(account=account, subordinate=subordinate).first()

    @classmethod
    def find_by_id(cls, _id: int) -> 'SubordinateModel':
        return cls.query.filter_by(id=_id).first()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()

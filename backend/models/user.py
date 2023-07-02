import typing as t

from db import db
from enums.user import UserCategoryEnum


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)  # sha256
    email = db.Column(db.String(100), nullable=True)
    category = db.Column(db.Enum(UserCategoryEnum), nullable=False)

    def __init__(self, account, password, email, category):
        self.account = account
        self.password = password
        self.email = email
        self.category = category

    @classmethod
    def find_by_account(cls, account: str) -> 'UserModel':
        return cls.query.filter_by(account=account).first()

    @classmethod
    def find_by_id(cls, _id: int) -> 'UserModel':
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_all_users(cls) -> t.List['UserModel']:
        return cls.query.all()

    @classmethod
    def reset_password(cls, account: str, password: str) -> None:
        user = cls.query.filter_by(account=account).first()
        user.password = password
        db.session.commit()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()

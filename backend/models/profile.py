import typing as t

from db import db


class ProfileModel(db.Model):
    __tablename__ = "profiles"

    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.ForeignKey('users.account'), nullable=False)
    updateUUID = db.Column(db.CHAR(36), nullable=False, unique=True)

    name = db.Column(db.String(100), nullable=True)
    gender = db.Column(db.String(100), nullable=True)
    birthday = db.Column(db.DateTime, nullable=True)
    diagnose = db.Column(db.String(100), nullable=True)
    stage = db.Column(db.String(100), nullable=True)
    dominantSide = db.Column(db.String(100), nullable=True)
    lded = db.Column(db.String(100), nullable=True)
    description = db.Column(db.String(200), nullable=True)

    dateUpload = db.Column(db.DateTime, default=db.func.current_timestamp())

    @classmethod
    def find_by_account(cls, account: str) -> t.List['ProfileModel']:
        return cls.query.filter_by(account=account).order_by(cls.dateUpload.desc()).all()

    @classmethod
    def find_latest_by_account(cls, account: str) -> t.List['ProfileModel']:
        return cls.query.filter_by(account=account).order_by(cls.dateUpload.desc()).first()

    @classmethod
    def find_by_updateUUID(cls, updateUUID: str) -> 'ProfileModel':
        return cls.query.filter_by(updateUUID=updateUUID).first()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()

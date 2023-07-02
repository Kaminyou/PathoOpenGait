import typing as t

from db import db


class ResultModel(db.Model):
    __tablename__ = "results"

    id = db.Column(db.Integer, primary_key=True)
    requestUUID = db.Column(db.ForeignKey('requests.submitUUID'), nullable=False)
    resultUUID = db.Column(db.CHAR(36), nullable=False)

    # model and data info
    resultKey = db.Column(db.String(100), nullable=False)
    resultValue = db.Column(db.String(100), nullable=False)
    resultType = db.Column(db.String(100), nullable=False)
    resultUnit = db.Column(db.String(100), nullable=False)

    createTime = db.Column(db.DateTime, default=db.func.current_timestamp())

    @classmethod
    def find_by_requestUUID(cls, requestUUID: str) -> t.List['ResultModel']:
        return cls.query.filter_by(requestUUID=requestUUID).all()

    @classmethod
    def find_by_resultUUID(cls, resultUUID: str) -> 'ResultModel':
        return cls.query.filter_by(resultUUID=resultUUID).first()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()

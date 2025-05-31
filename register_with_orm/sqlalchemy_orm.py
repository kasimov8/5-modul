from sqlalchemy import (create_engine, text, Column, Text, String, Integer, INT, CheckConstraint, BigInteger, select)
from sqlalchemy.orm import declarative_base, sessionmaker
from tabulate import tabulate

db_url = 'database.db'
engine = create_engine(f'sqlite:///file:{db_url}?mode=rwc&uri=true', echo=True)
Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    phone = Column(String(19), nullable=False, unique=True)
    chat_id = Column(BigInteger, unique=True)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.id}, {self.full_name!r}, {self.email}, {self.phone}, {self.chat_id})'

    # @property
    # def is_adult(self):
    #     return self.age >= 18
    #
    # @property
    # def greating(self):
    #     return f"Hello, {self.name}"
    #
    # @classmethod
    # def display(cls, session):
    #     users = session.query(cls).all()
    #     users = [(p, p.is_adult, p.greating) for p in users]
    #     header = ['Obyekt', 'is_adult', 'greating']
    #     print(tabulate(users, header, tablefmt='simple_grid'))
    #     return users

    @classmethod
    def select(cls):
        query = "SELECT chat_id FROM users"
        conn = engine.connect()
        datas = conn.execute(text(query))
        datas = [data[0] for data in datas]

        return datas

    def save(self, session):
        session.add(self)
        session.commit()

    @classmethod
    def save_all(cls, session, instances: list):
        session.add_all(instances)
        session.commit()

    @classmethod
    def delete(cls, session, chat_id):
        obj = session.query(cls).filter(chat_id == cls.chat_id).first()
        if obj:
            session.delete(obj)
            session.commit()

    @classmethod
    def get_by_id(cls, session, id_):
        return session.query(cls).filter(id_ == cls.id).first()

    # update
    @classmethod
    def update(cls, session, chat_id, data):
        obj = session.query(cls).filter(chat_id == cls.chat_id).first()
        data = data.split("=")
        print(data)
        if obj:
            if hasattr(obj, data[0]):
                setattr(obj, data[0], data[1])
            else:
                raise KeyError(f'`{cls.__name__}` class da  `{data[0]}` attribut mavjud emas!')
        session.commit()


Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()

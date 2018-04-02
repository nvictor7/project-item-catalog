from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)


class Technology(Base):
    __tablename__ = 'technology'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id,
        }


class Machine(Base):
    __tablename__ = 'machine'

    name = Column(String(100), nullable=False)
    id = Column(Integer, primary_key=True)
    manufacturer = Column(String(100))
    price = Column(String(8))
    feature = Column(String(600))
    technology_id = Column(Integer, ForeignKey('technology.id'))
    technology = relationship(Technology)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id,
            'manufacturer': self.manufacturer,
            'feature': self.feature,
        }


engine = create_engine('sqlite:///printingmachines.db')

Base.metadata.create_all(engine)

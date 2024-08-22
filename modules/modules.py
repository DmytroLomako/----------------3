from .settings import *

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key = True)
    full_name = Column(String)
    telegram_id = Column(Integer, unique = True)
    results = relationship('Results', back_populates = 'user')
    def __repr__(self):
        return f"Users(id={self.id}, full_name={self.full_name}, telegram_id={self.telegram_id})"
class Results(Base):
    __tablename__ = 'results'
    id = Column(Integer, primary_key = True)
    score = Column(Integer)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('Users', back_populates = 'results')
    def __repr__(self):
        return f"Results(id={self.id}, score={self.score}, user_id={self.user_id})"
Base.metadata.create_all(connection)
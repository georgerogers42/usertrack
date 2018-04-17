from os import environ
from contextlib import contextmanager
import arrow
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from passlib.hash import argon2

engine = create_engine(environ.get("DATABASE_URL", "postgres://localhost/users_dev"))

Session = sessionmaker(engine)

@contextmanager
def db_session():
    s = Session()
    try:
        yield s
    except:
        s.rollback()
        raise
    else:
        s.commit()
    finally:
        s.close()

Base = declarative_base(engine)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False, unique=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    ctime = Column(DateTime, nullable=False, default=lambda:arrow.get().datetime)
    def set_password(self, clearpass):
        self.password = argon2.hash(clearpass)
    def has_password(self, clearpass):
        return argon2.verify(clearpass, self.password)
    @property
    def full_name(self):
        return "%s %s" % (self.first_name, self.last_name)
    @property
    def to_line(self):
        return "%s <%s>" % (self.full_name, self.email)

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    from_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    from_user = relationship("User", backref="posts_from", foreign_keys=from_user_id)
    to_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    to_user = relationship("User", backref="posts_to", foreign_keys=to_user_id)
    title = Column(String, nullable=False)
    contents = Column(String, nullable=False)
    ctime = Column(DateTime, nullable=False, default=lambda:arrow.get().datetime)
    utime = Column(DateTime, nullable=False, default=lambda:arrow.get().datetime)

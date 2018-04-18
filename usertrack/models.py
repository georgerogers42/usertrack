from os import environ
from contextlib import contextmanager
import arrow
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from passlib.hash import argon2

engine = create_engine(environ.get("DATABASE_URL", "postgres://localhost/users_dev"), echo=True)

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

class ArrowTime(object):
    @property
    def arrow_ctime(self):
        return arrow.get(self.ctime)
    @property
    def arrow_utime(self):
        return arrow.get(self.utime)

class User(Base, ArrowTime):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False, unique=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    ctime = Column(DateTime, nullable=False, default=lambda:arrow.get().datetime)
    posts_from = relationship("Post", foreign_keys="Post.from_user_id", order_by="desc(Post.ctime)", back_populates="from_user")
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

class Post(Base, ArrowTime):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    from_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    from_user = relationship("User", foreign_keys=from_user_id, back_populates="posts_from")
    title = Column(String, nullable=False)
    contents = Column(String, nullable=False)
    ctime = Column(DateTime, nullable=False, default=lambda:arrow.get().datetime)
    utime = Column(DateTime, nullable=False, default=lambda:arrow.get().datetime)

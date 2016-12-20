#! -*- coding: utf-8 -*-
"""
针对sqlalchemy 的练习
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
import datetime


engine = create_engine('sqlite:///:memory:', echo=True)
Session = sessionmaker()
session = Session(bind=engine)

base = declarative_base()


class User(base):
    __tablename__ = "user"

    id = Column('uid', Integer, primary_key=True, autoincrement=True)
    name = Column(String(32), nullable=False)
    age = Column(Integer)
    password = Column(String(64))



    def __repr__(self):
        return "{0}(name={1}, age={2}, password={3})".format(self.__class__.__name__, self.name,
                                                                       self.age, self.password)

class Course(base):
    __tablename__ = 'course'

    id = Column('cid', Integer, primary_key=True, autoincrement=True)
    name = Column(String(32), nullable=False)
    score = Column(Integer, default=2, nullable=False)
    start_time = Column(DateTime, default=datetime.datetime.utcnow())



    def __repr__(self):
        return "{0}(name={1}, score={2}, start_time={3})".format(self.__class__.__name__, self.name,
                                                                           self.score, self.start_time)

class User2Course(base):
    __tablename__ = "user_course"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column('uid', Integer, ForeignKey(User.id), index=True)
    user_name = Column('uname', String, ForeignKey(User.name))
    course_id = Column('cid', Integer, ForeignKey(Course.id), index=True)
    course_name = Column('cname', String, ForeignKey(Course.name))
    select_time = Column(DateTime, default=datetime.datetime.utcnow())

    _user_id = relationship(User, primaryjoin='User.id == User2Course.user_id')
    _user_name = relationship(User, primaryjoin='User.name == User2Course.user_name')
    _course_id = relationship(Course, primaryjoin='Course.id == User2Course.course_id')
    _course_name = relationship(Course, primaryjoin='Course.name == User2Course.course_name')


    def __repr__(self):
        return "{0}(user_id={0}, user_name={1}, course_id={2},  course_name={3}, select_time={4})".format(self.user_id,
                                                                                                          self.user_name,
                                                                                                          self.course_id,
                                                                                                          self.course_name,
                                                                                                          self.select_time)

user1 = User(name='test1', age=10, password='test1')
user2 = User(name='test2', age=12, password='test2')
course1 = Course(name="english", score=4)
course2 = Course(name='chinese')


base.metadata.create_all(engine)

session.add(user1)
session.add(user2)
session.add(course1)
session.add(course2)

session.commit()

all_uid = [i for i in session.query(User)]
all_cid = [i for i in session.query(Course)]

for i in all_uid:
    for j in all_cid:
        u2c = User2Course()
        u2c.user_id = i.id
        u2c.user_name = i.name
        u2c.course_id = j.id
        u2c.course_name = j.name
        session.add(u2c)

session.commit()

for i in session.query(User2Course):
    print(i)
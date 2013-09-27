# -*- coding: utf-8 -*-
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Column, ForeignKey, MetaData
from sqlalchemy.types import String, Integer, Date
import settings

Base = declarative_base()
class User(Base):
    """Class which represents the users table"""
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), default='', nullable=True)
    email = Column(String(50), default='')

    def __repr__(self):
        """String representation of record while using print <instance>"""
        return "<User('%s: %s' - '%s')>" % (self.id, self.name, self.email)


class Appointment(Base):
    """Class which represents the appointments table
    This table is added after the first version and needs a schema migration for existing users.
    See
    - http://caneypuggies.alwaysreformed.com/wiki/DevelopingWithMigrations
    - http://packages.python.org/sqlalchemy-migrate/

    """
    __tablename__ = 'appointments'
    id = Column(Integer, primary_key=True)
    date = Column(Date())
    descr = Column(String(240))

    def __repr__(self):
        """String representation of record while using print <instance>"""
        return "<Appointment('%s: %s' - '%s')>" % (self.id, self.date.strftime(settings.DATESTRING), self.descr)


class Birthday(Base):
    """Class which represents the birthdays table"""
    __tablename__ = 'birthdays'
    id = Column(Integer, primary_key=True)
    date = Column(Date())
    descr = Column(String(240))

    def __repr__(self):
        """String representation of record while using print <instance>"""
        return "<Birthday('%s: %s' - '%s')>" % (self.id, self.date.strftime(settings.DATESTRING), self.descr)


class BirthdaySubscription(Base):
    """Class which represents the table birthday_subscriptions"""
    __tablename__ = 'birthday_subscriptions'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    birthday_id = Column(Integer, ForeignKey('birthdays.id'))


class SpecialDay(Base):
    """Class which represents the table special_days"""
    __tablename__ = 'special_days'
    id = Column(Integer, primary_key=True)
    date = Column(Date())
    descr = Column(String(240))

    def __repr__(self):
        """String representation of record while using print <instance>"""
        return "<Special day('%s: %s' - '%s')>" % (self.id, self.date.strftime(settings.DATESTRING), self.descr)


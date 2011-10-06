#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import argparse
import datetime
from email.mime.text import MIMEText
from email import Utils
import os
import time
import smtplib
from sqlalchemy import between, create_engine, engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import aliased
from sqlalchemy.orm.session import Session, sessionmaker
from sqlalchemy.schema import Column, ForeignKey, MetaData
from sqlalchemy.types import String, Integer, Date
import settings

__author__ = 'Nico den Boer'

class SpecialDays(object):
    """Class which handles the commands entered though the console

    Interesting links to find national holidays:

    The Netherlands:
    - http://www.feestdagen.nl

    Czech republic:
    - http://cs.wikipedia.org/wiki/Český_státní_svátek
    - http://www.doprava.vpraxi.cz/statni_svatky_evropa.html

    """
    is_open = False
    DATESTRING = '%d-%m-%Y'

    def _convert_date_string(self, date):
        """Internal method to convert a date string to a date object. If the format is incorrect, it will return None"""

        dt = None
        try:
            # http://docs.python.org/library/time.html#time.strptime
            tm = time.strptime(date, self.DATESTRING)
            dt = datetime.date(year=tm.tm_year, month=tm.tm_mon, day=tm.tm_mday)
        except TypeError, e:
            print e.args
            print 'Invalid date format. Please try again.'
        finally:
            return dt

    def _open_database(self):
        """Internal method to open the SQLite database. If the database does not exist yet, it will create it.
        Other methods can easily create a session after calling this method.

        """

        if self.is_open:
            return
        engine = create_engine('sqlite://' + settings.DATABASE_NAME, echo=settings.DATABASE_ECHO)
        self.Session = sessionmaker(bind=engine) # for creating the database
        if not settings.DATABASE_NAME:
            # for testing in memory
            Base.metadata.create_all(engine)
        elif settings.DATABASE_NAME and not os.path.exists(settings.DATABASE_NAME[1:]):
            # production use
            Base.metadata.create_all(engine)
        self.is_open = True
#        User.create(engine)
#        User.create(engine, checkfirst=True)
#        User.drop(engine, checkfirst=False)
#        Session.configure(bind=engine)  # once engine is available

    def _send_email(self, user_id, email):
        print 'Now processing %s' % email

        now = datetime.datetime.now()
        dt = datetime.date(year=now.year, month=now.month, day=now.day)
        date_from = dt - datetime.timedelta(days = settings.QUERY_FROM_DELTA)
        date_to = dt + datetime.timedelta(days = settings.QUERY_TO_DELTA)

        self._open_database()
        session = self.Session()

        # build query
        query_a = session.query(Birthday.date, Birthday.descr)
        query_a = query_a.filter(BirthdaySubscription.user_id==user_id)
        query_a = query_a.filter(Birthday.date.between(date_from, date_to))

        query_b = session.query(SpecialDay.date, SpecialDay.descr)
        query_b = query_b.filter(SpecialDay.date.between(date_from, date_to))

        query = query_a.union(query_b)
        query = query.order_by('1') # order by date column

        events = {}
        i = 0

        for record in query.all():
            i += 1
            dt = datetime.datetime(year=record.date.year, month=record.date.month, day=record.date.day)
            sort_field = dt.strftime('%Y%m%d-') + str(i)
            events[sort_field] = '%s - %s' % (dt.strftime(self.DATESTRING), record.descr)

        if not events:
            # nothing to do...
            return

        # note: Now sorted on date. Sorting on description would be sorted(events.iteritems())
        body = []
        for record in sorted(events):
            if settings.IS_TEST:
                print events[record]
            body.append(events[record])

        if settings.IS_TEST:
            email = settings.EMAIL_RECEIVER_TEST

        # Create email
        msg = MIMEText("\n".join(body))
        msg['Date'] = Utils.formatdate(localtime = 1)
        msg['Subject'] = settings.EMAIL_SUBJECT
        msg['From'] = settings.EMAIL_SENDER
        msg['To'] = email
        msg['Message-ID'] = Utils.make_msgid()
        # Send the message via our own SMTP server, but don't include the envelope header.
        s = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
        if settings.SMTP_TLS:
            s.ehlo()
            s.starttls()
            s.ehlo()
            s.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        s.sendmail(settings.EMAIL_SENDER, email, msg.as_string())
        s.quit()

        # Need a fake email server for testing? See http://www.lastcraft.com/fakemail.php

    def _update_data(self):
        """Update dates which are in the past, so they will reoccur in the future"""
        now = datetime.datetime.now()
        dt = datetime.date(year=now.year, month=now.month, day=now.day)
        date_to = dt - datetime.timedelta(days = settings.QUERY_FROM_DELTA)

        self._open_database()
        session = self.Session()

        # build query for birthdays and update data
        query = session.query(Birthday)
        query = query.filter(Birthday.date < date_to)
        for record in query.all():
            print record
            date_old = record.date
            date_new = datetime.date(year=now.year + 1, month=date_old.month, day=date_old.day)
            record.date = date_new
            session.add(record)

        # build query for special days and update data
        query = session.query(SpecialDay)
        query = query.filter(SpecialDay.date < date_to)
        for record in query.all():
            date_old = record.date
            date_new = datetime.date(year=now.year + 1, month=date_old.month, day=date_old.day)
            record.date = date_new
            session.add(record)

        session.commit()

    def add_user(self, name, email):
        """Method add a users.
         Pre-condition; required parameters. The command line parser has already validated that.

         """

        self._open_database()

        session = self.Session()

        user = User()
        user.name = name
        user.email = email # would normally be validated for a valid email address
        session.add(user)

        session.commit()
        for instance in session.query(User).filter_by(id=user.id).order_by(User.id):
            print 'Added: %s' % instance
#        session.rollback()
        pass

    def add_special_day(self, date, descr):
        """Method add a special day, which could be a national holiday or other days which are important to all.
         Pre-condition; required parameters. The command line parser has already validated that.

         """

        self._open_database()
        dt = self._convert_date_string(date)
        if not dt:
            return

        session = self.Session()

        day = SpecialDay()
        day.date = dt
        day.descr = descr
        session.add(day)

        session.commit()
        for instance in session.query(SpecialDay).filter_by(id=day.id).order_by(SpecialDay.id):
            print 'Added: %s' % instance

    def add_birthday(self, date, descr, users):
        """Method add a birthday, which is relevant for specified users only.
         Pre-condition; required parameters. The command line parser has already validated that.

         """

        self._open_database()
        dt = self._convert_date_string(date)
        if not dt:
            return

        session = self.Session()

        # add birthday itself
        day = Birthday()
        day.date = dt
        day.descr = descr
        session.add(day)

        # need to commit here, because otherwise the record has no ID yet. Which we need for related records.
        session.commit()

        # add some related records
        records = users.split(',')
        for user in records:
            record = BirthdaySubscription()
            record.user_id = user
            record.birthday_id = day.id
            session.add(record)

        session.commit()

        for instance in session.query(Birthday).filter_by(id=day.id).order_by(Birthday.id):
            print 'Added: %s' % instance

        print 'Subscriptions for birthday ID %s:' % day.id
        for dy, usr in session.query(BirthdaySubscription, User).filter(BirthdaySubscription.user_id==User.id).filter_by(birthday_id=day.id).order_by(User.id):
            # used  "direct join" or 'Cartesian product' here.
            print 'ID %d for user %s' % (dy.id, usr.name)

    def edit_birthday(self, id):
        self._open_database()
        session = self.Session()
        birthday = session.query(Birthday).filter_by(id=id).first()
        if not birthday:
            print 'Birthday does not exist. Check ID and try again'
            return

        # Check if we can continue
        print 'You are going to edit the following record:'
        print birthday
        print 'What would you now like to do?'
        print 'Press e to edit, d to delete and q to quit (e/d/q)'
        user_input = raw_input()
        if user_input == 'e':
            # Get and validate user input
            dt = datetime.datetime(year=birthday.date.year, month=birthday.date.month, day=birthday.date.day)
            old_date = dt.strftime(self.DATESTRING)

            print 'Current value: %s ' % old_date
            new_date = self._convert_date_string(raw_input('$ '))
            if not new_date:
                new_date = birthday.date

            print 'Current value: %s ' % birthday.descr
            new_desc = raw_input('$ ')
            if not new_desc:
                new_desc = birthday.descr

            # Store information
            birthday.date = new_date
            birthday.descr = new_desc
            session.add(birthday)
        elif user_input == 'd':
            session.delete(birthday)
            # delete cascade - delete related records too
            session.execute('DELETE FROM birthday_subscriptions WHERE birthday_id=:id', {'id': id})
        else:
            return

        session.commit()

    def edit_special_day(self, id):
        self._open_database()
        session = self.Session()
        special_day = session.query(SpecialDay).filter_by(id=id).first()
        if not special_day:
            print 'Special day does not exist. Check ID and try again'
            return

        # Check if we can continue
        print 'You are going to edit the following record:'
        print special_day
        print 'What would you now like to do?'
        print 'Press e to edit, d to delete and q to quit (e/d/q)'
        user_input = raw_input()
        if user_input == 'e':
            # Get and validate user input
            dt = datetime.datetime(year=special_day.date.year, month=special_day.date.month, day=special_day.date.day)
            old_date = dt.strftime(self.DATESTRING)

            print 'Current value: %s ' % old_date
            new_date = self._convert_date_string(raw_input('$ '))
            if not new_date:
                new_date = special_day.date

            print 'Current value: %s ' % special_day.descr
            new_desc = raw_input('$ ')
            if not new_desc:
                new_desc = special_day.descr

            # Store information
            special_day.date = new_date
            special_day.descr = new_desc
            session.add(special_day)
        elif user_input == 'd':
            session.delete(special_day)
        else:
            return

        session.commit()

    def edit_user(self, id):
        self._open_database()
        session = self.Session()
        user = session.query(User).filter_by(id=id).first()
        if not user:
            print 'User does not exist. Check ID and try again'
            return

        # Check if we can continue
        print 'You are going to edit the following record:'
        print user
        print 'What would you now like to do?'
        print 'Press e to edit, d to delete and q to quit (e/d/q)'
        user_input = raw_input()
        if user_input == 'e':
            # Get and validate user input
            print 'Current value: %s ' % user.name
            new_name = raw_input('$ ')
            if not new_name:
                new_name = user.name
            print 'Current value: %s ' % user.email
            new_email = raw_input('$ ')
            if not new_email:
                new_email = user.email
            # Store information
            user.name = new_name
            user.email = new_email
            session.add(user)
        elif user_input == 'd':
            session.delete(special_day)
            # delete cascade - delete related records too
            session.execute('DELETE FROM birthday_subscriptions WHERE users_id=:id', {'id': id})
        else:
            return

        session.commit()

    def list_users(self):
        self._open_database()
        session = self.Session()
        for record in session.query(User).order_by(User.id):
            print record

    def list_birthdays(self, subscriptions):
        self._open_database()
        session = self.Session()
        for record in session.query(Birthday).order_by(Birthday.date):
            print record
            if not subscriptions:
                continue
            print '- Subscriptions:'
            for dy, usr in session.query(BirthdaySubscription, User).filter(BirthdaySubscription.user_id==User.id).filter_by(birthday_id=record.id).order_by(User.id):
                # used  "direct join" or 'Cartesian product' here.
                print '  ID %d for user %s' % (dy.id, usr.name)

    def list_special_days(self):
        self._open_database()
        session = self.Session()
        for record in session.query(SpecialDay).order_by(SpecialDay.date):
            print record

    def add_subscription(self, user_id, birthday_id):
        self._open_database()
        session = self.Session()

        record = BirthdaySubscription()
        record.user_id = user_id
        record.birthday_id = birthday_id
        session.add(record)

        session.commit()

    def delete_subscription(self, id):
        self._open_database()
        session = self.Session()
        record = session.query(BirthdaySubscription).filter_by(id=id).first()
        if not record:
            print 'Birthday does not exist. Check ID and try again'
            return

        session.delete(record)
        session.commit()

    def send_emails(self):
        self._open_database()
        session = self.Session()
        for record in session.query(User).all():
            self._send_email(record.id, record.email)
        self._update_data()


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


class Birthday(Base):
    """Class which represents the birthdays table"""
    __tablename__ = 'birthdays'
    id = Column(Integer, primary_key=True)
    date = Column(Date())
    descr = Column(String(240))

    def __repr__(self):
        """String representation of record while using print <instance>"""
        return "<Birthday('%s: %s' - '%s')>" % (self.id, self.date.strftime(SpecialDays.DATESTRING), self.descr)


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
        return "<Special day('%s: %s' - '%s')>" % (self.id, self.date.strftime(SpecialDays.DATESTRING), self.descr)


def main():
    descr = []
    descr.append('A little program to remind you of special days; birthdays and other special days.')
    descr.append('Birthdays are connected to specific users. Special days are global and relevant for all users.')

    parser = argparse.ArgumentParser(prog='special_days', description="\n".join(descr))
    subparsers = parser.add_subparsers(dest = 'command')

    cmd = subparsers.add_parser('add-user', help='Add a user')
    cmd.add_argument('name', help='<First name> <last name>')
    cmd.add_argument('email', help='Valid please')

    cmd = subparsers.add_parser('add-special-day', help='Add a national holiday')
    cmd.add_argument('date', help='Format: dd-mm-yyyy')
    cmd.add_argument('description', help='Description of national holiday')

    cmd = subparsers.add_parser('add-birthday', help='Add a birthday')
    cmd.add_argument('date', help='Format: dd-mm-yyyy')
    cmd.add_argument('description', help='Name of person')
    cmd.add_argument('users', help='ID of user - or comma delimited list of users - who should receive an email')

    cmd = subparsers.add_parser('add-subscription', help='Add a subscription to a birthday')
    cmd.add_argument('user_id', help='ID of user')
    cmd.add_argument('birthday_id', help='ID of birthday')

    # if you just want to check if an option is entered (will store a bool value to the option):
#    cmd.add_argument('--display-processed', action = 'store_true')

    cmd = subparsers.add_parser('edit-user', help='Edit a user')
    cmd.add_argument('id', help='ID of user')

    descr = []
    descr.append('Edit a birthday. ')
    descr.append('You need to provide user ID(\'s) for user(s) who need to be reminded by email')
    cmd = subparsers.add_parser('edit-birthday', help="\n".join(descr))
    cmd.add_argument('id', help='ID of birthday')

    cmd = subparsers.add_parser('edit-special-day', help='Edit a special day')
    cmd.add_argument('id', help='ID of special day')

    cmd = subparsers.add_parser('delete-subscription', help='Delete a subscription to a birthday')
    cmd.add_argument('id', help='ID of subscription')

    cmd = subparsers.add_parser('list-users', help='List users')

    cmd = subparsers.add_parser('list-birthdays', help='List birthdays')
    cmd.add_argument('--subscriptions', help='Include subscriptions', action = 'store_true')

    cmd = subparsers.add_parser('list-special-days', help='List special days')

    cmd = subparsers.add_parser('send-emails', help='Send emails to users')
    cmd.add_argument('--user_id', help='ID of user')

    args = parser.parse_args()

    cls = SpecialDays()

    if settings.INSERT_TEST_DATA and not settings.DATABASE_NAME:
        # some data to test the list and exit commands from the console or the pycharm debugger
        print '-- begin insertion test data --'
        cls.add_user('Pietje Puk', 'pietje@puk.com')
        cls.add_user('Kees Janssen', 'kees@janssen.com')
        cls.add_birthday('28-01-2011', 'Pietje Puk', '1,2')
        cls.add_special_day('15-04-2011', 'National event, something important')
        print "-- end insertion test data --\n\n"

    if args.command == 'add-user':
        cls.add_user(args.name, args.email)
    elif args.command == 'add-birthday':
        cls.add_birthday(args.date[:-1], args.description, args.users)
    elif args.command == 'add-special-day':
        cls.add_special_day(args.date, args.description)
    elif args.command == 'add-subscription':
        cls.add_subscription(int(args.user_id), int(args.birthday_id))
    elif args.command == 'delete-subscription':
        cls.delete_subscription(int(args.id))
    elif args.command == 'edit-birthday':
        cls.edit_birthday(int(args.id))
    elif args.command == 'edit-special-day':
        cls.edit_special_day(int(args.id))
    elif args.command == 'edit-user':
        cls.edit_user(int(args.id))
    elif args.command == 'list-users':
        cls.list_users()
    elif args.command == 'list-birthdays':
        cls.list_birthdays(args.subscriptions)
    elif args.command == 'list-special-days':
        cls.list_special_days()
    elif args.command == 'send-emails':
        cls.send_emails()

if __name__ == '__main__':
    main()

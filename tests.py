#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
__author__ = 'Nico den Boer'

import unittest
import main

class TestFunctions(unittest.TestCase):
    def setUp(self):
        pass

    def test_add_records(self):
        cls.add_user('Pietje Puk', 'pietje@puk.com')
        cls.add_user('Kees Janssen', 'kees@janssen.com')
        cls.add_birthday('28-01-2011', 'Pietje Puk', '1,2')
        cls.add_special_day('15-04-2011', 'National event, something important')

    def test_list_tables(self):
        cls.list_users()
        cls.list_birthdays()
        cls.list_special_days()

    def test_update_data(self):
        cls.send_emails()
        cls.list_birthdays()
        cls.list_special_days()


"""
For manual testing:

./main.py add-user 'Pietje Puk' 'pietje@puk.com'
./main.py add-user 'Pietje Puk' 'pietje@puk.com'
./main.py list-users 'Pietje Puk' 'pietje@puk.com'

#cls.edit_birthday(args.id)
#cls.add_national_holiday(args.id)
#cls.add_user(args.id)

TODO check how to test raw input

"""
if __name__ == '__main__':
    cls = main.SpecialDays()
    unittest.main()
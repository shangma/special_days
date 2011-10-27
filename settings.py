#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import os

DATABASE_ECHO = False
DATABASE_NAME = '' # in-memory
# DATABASE_NAME = '/%s/data.sq3' % os.path.abspath(os.path.dirname(__file__)) # physical file
DATESTRING = '%d-%m-%Y'
EMAIL_SENDER = 'me@myserver.com'
EMAIL_RECEIVER_TEST = 'you@server.com'
EMAIL_SUBJECT = 'Upcoming important days'
INSERT_TEST_DATA = False
IS_TEST = False
QUERY_FROM_DELTA = 5
QUERY_TO_DELTA = 30
SMTP_PORT = None
SMTP_SERVER = 'localhost'
SMTP_USER = None
SMTP_PASSWORD = None
SMTP_TLS = False

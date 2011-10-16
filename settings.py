#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import os

DATABASE_ECHO = False
#DATABASE_NAME = '' # in-memory
DATABASE_NAME = '/%s/data.sq3' % os.path.abspath(os.path.dirname(__file__))
DATESTRING = '%d-%m-%Y'
EMAIL_SENDER = 'nico@nicodenboer.com'
EMAIL_RECEIVER_TEST = None
EMAIL_SUBJECT = 'Komende verjaardagen en feestdagen'
INSERT_TEST_DATA = False
IS_TEST = True
QUERY_FROM_DELTA = 5
QUERY_TO_DELTA = 30
SMTP_PORT = '2525'
SMTP_SERVER = 'vps7553.mod4u.org'
SMTP_USER = 'nico@nicodenboer.com'
SMTP_PASSWORD = 'v170192v'
SMTP_TLS = True

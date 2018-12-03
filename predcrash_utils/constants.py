# coding: utf-8
"""
.. module:: albator_utils.constants
Constants module for albator utilities
"""

__author__ = "Axel Marchand"

# Globals
###############################################################################

# Redis store
SET = "set"
GET = "get"
API_CONFIGURATION = "api_configuration"
REDIS_URL = "redis_url"
PG_DSN = "pg_dsn"
SQL_ROOT = "sql_root"
CSV_ROOT = "csv_root"

# MAILJET constants
MAILJET_API_MAIL = 'MAILJET_API_MAIL'
MAILJET_API_NAME = 'MAILJET_API_NAME'
MAILJET_API_KEY = 'MAILJET_API_KEY'
MAILJET_API_SECRET = 'MAILJET_API_SECRET'

# Sentry constants
SENTRY_LOG_ACTIVATED = False
SENTRY_DSN = "SENTRY_DSN"
SENTRY_ACTIVATED = 'SENTRY_ACTIVATED'


# smtplib constants to send mail with attachments
SMTP_MAIL = "grille.albator@gmail.com"
SMTP_PASS = "cipwuk-xaQjac-0bajke"
SMTP_HOST = "smtp.gmail.com"


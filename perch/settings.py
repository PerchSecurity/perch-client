import os

PERCH_ENV = os.environ.get('PERCH_ENV', 'prod')

ROOT_URL = 'https://api.perch.rocks/v1'
if PERCH_ENV == 'qa':
    ROOT_URL = 'https://api.qa.perch.rocks/v1'
if PERCH_ENV == 'dev':
    ROOT_URL = 'http://api.local.perchsecurity.com/v1'

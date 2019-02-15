import os

# Suppress warnings in python2
import warnings
warnings.filterwarnings("ignore")


PERCH_ENV = os.environ.get('PERCH_ENV', 'PROD')

ROOT_URL = 'https://api.perch.rocks/v1'
if PERCH_ENV == 'QA':
    ROOT_URL = 'https://api.qa.perch.rocks/v1'
if PERCH_ENV == 'DEV':
    ROOT_URL = 'https://api.local.perchsecurity.com/v1'

INDICATOR_CHUNK_SIZE = 350

PYPI_URL = 'https://pypi.org/pypi/perch/json'

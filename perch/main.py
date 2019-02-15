from __future__ import unicode_literals

import click
import csv
import json
import requests
import sys
import unicodecsv


from .settings import INDICATOR_CHUNK_SIZE, PERCH_ENV, PYPI_URL, ROOT_URL
from .version import __version__


COLUMNS = {
    'title': 0,
    'tlp': 2,
    'description': 1,
    'confidence': 3,
    'observable_type': 4,
    'observable_value': 5,
    'observable_file_hash': 6
}

TLP = {
    'WHITE': 0,
    'GREEN': 1,
    'AMBER': 2,
    'RED': 3,
}

CONFIDENCE = {
    'LOW': 0,
    'MEDIUM': 1,
    'HIGH': 2,
}

FILE_HASH_TYPES = {
    'MD5': 0,
    'SHA1': 1,
    'SHA224': 2,
    'SHA256': 3
}


def check_version(ctx):
    # Don't bother checking in dev mode
    if PERCH_ENV == 'DEV':
        return True

    res = requests.get(PYPI_URL)

    # In case PyPi is down we don't want to halt
    if res.status_code != 200:
        return True

    pypi_info = res.json()
    latest_version = pypi_info['info']['version']

    versions_match = __version__ == latest_version

    if not versions_match:
        message = 'Your perch client is out of date! Please upgrade your client using:\r\n\r\n    pip install perch -U\r\n'
        click.echo(message=message, err=True)
        ctx.abort()

    return versions_match


def get_observable_type(reported_type):
    reported_type = reported_type.lower()
    if 'ip' in reported_type:
        return 0
    if 'domain' in reported_type:
        return 1
    if 'url' in reported_type or 'http uri' in reported_type:
        return 2
    if 'regex' in reported_type:
        return 3
    if 'file' in reported_type:
        return 4
    return False


def get_observable_value(obs_type, row):
    if obs_type == 2:
        value = row[COLUMNS['observable_value']]
        return value.strip().split(' ')[-1]
    return row[COLUMNS['observable_value']]


def get_hash_type(row):
    try:
        hash_type = row[COLUMNS['observable_file_hash']]
    except IndexError:
        hash_type = None

    if hash_type:
        try:
            return FILE_HASH_TYPES[hash_type.upper()]
        except KeyError:
            return False

    file_hash = row[COLUMNS['observable_value']]
    hash_len = len(file_hash)
    if hash_len == 32: #MD5
        return 0
    if hash_len == 40: #SHA1
        return 1
    if hash_len == 56: #SHA224
        return 2
    if hash_len == 64: #SHA256
        return 3
    return False


def readrows(indicator_file):
    if sys.version_info[0] < 3:
        rows = unicodecsv.reader(indicator_file, dialect=csv.excel_tab, delimiter=b',', quotechar=b'"')
    else:
        rows = csv.reader(indicator_file, dialect=csv.excel_tab, delimiter=',', quotechar='"')
    for row in rows:
        yield row


def validate_csv(ctx, indicator_file):
    if not indicator_file.name.endswith('.csv'):
        click.echo('ERROR: {} is not a CSV file!'.format(indicator_file.name))
        ctx.abort()


def build_indicator(row, company_id=None, communities=[]):
    observable_type = get_observable_type(row[COLUMNS['observable_type']])
    if observable_type is False:
        return None, 'Invalid observable type'
    observable_value = get_observable_value(observable_type, row)
    if not observable_value:
        return None, 'No observable value found'

    tlp_key = row[COLUMNS['tlp']]
    try:
        tlp = TLP[tlp_key.upper()]
    except KeyError:
        return None, '"{}" is not a valid TLP option. Options are: {}, {}, {}'.format(tlp_key, *TLP.keys())

    confidence_key = row[COLUMNS['confidence']]
    try:
        confidence = CONFIDENCE[confidence_key.upper()]
    except KeyError:
        return None, '"{}" is not a valid Confidence option. Options are: {}, {}, {}'.format(confidence_key, *CONFIDENCE.keys())

    indicator = {
        'title': row[COLUMNS['title']],
        'tlp': tlp,
        'description': row[COLUMNS['description']],
        'confidence': confidence,
        'observables': [{
            'type': observable_type,
            'details': {'value': observable_value}
        }],
        'communities': [{'id': int(com_id)} for com_id in communities],
        'company_id': company_id if company_id else None
    }

    if indicator['observables'][0]['type'] == 4:
        hash_type = get_hash_type(row)
        if hash_type is False:
            return None, 'Unable to detect file hash type'
        indicator['observables'][0]['details']['hash'] = hash_type
    return indicator, None


def authenticate(ctx, api_key, username, password):
    headers = {'Content-Type': 'application/json', 'x-api-key': api_key}
    req_body = json.dumps({'username': username, 'password': password})
    url = ROOT_URL + '/auth/access_token'
    res = requests.post(url, data=req_body, headers=headers)
    if not res.status_code == 200:
        click.echo('Your username or password or api key is not correct!')
        ctx.abort()
    res_body = res.json()
    headers['Authorization'] = 'Bearer ' + res_body['access_token']
    return headers


def prompt_for_communities(ctx, headers):
    url = ROOT_URL + '/communities'
    res = requests.get(url, headers=headers)
    if not res.status_code == 200:
        click.echo('API ERROR: {}'.format(res.text))
        ctx.abort()
    communities = res.json()['results']
    msg = 'Please enter the community id\'s that you want to share with separated by a comma: \n'
    for community in communities:
        msg += '{id}: {name} \n'.format(**community)
    community_ids = click.prompt(msg, type=str)
    return community_ids.split(',')


@click.group()
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx):
    check_version(ctx)
    pass


@cli.command()
@click.argument('indicator_file', type=click.File('rU'))
@click.option('--api_key', type=click.STRING, prompt=True)
@click.option('--username', type=click.STRING, prompt=True)
@click.option('--password', type=click.STRING, prompt=True)
@click.pass_context
def upload_indicators_csv(ctx, indicator_file, api_key, username, password):
    headers = authenticate(ctx, api_key, username, password)
    validate_csv(ctx, indicator_file)
    community_ids = prompt_for_communities(ctx, headers)
    req_bodies = []
    bad_rows = []
    chunk = []

    for index, row in enumerate(readrows(indicator_file)):
        indicator, error_message = build_indicator(row, communities=community_ids)
        if indicator:
            chunk.append(indicator)
            if len(chunk) >= INDICATOR_CHUNK_SIZE:
                req_bodies.append(chunk)
                chunk = []
        else:
            bad_rows.append({'row': index + 1, 'reason': error_message, 'data': row})

    if chunk:
        req_bodies.append(chunk)

    if bad_rows:
        msg = 'The following rows are not valid: \n'
        for bad_row in bad_rows:
            msg = '{row}: {reason} \n'.format(**bad_row)
        msg += 'Do you want to continue anyway?'
        click.confirm(msg, abort=True)

    click.echo('Uploading...')
    url = ROOT_URL + '/indicators'

    # TODO: Make this use a progress bar. Click has support.
    for req_body in req_bodies:
        res = requests.post(url, data=json.dumps(req_body), headers=headers)
        """ TODO: This creates a bad scenario where if the first chunk is successful, and a subsequent chunk fails,
         it prompts the user to fix it and re-upload, which will result in duplication of the first chunk. I don't know
         how to fix this easily. The endpoint should probably accept and validate all the data, respond, and then queue
         a job to INSERT the data into the db in the background.
        """
        if res.status_code == 400:
            click.echo('Upload failed. Please correct the following rows and try again. \n\n {}'.format(res.text))
            ctx.abort()
        if res.status_code != 201:
            click.echo('Server Error: {}'.format(res.status_code))
            ctx.abort()
        click.echo('Working...')

    click.echo('Upload Successful!')

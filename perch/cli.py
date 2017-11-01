import json
import click

from perch import PerchAPIClient


ROOT_URL = 'http://api.local.perchsecurity.com'

COMPANY_ID = 1

COMMUNITIES = (
    '16', #MPSISAO dev
    '29', #MPSISAO
)

COLUMNS = {
    'id': 0,
    'title': 6,
    'tlp': 7,
    'description': 3,
    'confidence': 9,
    'observable_type': 5,
    'observable_value': 1,
    'observable_file_hash': 2
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


def get_observable_type(reported_type):
    reported_type = reported_type.lower()
    if 'ip ' in reported_type:
        return 0
    if 'domain' in reported_type:
        return 1
    if 'url' in reported_type:
        return 2
    if 'file' in reported_type:
        return 4
    return False


def get_observable_value(obs_type, row):
    if obs_type == 4:
        return row[COLUMNS['observable_file_hash']]
    return row[COLUMNS['observable_value']]


def get_hash_type(file_hash):
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


@click.command()
@click.argument('csv', type=click.File('rb'))
@click.option('--username', type=click.STRING, prompt=True)
@click.option('--password', type=click.STRING, prompt=True)
@click.option('--communities', type=click.Choice(COMMUNITIES), prompt="Enter the ids of communities to share with seperated by a comma")
def cli(csv, username, password, communities):
    perch = PerchAPIClient(username=username, password=password, root_url=ROOT_URL)
    skipped_rows = []
    successful_rows = []
    for row in csv:
        row = row.decode('utf-8').rstrip('\r\n').split(',')
        observable_type = get_observable_type(row[COLUMNS['observable_type']])
        if observable_type is False:
            skipped_rows.append({'reason': 'Invalid observable type', 'data': row})
            continue
        observable_value = get_observable_value(observable_type, row)
        if not observable_value:
            skipped_rows.append({'reason': 'No observable value found', 'data': row})
            continue
        indicator = {
            'title': row[COLUMNS['title']],
            'tlp': TLP[row[COLUMNS['tlp']]],
            'description': row[COLUMNS['description']],
            'confidence': CONFIDENCE[row[COLUMNS['confidence']]],
            'observables': [{
                'type': observable_type,
                'details': {'value': observable_value}
            }],
            'communities': [{'id': int(com_id)} for com_id in communities.split(',')],
            'company_id': COMPANY_ID,
        }

        if indicator['observables'][0]['type'] == 4:
            hash_type = get_hash_type(indicator['observables'][0]['details']['value'])
            if hash_type is False:
                skipped_rows.append({'reason': 'Unable to detect file hash type', 'data': row})
                continue
            indicator['observables'][0]['details']['hash'] = hash_type

        perch.indicators.create(**indicator)
        successful_rows.append(row)

    error_report = '{}\n {} records could not be loaded. See list above for reasons.'.format(
        json.dumps(skipped_rows, indent=2),
        len(skipped_rows)
    )
    click.echo(error_report)
    click.echo('{} records successfully added'.format(len(successful_rows)))

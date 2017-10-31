import os
import json
import click
import six

from perch import PerchAPIClient


INDICATOR_UPLOAD_CONFIG_FILENAME = 'indicator-upload-{}.json'


def read_config(filename):
    with open('config/{}'.format(filename), 'rb') as config_file:
        return json.loads(config_file.read())


def write_config(filename, config):
    with open('config/{}'.format(filename), 'wb') as config_file:
        config_file.write(json.dumps(config, indent=2, sort_keys=True))


def get_config_filename(csv_name):
    return INDICATOR_UPLOAD_CONFIG_FILENAME.format(csv_name.split('.')[0])


def get_user_communities():
    return []


def parse_row_to_indicator(config, row):
    indicator = {k: row[v - 1] for k, v in six.iteritems(config['column_map'])}
    indicator['observables'] = {

    }
    return indicator


@click.group(invoke_without_command=False)
@click.pass_context
def cli(context):
    pass


@click.command()
@click.argument('csv', type=click.File('rb'), prompt='Path to your CSV')
@click.option('--build_config', type=click.BOOL, default=False)
@click.option('--username', type=click.STRING, prompt=True)
@click.option('--password', type=click.STRING, prompt=True)
def upload_indicators(context, csv, build_config, username, password):
    config_filename = get_config_filename(csv.name)
    config_exists = os.path.exists(config_filename)
    if not config_exists or build_config:
        config = configure_indicator_uploader(config_filename)
    else:
        config = read_config(config_filename)

    perch = PerchAPIClient(username=username, password=password)

    for row in csv:
        indicator = parse_row_to_indicator(config, row)
        perch.indicators.create(**indicator)


    click.echo('hello world')


def configure_indicator_uploader(filename):
    communities = get_user_communities()
    config = {
        'filename': filename,
        'column_map': {
            'id': click.prompt('Which column contains the indicator id?', type=click.INT),
            'title': click.prompt('Which column contains the indicator title?', type=click.INT),
            'description': click.prompt('Which column contains the indicator description?', type=click.INT),
            'tlp': click.prompt('Which column contains the tlp level?', type=click.INT),
            'confidence': click.prompt('Which column contains the confidence level?', type=click.INT),
            'observable_type': click.prompt('Which column contains the observable type?', type=click.INT),
            'observable_value': click.prompt('Which column contains the observable value?', type=click.INT)
        },
        'communities': [
            click.prompt('Please enter the ids of the communities you wish to share with separated by a comma.',
                         type=click.Choice(communities)).split(',')
        ]
    }
    confirm_msg = '/n'.join([json.dumps(config, indent=2), 'Does this configuration look correct?'])
    if click.confirm(confirm_msg):
        write_config(filename, config)
        return config
    click.echo('Alright, lets try that again.')
    configure_indicator_uploader(filename)

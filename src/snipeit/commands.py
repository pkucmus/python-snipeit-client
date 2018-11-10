import json
import logging
from subprocess import run, PIPE
import click

from snipeit.client import SnipeItClient
from snipeit.utils import SetEncoder


logging.captureWarnings(True)


HW_INFO_CLASSES = (
    b'bus',
    b'memory',
    b'processor',
    b'bridge',
    b'display',
    b'network',
    b'disk',
)


@click.group()
@click.option('--url', type=click.STRING, envvar='SNIPEIT_URL', prompt=True)
@click.option('--jwt', type=click.STRING, envvar='SNIPEIT_JWT', prompt=True)
@click.option('--no-https-verify', is_flag=True)
@click.pass_context
def cli(ctx, url, jwt, no_https_verify):
    ctx.obj = {'client': SnipeItClient(url, jwt, not no_https_verify)}


@cli.command()
@click.pass_context
@click.argument('asset_tag', type=click.STRING)
def report_asset(ctx, asset_tag):
    client = ctx.obj['client']
    asset_id = client.endpoints.get_hardware_bytag(asset_tag)['id']
    result = run(['sudo', 'lshw', '-short'], check=True, stdout=PIPE)
    lines = result.stdout.split(b'\n')
    index_of_class = lines[0].index(b'Class')
    index_of_desc = lines[0].index(b'Description')
    output = {}
    for line in lines[2:]:
        klass = line[index_of_class:index_of_desc].strip()
        desc = line[index_of_desc:].strip()

        if klass in HW_INFO_CLASSES:
            if klass == b'memory':
                output.setdefault(
                    klass.decode('utf-8'),
                    list()
                ).append(desc.decode('utf-8'))
            else:
                output.setdefault(
                    klass.decode('utf-8'),
                    set()
                ).add(desc.decode('utf-8'))

    resposne = client.endpoints.update_hardware(
        asset_id,
        {
            '_snipeit_hw_info_2': json.dumps(output, indent=4, cls=SetEncoder)
        }
    )
    resposne['messages']


if __name__ == '__main__':
    cli()

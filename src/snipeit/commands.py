from subprocess import run, PIPE
import click

from snipeit.client import SnipeItClient


@click.group()
@click.option('--url', type=click.STRING, envvar='SNIPEIT_URL', prompt=True)
@click.option('--jwt', type=click.STRING, envvar='SNIPEIT_JWT', prompt=True)
@click.option('--verify_https', type=click.BOOL, default=True)
@click.pass_context
def cli(ctx, url, jwt, verify_https):
    ctx.obj = {'client': SnipeItClient(url, jwt, verify_https)}


@cli.command()
@click.pass_context
@click.argument('asset_tag', type=click.STRING)
def report_asset(ctx, asset_tag):
    result = run(['sudo', 'lshw', '-short'], check=True, stdout=PIPE)
    lines = result.stdout.split(b'\n')
    index_of_class = lines[0].index(b'Class')
    index_of_desc = lines[0].index(b'Description')
    for line in lines[2:]:
        klass = line[index_of_class:index_of_desc].strip()
        desc = line[index_of_desc:].strip()

        print(klass, desc)


if __name__ == '__main__':
    cli()

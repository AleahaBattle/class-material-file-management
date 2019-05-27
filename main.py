"""
Usage:
main.py list -s done|pending|all(D) -c [CATEGORY]
main.py create [TASK NAME] -d [DESCRIPTION] -p [PENDING DUE DATE] -c [CATEGORY]
main.py complete id | [TASK NAME] -c [CATEGORY]
Homework:
* Add the "filter by date" functionality to list
"""
import os
import json
import click

from todos import TodoManager


def _debug(msg):
    ctx = click.get_current_context()
    if ctx.obj['debug']:
        click.echo(msg)


def _json_dumps(obj):
    ctx = click.get_current_context()
    return json.dumps(obj, indent=ctx.obj['indent'])


@click.group()
@click.option('--debug/--no-debug', default=False)
@click.option('-i', '--indent', type=int, default=2)
@click.option('--path', default='todos/')
@click.pass_context
def cli(ctx, debug, indent, path):
    ctx.obj['debug'] = debug
    ctx.obj['indent'] = indent
    ctx.obj['path'] = path
    ctx.obj['manager'] = TodoManager(path)
    _debug('Debug mode is %s' % ('on' if debug else 'off'))


@cli.command()
@click.option(
    '-s', '--status',
    type=click.Choice(['all', 'pending', 'done']), default='pending')
@click.pass_context
def list(ctx, status):
    manager = ctx.obj['manager']
    todos = manager.list()
    if not todos:
        print("No todos yet :(")

    for category, _todos in todos.items():
        print("# {}".format(category))
        for todo in _todos:
            if status == 'all' or status == todo['status']:
                print("\t{} - {} - {} - {}".format(
                    todo['task'], todo['description'],
                    todo['due_on'], todo['status']))
        print('-' * 90)


@cli.command()
@click.argument('name')
@click.option('-c', '--category', default='general')
@click.option('-d', '--description')
@click.option('-p', '--due-on', help='Date Formats: 2018-01-01')
@click.pass_context
def create(ctx, name, category, description, due_on):
    manager = ctx.obj['manager']
    manager.new(name, category, description=description, due_on=due_on)


@cli.command()
@click.argument('name')
@click.option('-c', '--category', default='general')
@click.pass_context
def complete(ctx, name, category):
    manager = ctx.obj['manager']
    manager.done(name, category


if __name__ == '__main__':
    cli(obj={})

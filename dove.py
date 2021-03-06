import os
import json
import click
import subprocess

__location__ = os.path.realpath(os.path.join(os.getcwd()))
CONFIG_FILE = 'dove.json'


def read_config(location=__location__):
  with open(os.path.join(location, CONFIG_FILE)) as version_file:
    return json.load(version_file)

def write_config(config, location=__location__):
  with open(os.path.join(location, CONFIG_FILE), 'w') as version_file:
    version_file.write(json.dumps(obj=config, indent=4, sort_keys=True))

def update_version(version, pos):
  components = version.split('.')
  for position in pos:
    components[position] = str(int(components[position]) + 1)
  return components

def reset_version(version, pos):
  components = version.split('.')
  for position in pos:
    components[position] = '0'
  return components

def to_version_string(components):
  version = ''
  for i in range(0, len(components)):
    version += components[i]
    if i != len(components) - 1:
      version += '.'
  return version

def extend_command(*args):
  command = None
  for arr in args:
    if command is None:
      command = arr
    else:
      command.extend(arr)
  return command


@click.group(name='dove')
def cli():
  """A docker versioning extension that manages docker tags
     through a JSON file, so that the user doesn't have to 
     get into the hassle of writing and updating image tags.\n
     Maintained by: Intech Process Automation \n
     For more info, visit: \n
     \t https://github.com/intech-iiot/dove
     """
  pass


@click.command(name='build')
@click.option('--bump', '-b', multiple=True, help='Version position(s) to bump')
@click.option('--args', '-a', multiple=True,
              help='Docker build arguments (Except --tag, -t)')
def build(bump, args):
  """Call docker build with saved tag"""
  try:
    config = read_config()
    if 'version' not in config or 'format' not in config:
      click.echo('Error: The dove.json configuration is invalid')
      return
    old_version = config['version']
    version_parts = old_version.split('.')
    if bump is not None:
      version_parts = update_version(old_version, map(int, bump))
      config['version'] = to_version_string(version_parts)
    new_tag = config['format'].format(*version_parts)
    click.echo('Using tag: [{}]'.format(new_tag))
    command = extend_command(['docker', 'build'], args, ['-t', new_tag, './'])
    subprocess.check_call(command, cwd=str(__location__))
    write_config(config)
  except BaseException as e:
    print str(e)


@click.command(name='tag')
@click.option('--srcimg', '-s', help='Tag of the source image')
@click.option('--bump', '-b', multiple=True, help='Version position(s) to bump')
def tag(srcimg, bump):
  """Call docker tag with saved tag"""
  try:
    config = read_config()
    if 'version' not in config or 'format' not in config:
      click.echo('Error: The dove.json configuration is invalid')
      return
    old_version = config['version']
    version_parts = old_version.split('.')
    if bump is not None:
      version_parts = update_version(old_version, map(int, bump))
      config['version'] = to_version_string(version_parts)
    new_tag = config['format'].format(*version_parts)
    click.echo('Using tag: [{}]'.format(new_tag))
    command = ['docker', 'tag', srcimg, new_tag]
    subprocess.check_call(command, cwd=str(__location__))
    write_config(config)
  except BaseException as e:
    print str(e)


@click.command(name='new')
@click.option('--template', '-t', help='Image name template')
@click.option('--initial', '-i', help='The initial version to start from')
def create_new(template, initial):
  """Initialize a new dove configuration"""
  try:
    if template is None:
      click.echo('Error: No template provided')
      return
    if initial is None:
      click.echo('Error: No initial version provided')
      return
    new_config = dict()
    new_config['format'] = template
    new_config['version'] = initial
    write_config(new_config)
    click.echo('New config generated: \n' + json.dumps(obj=new_config, indent=4, sort_keys=True))
  except BaseException as e:
    print str(e)


@click.command(name='get')
@click.option('--version', '-v', help='Just get the version', is_flag=True)
def get_tag(version):
  """Get the current tag of the image"""
  try:
    config = read_config()
    if 'version' not in config or 'format' not in config:
      click.echo('Error: The dove.json configuration is invalid')
      return
    if version is True:
      click.echo(config['version'])
    else:
      version = config['version'].split('.')
      tag = config['format'].format(*version)
      click.echo(tag)
      return tag
  except BaseException as e:
    print str(e)


@click.command(name='push')
@click.option('--args', '-a', multiple=True, help='Docker command arguments')
def push(args):
  """Call docker push on saved tag"""
  try:
    config = read_config()
    if 'version' not in config or 'format' not in config:
      click.echo('Error: The dove.json configuration is invalid')
      return
    version = config['version'].split('.')
    tag = config['format'].format(*version)
    click.echo("Pushing image: [{}]".format(tag))
    command = extend_command(['docker', 'push'], args, [tag])
    subprocess.check_call(command, cwd=str(__location__))
  except BaseException as e:
    print str(e)
  

@click.command(name='bump')
@click.option('--position', '-p', multiple=True, help='Version position(s) to bump')
def bump(position):
  """Just bump up the current version"""
  try:
    config = read_config()
    if 'version' not in config or 'format' not in config:
      click.echo('Error: The dove.json configuration is invalid')
      return
    old_version = config['version']
    version_parts = old_version.split('.')
    if position is not None:
      version_parts = update_version(old_version, map(int, position))
      config['version'] = to_version_string(version_parts)
    write_config(config)
    new_tag = config['format'].format(*version_parts)
    click.echo(new_tag)
  except BaseException as e:
    print str(e)


@click.command(name='reset')
@click.option('--position', '-p', multiple=True, help='Version position(s) to reset')
def reset(position):
  """Reset the version at position(s) to 0"""
  try:
    config = read_config()
    if 'version' not in config or 'format' not in config:
      click.echo('Error: The dove.json configuration is invalid')
      return
    old_version = config['version']
    version_parts = old_version.split('.')
    if position is not None:
      version_parts = reset_version(old_version, map(int, position))
      config['version'] = to_version_string(version_parts)
    write_config(config)
    new_tag = config['format'].format(*version_parts)
    click.echo(new_tag)
  except BaseException as e:
    print str(e)


@click.command(name='save')
@click.option('--filename', '-f', help='The name of the resultant file')
def save(filename):
  """Call a docker save with saved tag"""
  try:
    config = read_config()
    if config is None:
      click.echo("Error: No filename provided")
      return
    if 'version' not in config or 'format' not in config:
      click.echo('Error: The dove.json configuration is invalid')
      return
    version = config['version'].split('.')
    tag = config['format'].format(*version)
    command = ['docker', 'save', '-o', filename, tag]
    subprocess.check_call(command, cwd=str(__location__))
  except BaseException as e:
    print str(e)


cli.add_command(build)
cli.add_command(tag)
cli.add_command(create_new)
cli.add_command(push)
cli.add_command(get_tag)
cli.add_command(save)
cli.add_command(bump)
cli.add_command(reset)
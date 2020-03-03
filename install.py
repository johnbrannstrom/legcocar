#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.. moduleauthor:: John Brännström <john.brannstrom@gmail.com>

Install
*******

This is a program installer module. It can be used to install a program on a
Linux system and prepare the Linux environment for this program to run
properly. This script also requires a Linux environment.

"""

# Built in modules
import subprocess
import argparse
import os
import sys


# Adding variables and values in this dictionary will enable them to be
# substituted into run_cmd commands
run_cmd_vars = dict()

# Name of project
PROJECT = 'legcocar'
run_cmd_vars['PROJECT'] = PROJECT


# Install script location
run_cmd_vars['DIR'] = os.path.dirname(os.path.realpath(sys.argv[0]))


# noinspection PyShadowingNames,PyTypeChecker,PyUnboundLocalVariable
def run_cmd(command: str, mode: str = 'status'):
    """
    Run a command and print status.

    :param command: Command to run.
    :param mode:    Choises are: "status", "regular" and "quiet":
                    "status":  Print command and status.
                    "regular": Print command, stdout and stderr to screen, just
                               as usual.
                    "quiet":   Don't print anything.

    """
    # Insert values from run_cmd_vars if they exist
    for key, val in run_cmd_vars.items():
        var = '{' + key + '}'
        if var in command:
            command = command.replace(var, val)

    # Handle regular mode
    if mode.lower() == 'regular':
        print(command, flush=True)
        with subprocess.Popen(command,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              bufsize=1,
                              shell=True,
                              universal_newlines=True) as p:
            for line in p.stdout:
                print(line, end='', flush=True)
            for line in p.stderr:
                print(line, end='', flush=True)

    # Handle status mode
    elif mode == 'status':
        result = subprocess.run(command, shell=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            status = '\033[1;32m OK  \033[0m'
            stderr = ''
        elif result.returncode > 0:
            status = '\033[1;91mERROR\033[0m'
            stderr = '\n' + result.stderr.decode('utf-8')

        # Print status
        status_string = "[ {status} ] {command}{stderr}"
        status_string = status_string.format(status=status,
                                             command=command,
                                             stderr=stderr)
        print(status_string, flush=True)

    # Handle quiet mode
    else:
        subprocess.run(command, shell=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)


# Parse command line arguments
# noinspection PyShadowingNames
def parse_command_line_options():
    """
    Parse options from the command line.
    
    :rtype: Namespace

    """
    quick_help = (
        'Supplying this flag will skip as many time consuming steps as possibl'
        'e to speed up the installation process. This is used for delevopment '
        'purposes only.')
    remote_help = 'Install program on remote user@host.'
    description = 'Installer script for the {PROJECT}.'.format(PROJECT=PROJECT)
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-q', '--quick',  default=False, action='store_true',
                        help=quick_help, required=False)
    parser.add_argument('-r', '--remote', type=str, default="",
                        help=remote_help, required=False)
    args = parser.parse_args()
    return args


args = parse_command_line_options()
quick = args.quick
remote = args.remote

# Copy program and installer script to remote location and run it there instead
if remote != "":
    run_cmd_vars['REMOTE'] = remote
    run_cmd("ssh {REMOTE} 'mkdir -p /tmp/{PROJECT}'", mode='quiet')
    run_cmd("echo 'put -r {DIR}/*' > /tmp/sftp_batchfile", mode='quiet')
    run_cmd("sftp -b /tmp/sftp_batchfile {REMOTE}:/tmp/{PROJECT}",
            mode='regular')
    run_cmd("rm /tmp/sftp_batchfile", mode='quiet')

    # Run install script on remote side
    command = "ssh {REMOTE} '/tmp/{PROJECT}/install.py'"
    if quick:
        command = "ssh {REMOTE} '/tmp/{PROJECT}/install.py -q'"
    run_cmd(command, mode='regular')
    sys.exit(0)

# Add program specific content below this line

# List of packages to install with apt
APT_PACKAGE_LIST = [
    'python3=3.7.3-1', 'openssl=1.1.1c-1', 'build-essential=12.6',
    'tk-dev=8.6.9+1', 'libncurses5-dev=6.1+20181013-2+deb10u2',
    'libncursesw5-dev=6.1+20181013-2+deb10u2', 'libreadline-dev=7.0-5',
    'libgdbm-dev=1.18.1-4', 'libsqlite3-dev=3.27.2-3',
    'libssl-dev=1.1.1d-0+deb10u2', 'libbz2-dev=1.0.6-9.2~deb10u1',
    'libexpat1-dev=2.2.6-2+deb10u1', 'liblzma-dev=5.2.4-1',
    'zlib1g-dev=1:1.2.11.dfsg-1', 'libffi-dev=3.2.1-9', 'uuid-dev=2.33.1-0.1',
    'python3-pip=18.1-5+rpt1', 'apache2=2.4.38-3+deb10u3',
    'libapache2-mod-wsgi-py3=4.6.5-1', 'rabbitmq-server=3.7.8-4',
    'supervisor=3.3.5-1']

# List of packages to install with pip3
PIP3_PACKAGE_LIST = [
    'bricknil==0.9.3', 'flask==1.1.1', 'pika==1.1.0', 'bricknil-bleak==0.3.1',
    'coloredlogs==10.0', 'verboselogs==1.7']

# Create supervisor log dir
run_cmd('mkdir -p /var/log/supervisor')

# Set bash_aliases for root
run_cmd('''sed -i "/alias ls='ls -lah --color=auto'/d" /root/.bashrc''',
        mode='quiet')
run_cmd('''echo "alias ls='ls -lah --color=auto'" >> /root/.bashrc''')

# Install packages with apt
if not quick:
    run_cmd('apt-get update')
    for package in APT_PACKAGE_LIST:
        run_cmd('apt-get -y install {package}'.format(package=package))

# Install packages with pip3
if not quick:
    for package in PIP3_PACKAGE_LIST:
        run_cmd('pip3 install {package}'.format(package=package))

# Create project user
if not quick:
    run_cmd('useradd -m {PROJECT}')

# Create directories, move files, and set permissions
run_cmd('rm -Rf /srv/flask_wsgi', mode='quiet')
run_cmd('rm -Rf /srv/{PROJECT}', mode='quiet')
run_cmd('mkdir /srv/flask_wsgi')
run_cmd('mkdir /srv/{PROJECT}')
run_cmd('mkdir -p /var/log/{PROJECT}')
run_cmd('chown -R {PROJECT}:{PROJECT} /var/log/{PROJECT}')
run_cmd('chmod 755 /var/log/{PROJECT}')
run_cmd('cp {DIR}/other/legcocar_template.conf /srv/{PROJECT}/')
run_cmd('cp -R {DIR}/html_static /srv/{PROJECT}/')
run_cmd('cp -R {DIR}/html_templates /srv/{PROJECT}/')
run_cmd('cp {DIR}/src/flaskserver.py /srv/{PROJECT}/')
run_cmd('cp {DIR}/src/wsgi.py /srv/flask_wsgi/')
run_cmd('cp {DIR}/other/000-default.conf /etc/apache2/sites-available/')
run_cmd('chown -R {PROJECT}:{PROJECT} /srv/flask_wsgi')
run_cmd('chmod 755 /srv/flask_wsgi')
run_cmd('chown -R {PROJECT}:{PROJECT} /srv/{PROJECT}')
run_cmd('chmod 755 /srv/{PROJECT}')

# Restart apache2 for settings to take affect
run_cmd('service apache2 restart')

# Create rabbitMQ .erlang.cookie
if not quick:
    run_cmd_vars['ERLANG_COOKIE'] = 'HEIQLGKPYPKGHVQFRPRF'
    run_cmd('echo -n {ERLANG_COOKIE} > /var/lib/rabbitmq/.erlang.cookie')
    run_cmd('chown rabbitmq.rabbitmq /var/lib/rabbitmq/.erlang.cookie')
    run_cmd('chmod 400 /var/lib/rabbitmq/.erlang.cookie')

# /etc/rabbitmq/enabled_plugins
if not quick:
    run_cmd(
        '''echo '[rabbitmq_management].' > /etc/rabbitmq/enabled_plugins''')
    run_cmd('chown rabbitmq.rabbitmq /etc/rabbitmq/enabled_plugins')

# Create RabbitMQ project user
if not quick:
    run_cmd('rabbitmqctl add_user {PROJECT} {PROJECT}')
    run_cmd('rabbitmqctl set_user_tags {PROJECT} administrator')

# Restart RabbitMQ server
if not quick:
    run_cmd('service rabbitmq-server restart')

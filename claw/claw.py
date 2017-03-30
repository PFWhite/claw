VER = '1.1.0'
docstr = """The Claw.
This module is used to connect to an sftp server and download a file

Usage:
  claw.py --version
  claw.py (-h | --help)
  claw.py <ftp_host> <ftp_port> <remote_file_path> ... [--destination=<d>]  [--username=<un>] [--password=<pw>] [--key_path=<key>] [--key_pw=<keypw>] [--verbose]
  claw.py <config_file> [--verbose]

Options:
  -h --help                      Show this screen.
  -v --version                   Show version.
  --verbose                      Print more text
  -k <key> --key_path=<key>      Path to keyfile used on server
  -p <keypw> --key_pw=<keypw>    Password to keyfile
  -u <un> --username=<un>        SFTP username
  -s <pw> --password=<pw>        SFTP username password
  -d <d> --destination           Path to place the file

"""

import logging
import pysftp
import sys
from paramiko.ssh_exception import SSHException, BadAuthenticationType

import yaml
from docopt import docopt

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def main(args=docopt(docstr)):
    """
    Creates the connection, pulls a file, and closes the connection

    args: a dictionary containing the required parametes for sftp
    """
    config_path = args.get('<config_file>', None)
    if config_path:
        with open(config_path, 'r') as config_file:
            try:
                args = yaml.load(config_file.read()).get('arguments')
            except yaml.YAMLError as exc:
                print(exc)

    verbose = args['--verbose'] or False
    connection_details = position_claw(host=args['<ftp_host>'],
                                       port=args['<ftp_port>'],
                                       username=args['--username'],
                                       password=args['--password'],
                                       private_key=args['--key_path'],
                                       private_key_pass=args['--key_pw'])

    with get_connection(connection_details, verbose) as connection:
        get_target(connection, args['<remote_file_path>'], args['--destination'], verbose)

def get_connection(connection_details, verbose=False):
    try:
        connection = pysftp.Connection(**connection_details)
        logger.info("User %s connected to sftp server %s" % \
            (connection_details['username'], connection_details['host']))
    except IOError as e:
        logger.error("Please verify that the private key file mentioned in "\
            "config.yaml exists.")
        logger.exception(e)
        sys.exit()
    except BadAuthenticationType as e:
        logger.error("Please verify that the server connection details "\
            "in config.yaml are correct")
        logger.exception(e)
        sys.exit()
    except SSHException as e:
        logger.error("Please verify that the server connection details "\
            "in config.yaml are correct")
        logger.exception(e)
        sys.exit()

    return connection

def get_target(connection, file_path, destination_path, verbose=False):
    """
    For all the file paths, go grab the file off the server

    connection: SFTP connection object
    file_path: remote file path we are trying to download
    destination_path: where we want the file to go
    verbose: print out logs as it happens
    """

    if isinstance(file_path, str):
        file_path = file_path.split()

    for path in file_path:
        logger.info("Downloading remote file file: %s" % path or '')
        logger.info("Saving to local file name: %s " % destination_path or path)
        connection.get(path,destination_path)

def position_claw(host, port,
                  username, password,
                  private_key, private_key_pass):
    """
    Process args and get them ready to make a connection
    """

    #Ignore default behavior requiring host to be in known_hosts file
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None

    connection_details = {'host':host,
                          'port':int(port),
                          'username':username,
                          'password':password,
                          'private_key':private_key,
                          'private_key_pass':private_key_pass,
                          'cnopts':cnopts
                          }
    return connection_details

if __name__ == '__main__':
    arguments = docopt(docstr, version=VER)
    main(arguments)

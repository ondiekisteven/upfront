from configparser import ConfigParser


parser = ConfigParser()
parser.read('config.ini')


def stkdb_host():
    return parser.get('stk_db', 'host')


def stkdb_user():
    return parser.get('stk_db', 'user')


def stkdb_pass():
    return parser.get('stk_db', 'pass')


def stkdb_db():
    return parser.get('stk_db', 'db')
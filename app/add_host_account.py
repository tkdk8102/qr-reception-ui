import sys
import argparse
from flask_bcrypt import Bcrypt
from library import db_manager
from library import db_config

def main():
    parser = argparse.ArgumentParser(description='add host account and password.')
    parser.add_argument('--delete', action='store_true', default=False)
    parser.add_argument('-a', '--account', required=True)
    parser.add_argument('-p', '--password', required='--delete' not in sys.argv)
    args = parser.parse_args()

    guests = db_manager.Connector()
    guests.connect(**db_config.users_db, table='hosts')
    if args.delete:
        guests.del_host(
            account = args.account
        )
    else:
        data = guests.add_host(
            account  = args.account,
            password = Bcrypt().generate_password_hash(args.password + args.account)
        )
    guests.close()

if __name__ == '__main__':
    main()

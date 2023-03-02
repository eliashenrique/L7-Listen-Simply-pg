# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function

import configparser
import psycopg2
import os


class Dao(object):

    def __init__(self, get_config_parser, env):
        self.env = env
        self.get_config_parser = get_config_parser
        host = self.get_config_parser[self.env]['host']
        user = self.get_config_parser[self.env]['user']
        password = self.get_config_parser[self.env]['password']
        database = self.get_config_parser[self.env]['database']

        self.conn_params = {
            "host": host,
            "user": user,
            "password": password,
            "database": database,
        }

    def store(self, raw):
        log_id = str(raw['id'])
        connection_dat = str(raw['connection_date'])
        key = "RmVsaXBlLUFuZHJhZGUtMjEuNzA2LjI2OS8wMDAxLTY4"

        # Remove id and connection_date keys from the raw dictionary
        raw_del = raw.copy()
        del raw_del['id']
        del raw_del['connection_date']

        # Construct the SQL query with parameterized placeholders for the values
        param = ''.join(
            f'connection_log (id, connection_date, %s, created_at) VALUES' %
            ', '.join(i for i in raw.keys()))
        
        sql = ''.join(
            f'INSERT INTO {param} ({log_id}, \'{connection_dat}\', %s, NOW())'
            % ', '.join("pgp_sym_encrypt('" + str(i) + "', '" + key + "')"
                        for i in raw_del.values()))

        # Insert the values into the database using a context manager
        with psycopg2.connect(**self.conn_params) as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute(sql)
                    conn.commit()
                except psycopg2.Error as e:
                    print(f"Error inserting data into database: {e}")
                    conn.rollback()


def get_config():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.abspath(os.path.join(BASE_DIR + '/.config',
                                               'db.ini'))
    try:
        with open(config_path) as f:
            db_config = configparser.ConfigParser()
            db_config.read_file(f)
            return db_config
    except FileNotFoundError as e:
        print(f"Could not find config file: {e}")
        return None
    except configparser.Error as e:
        print(f"Error reading config file: {e}")
        return None

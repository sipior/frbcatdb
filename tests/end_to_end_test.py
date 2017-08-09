import os
from os.path import join,dirname,abspath
import unittest
import datetime
import psycopg2
from pyfrbcatdb import dbase as dbase
from pyfrbcatdb import decode_VOEvent as decode

class end2endtest(unittest.TestCase):
    def setUp(self):
        if 'TRAVIS' in os.environ:
             self.DB_NAME = 'frbcat'
             self.USER_NAME = 'postgres'
             self.DB_HOST = None
             self.DB_PORT = None
             self.USER_PASSWORD = None
             self.connection, self.cursor = dbase.connectToDB(
                 dbName=self.DB_NAME, userName=self.USER_NAME,
                 dbPassword=self.USER_PASSWORD, dbHost=self.DB_HOST,
                 dbPort=self.DB_PORT, dbCursor=psycopg2.extensions.cursor)
        else:
            # TODO: read config file
            self.DB_NAME = 'frbcat'
            self.USER_NAME = 'aa-alert'
            self.DB_HOST = 'localhost'
            self.DB_PORT = None
            self.USER_PASSWORD = 'aa-alert'
            self.connection, self.cursor = dbase.connectToDB(
                dbName=self.DB_NAME, userName=self.USER_NAME,
                dbPassword=self.USER_PASSWORD, dbHost=self.DB_HOST,
                dbPort=self.DB_PORT, dbCursor=psycopg2.extensions.cursor)
        self.test_data = os.path.join(dirname(abspath(__file__)), '..', 'test_data')

    def tearDown(self):
        self.connection.close()

    def get_num_rows_main_tables(self):
        '''
        return the number of rows for the main tables:
            authors, frbs, observations, rop, rmp
        '''
        sql = "select id from authors"
        self.cursor.execute(sql)
        len_authors = len(self.cursor.fetchall())
        sql = "select id from frbs"
        self.cursor.execute(sql)
        len_frbs = len(self.cursor.fetchall())
        sql = "select id from observations"
        self.cursor.execute(sql)
        len_observations = len(self.cursor.fetchall())
        sql = "select id from radio_observations_params"
        self.cursor.execute(sql)
        len_rop = len(self.cursor.fetchall())
        sql = "select id from radio_measured_params"
        self.cursor.execute(sql)
        len_rmp = len(self.cursor.fetchall())
        return (len_authors, len_frbs, len_observations, len_rop, len_rmp)

    def test_01(self):
        '''
        Adding a new event with a new author
        should add one row in authors, frbs, observations, rop, rmp
        '''
        len_before = self.get_num_rows_main_tables()
        decode.decode_VOEvent(os.path.join(self.test_data, 'Detection_unitTest1.xml'),
                              self.DB_NAME, self.DB_HOST, self.DB_PORT,
                              self.USER_NAME, self.USER_PASSWORD)
        len_after = self.get_num_rows_main_tables()
        # assert authors increased by 1
        #self.assertEqual(len_before[0], len_after[0]-1)
        # assert frbs increased by 1
        self.assertEqual(len_before[1], len_after[1]-1)
        # assert observations increased by 1
        self.assertEqual(len_before[2], len_after[2]-1)
        # assert rop increased by 1
        self.assertEqual(len_before[3], len_after[3]-1)
        # assert rmp increased by 1
        self.assertEqual(len_before[4], len_after[4]-1)


if __name__ == '__main__':
    unittest.main()
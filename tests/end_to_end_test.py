import os
from os.path import join,dirname,abspath
import unittest
import datetime
import psycopg2
from pyfrbcatdb import dbase as dbase
from pyfrbcatdb import create_VOEvent as pFcreate

class end2endtest(unittest.TestCase):
    def setUp(self):
        if 'TRAVIS' in os.environ:
            self.connection, self.cursor = dbase.connectToDB(dbName='frbcat', userName='postgres', dbPassword=None, dbHost=None,dbPort=None, dbCursor=psycopg2.extensions.cursor)
        else:
            self.connection, self.cursor = dbase.connectToDB(dbName='frbcat', dbCursor=psycopg2.extensions.cursor)
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
        Adding a new event with existing author 
        should add one row in frbs, observations, rop, rmp
        '''
        len_before = self.get_num_rows_main_tables()
        pFcreate.process_VOEvent(os.path.join(self.test_data, 'add_1.xml'))
        len_after = self.get_num_rows_main_tables()
        # assert frbs increased by 1
        self.assertEqual(len_before[1], len_after[1]-1)
        # assert observations increased by 1
        self.assertEqual(len_before[2], len_after[2]-1)
        # assert rop increased by 1
        self.assertEqual(len_before[3], len_after[3]-1)
        # assert rmp increased by 1
        self.assertEqual(len_before[4], len_after[4]-1)

    def test_02(self):
        '''
        Retracting the event added by test_01
        should remove one row in frbs, observations, rop, rmp
        '''
        len_before = self.get_num_rows_main_tables()
        pFcreate.process_VOEvent(os.path.join(self.test_data, 'retract_1.xml'))
        len_after = self.get_num_rows_main_tables()
        # assert frbs increased by 1
        self.assertEqual(len_before[1], len_after[1]+1)
        # assert observations increased by 1
        self.assertEqual(len_before[2], len_after[2]+1)
        # assert rop increased by 1
        self.assertEqual(len_before[3], len_after[3]+1)
        # assert rmp increased by 1
        self.assertEqual(len_before[4], len_after[4]+1)
        
    def test_03(self):
        '''
        Adding a new event with existing author and retracting the same
        event should result in the same amount of rows in
        authors, frbs, observations, rop, rmp
        '''
        len_before = self.get_num_rows_main_tables()
        pFcreate.process_VOEvent(os.path.join(self.test_data, 'add_1.xml'))
        pFcreate.process_VOEvent(os.path.join(self.test_data, 'retract_1.xml'))
        len_after = self.get_num_rows_main_tables()
        # assert authors,frbs,obs,rop,rmp all have the same length
        self.assertEqual(len_before, len_after)

if __name__ == '__main__':
    unittest.main()

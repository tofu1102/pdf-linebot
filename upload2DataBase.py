import os
import psycopg2
import datetime

DATABASE_URL = os.environ.get('DATABASE_URL')



def insert_test(name):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as curs:
            curs.execute(
                f"INSERT INTO test VALUES('{name}');"
                )

def insert_img(user_id,img,Done = False):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as curs:
            curs.execute(
                f"INSERT INTO Img VALUES('{user_id}',{Done}, {img});"
                )

if __name__ == '__main__':
    insert_test("tofu")

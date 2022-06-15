import os
import psycopg2

DATABASE_URL = os.environ.get('DATABASE_URL')


with psycopg2.connect(DATABASE_URL) as conn:
    with conn.cursor() as curs:
        curs.execute(
            "INSERT INTO articles(title, url) VALUES(%s, %s)", (title, url))

def insert_test(name):
    with conn.cursor() as curs:
        curs.execute(
        f"INSERT INTO test VALUES({name});"
        )

if __name__ == '__main__':
    insert_test("tofu")

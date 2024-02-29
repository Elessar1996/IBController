import psycopg2
import os
from Constants import *
import time
import csv

'''
MA_600
MA_540
MA_480
MA_420
MA_360
MA_300
MA_240
MA_180
MA_150
MA_90
MA_60
MA_30
MA_20
MA_5
'''


def check_db_exists(db_name):
    try:

        db = connect_db()

        cursor = db.cursor()

        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))

        exists = cursor.fetchone() is not None

        cursor.close()
        db.close()

        return exists

    except psycopg2.Error as e:

        print(f'error in checking the existence of the {db_name} database: {e}')

        return False


def create_db(db_name):
    if not check_db_exists(db_name):

        conn = None
        try:
            conn = psycopg2.connect(
                host=HOST,
                user=USER,
                password=PASSWORD,
                database=POSTGRES,
            )
        except psycopg2.Error as e:
            print(f"Error in Connecting to db: {e}")
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM pg_database;")
        list_database = cursor.fetchall()

        if db_name in [i[1] for i in list_database]:
            print("'{}' Database already exist".format(db_name))
            return
        else:
            print("'{}' Database not exist.".format(db_name))

        sql = f'CREATE database {db_name}'
        cursor.execute(sql)
        print(f"Database {db_name} has been created successfully !!")
        conn.close()

    else:
        print(f'database {db_name} already exists.')


def connect_db():
    try:
        db = psycopg2.connect(
            host=HOST,
            user=USER,
            password=PASSWORD,
            dbname=DATABASE_NAME
        )
    except psycopg2.Error as e:
        print("Error in Connecting to db: " + e)

    return db


def create_table(columns, table_name):
    """
    :param columns: [(a, b, c)] --> a, b, c are strings. a: column name   b: column type   c: if it is primary/foreign key
    :param table_name: name of the table
    :return: void
    """
    db = connect_db()
    cursor = db.cursor()
    executional_string = "CREATE TABLE " + table_name + " ("

    for idx, (col_name, col_var_type, col_key) in enumerate(columns):

        if idx == len(columns) - 1:
            executional_string += f"{col_name} {col_var_type} {col_key}"
        else:
            executional_string += f"{col_name} {col_var_type} {col_key}, "

    executional_string += ");"

    print(f'{executional_string}')

    try:
        cursor.execute(executional_string)
        db.commit()
    except psycopg2.Error as e:
        print("error in creating table: " + e)


def insert_item(table, columns_list, value_tuple):
    """
    :param table: the table in which you want to insert data
    :param columns_list: list of columns that you're going to insert data into them
    :param value_tuple: tuple of values that you're going to insert
    :return: void
    """
    db = connect_db()
    cursor = db.cursor()

    executional_string = f"INSERT INTO {table}("

    for idx, col in enumerate(columns_list):

        if idx == len(columns_list) - 1:
            executional_string += col
            executional_string += ") "
        else:
            executional_string += col
            executional_string += ", "

    executional_string += "VALUES("

    for idx in range(len(value_tuple)):

        if idx == len(value_tuple) - 1:
            executional_string += "%s)"
        else:
            executional_string += "%s,"

    try:
        cursor.execute(executional_string, value_tuple)
        db.commit()
        cursor.close()
        db.close()
    except psycopg2.Error as e:
        print(f'error in inserting item: {e}')


def delete_all():
    """
    :param db: the database
    :return: void
    """
    db = connect_db()

    cursor = db.cursor()

    cursor.execute("""SELECT table_name FROM information_schema.tables
           WHERE table_schema = 'public'""")

    all_tables = [i[0] for i in cursor.fetchall()]
    print(f'all tables: {all_tables}')

    try:

        for table in all_tables:
            cursor.execute(f"DELETE FROM {table}")
            db.commit()
            print(f'table {table} is cleaned')

    except psycopg2.Error as e:
        print(f'error occurred while trying to reseting the session: {e}')


    cursor.close()
    db.close()


def get_list_of_all_tables():
    db = connect_db()

    cursor = db.cursor()

    cursor.execute("""SELECT table_name FROM information_schema.tables
           WHERE table_schema = 'public'""")

    all_tables = [i[0] for i in cursor.fetchall()]

    return all_tables


def save_as_csv(table_name):
    # connect to the database
    conn = connect_db()

    # create a cursor
    cur = conn.cursor()

    # execute a sql query
    cur.execute(f"SELECT * FROM {table_name}")

    # fetch the results
    results = cur.fetchall()

    # open a file in the downloads folder
    with open(f"./{table_name}.csv", "w", newline="") as f:
        # Create a CSV writer
        writer = csv.writer(f)

        # write the column names
        writer.writerow([col[0] for col in cur.description])

        # write the query results
        writer.writerows(results)

    # close the cursor and connection
    cur.close()
    conn.close()


def drop_all_tables():
    '''
    dropping all tables in db
    :return: void
    '''
    db = connect_db()

    cursor = db.cursor()

    cursor.execute("""SELECT table_name FROM information_schema.tables
           WHERE table_schema = 'public'""")

    all_tables = [i[0] for i in cursor.fetchall()]

    try:

        for table in all_tables:
            cursor.execute(f"DROP TABLE {table}")
            db.commit()
            print(f'table {table} is dropped')

    except psycopg2.Error as e:
        print(f'error occurred while trying to drop all tabels: {e}')

    cursor.close()
    db.close()


def select_item(table, list_column, order_by, asc_or_desc, one_or_all):
    """
    :param db: database instance
    :param table: table name
    :param list_column: list of columns
    :param order_by: order criteria
    :param one_or_all: fetchone or fetchall
    :return: result
    """
    db = connect_db()

    try:
        cursor = db.cursor()
    except psycopg2.Error as e:
        db = connect_db()
        cursor = db.cursor()
    executive_string = "SELECT "
    for idx, col in enumerate(list_column):
        if idx == len(list_column) - 1:
            executive_string += f'{col} '
        else:
            executive_string += f'{col}, '
    executive_string += f'FROM {table}'

    if order_by is not None:
        executive_string += f' ORDER BY {order_by}'
    if asc_or_desc is not None:
        executive_string += f' {asc_or_desc}'
    try:
        cursor.execute(executive_string)
        if one_or_all == "all":
            result = cursor.fetchall()
        else:
            result = cursor.fetchone()
    except psycopg2.Error as e:
        print(f'error in selecting data: {e}')
        result = None
    cursor.close()
    db.close()
    return result

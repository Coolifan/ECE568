import psycopg2


def connect_db():
    conn = psycopg2.connect(host="db", database="postgres", user="postgres", password="123456", port="5432")

    return (conn, conn.cursor())

def execute_and_commit(sql, conn, cursor):
    cursor.execute(sql)
    conn.commit()

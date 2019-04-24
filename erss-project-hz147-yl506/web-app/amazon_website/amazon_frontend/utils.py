import psycopg2
import socket

from google.protobuf.internal.encoder import _VarintBytes
from google.protobuf.internal.decoder import _DecodeVarint32

# Get an open TCP socket(SOCK_STREAM) to the ip address
def get_open_socket(address):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(address)
    return client_socket


# Send a request (google buffer protocol object) through an opened socket.
# This function will not close the socket after sending the request.
# The request is serialized. Then a length indicator (big endian int) is added as the header to the serialized request.
# The socket SHOULD be an opened one, or an error may be raised by socket.sendall
def send_request_on_socket(request, socket):
    serialized_request = request.SerializeToString()
    size = request.ByteSize()
    socket.sendall(_VarintBytes(size) + serialized_request)


def connect_db():
    conn = psycopg2.connect(host="db", database="postgres", user="postgres", password="123456", port="5432")
    return (conn, conn.cursor())

def execute_and_commit(sql, conn, cursor):
    cursor.execute(sql)
    conn.commit()
import socket 
import sys
import struct
import time

import world_amazon_pb2 as amazon_protocol
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


# Receive, parse and return a response in AResponses format from an open socket
# The socket SHOULD be an opened one, or an error may be raised by socket.recv
# input --
    # sock: open tcp socket
    # response_type: google buffer protocol type, such as AReponses, which has ParseFromString method.
def recv_response_on_socket(response_type, sock):
    data = read_varint_delimited_stream(sock)
    response = response_type()
    response.ParseFromString(data)
    return response
    

# read google buffer protocol response from a socket, return the raw data
def read_varint_delimited_stream(sock):
    size_variant = b''
    while True:
        size_variant += sock.recv(1)
        try:
            size = _DecodeVarint32(size_variant, 0)[0]
        except IndexError:
            continue # if decode failed, read one more byte from stream
        break # else if decode succeeded, break. Size is available
    data = sock.recv(size) # data in string format
    return data

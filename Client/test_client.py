import socket
from Client import GameOfLife
import numpy as np
import sys
from io import BytesIO


def receive_complete_bytestream(client_socket,MESSAGE_SIZE, MAX_BUFFER_SIZE):
    '''
    Handles receiving data bytestream of client side sockets so that it is
    complete based on a fixed byte size and returns complete byte string
    '''
    bytes_received = 0
    # start with empty byte message
    input_from_server_bytes = b''

    #QUOTE FROM DOCUMENTATION:
    #"Now we come to the major stumbling block of sockets - send and recv operate on the network buffers.
    # They do not necessarily handle all the bytes you hand them (or expect from them), [...]"
    # Hence while loop to ensure we get the whole byte stream to deserialize
    while bytes_received < MESSAGE_SIZE:
        # receive bytestream from socket connection
        current_input = client_socket.recv(MAX_BUFFER_SIZE)
        #if we receive an empty message something is odd
        if current_input == b'':
            raise RuntimeError("socket connection broken")

        # Did we receive the whole message? How much did we receive?
        current_input_size = sys.getsizeof(current_input)
        print(current_input_size, " bytes received")
        #Update size condition to exit the loop
        bytes_received = bytes_received + current_input_size
        #appending current input to whole input byte message
        input_from_server_bytes = input_from_server_bytes + current_input

    return input_from_server_bytes

'''
Testing the connection to server with a sample
grid as np array
'''

#Specify server adress
server_adress ="127.0.0.1"
port = 12345

#Establish Socket Connection
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("127.0.0.1", 12345))

#Test if numpy array (board state can be sent)
game = GameOfLife.GameOfLife(100)
test_array = game.old_grid

#Serialize as byte string
with BytesIO() as b:
    np.save(b, test_array)
    old_grid_serialized = b.getvalue()

out = old_grid_serialized
#send to server
client_socket.sendall(out)

answer_from_server = receive_complete_bytestream(client_socket, MESSAGE_SIZE=40113, MAX_BUFFER_SIZE=65536)

try:
    #input_from_client = pickle.loads(input_from_client_bytes, fix_imports=False)
    answer_from_server = np.load(BytesIO(answer_from_server))
    print("Server Reply:\n", answer_from_server)
except ValueError:
    print("Value error occured")

client_socket.close()
 #--------

#Specify server adress
server_adress ="127.0.0.1"
port = 12345

#Establish Socket Connection
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("127.0.0.1", 12345))

#Test if numpy array (board state can be sent)
game = GameOfLife.GameOfLife(100)
test_array = answer_from_server

#Serialize as byte string
with BytesIO() as b:
    np.save(b, test_array)
    old_grid_serialized = b.getvalue()

out = old_grid_serialized
#send to server
client_socket.sendall(out)

answer_from_server = receive_complete_bytestream(client_socket, MESSAGE_SIZE=40113, MAX_BUFFER_SIZE=65536)

try:
    #input_from_client = pickle.loads(input_from_client_bytes, fix_imports=False)
    answer_from_server = np.load(BytesIO(answer_from_server))
    print("Server Reply:\n", answer_from_server)
except ValueError:
    print("Value error occured")

client_socket.close()
# -*- coding: utf-8 -*-
# !/usr/bin/env python

#  An implementation of Conway's Game of Life in Python.
import numpy
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random
from tkinter import *
from io import BytesIO
import numpy as np
import socket


class GameOfLife:



    def __init__(self, N=100):
        """ Set up Conway's Game of Life. """
        # Here we create two grids to hold the old and new configurations.
        # This assumes an N*N grid of points.
        # Each point is either alive or dead, represented by integer values of 1 and 0, respectively.
        self.N = N
        self.old_grid = numpy.zeros(N * N, dtype='i').reshape(N, N)
        self.new_grid = numpy.zeros(N * N, dtype='i').reshape(N, N)

        # Set up a random initial configuration for the grid.
        for i in range(0, self.N):
            for j in range(0, self.N):
                if (random.randint(0, 100) < 15):
                    self.old_grid[i][j] = 1
                else:
                    self.old_grid[i][j] = 0

    def live_neighbours(self, i, j):
        """ Count the number of live neighbours around point (i, j). """
        s = 0  # The total number of live neighbours.
        # Loop over all the neighbours.
        for x in [i - 1, i, i + 1]:
            for y in [j - 1, j, j + 1]:
                if (x == i and y == j):
                    continue  # Skip the current point itself - we only want to count the neighbours!
                if (x != self.N and y != self.N):
                    s += self.old_grid[x][y]
                # The remaining branches handle the case where the neighbour is off the end of the grid.
                # In this case, we loop back round such that the grid becomes a "toroidal array".
                elif (x == self.N and y != self.N):
                    s += self.old_grid[0][y]
                elif (x != self.N and y == self.N):
                    s += self.old_grid[x][0]
                else:
                    s += self.old_grid[0][0]
        return s

    def update_grid(self):
        # Loop over each cell of the grid and apply Conway's rules.

        # network communication set up to communicate with remote server
        SERVER_ADRESS ="127.0.0.1"
        PORT = 12345
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #get client socket
        client_socket.connect((SERVER_ADRESS, PORT)) # connect to the server
        print("Client connection established at ", SERVER_ADRESS,":",PORT)

        # Serialize current grid state as byte string for sever transmission
        with BytesIO() as b:
            np.save(b, self.old_grid)
            old_grid_serialized = b.getvalue()

        size=sys.getsizeof(old_grid_serialized)
        print(self.old_grid)
        print("Size: ", size)
        out = old_grid_serialized
        # send to server
        client_socket.sendall(out)

        #Sever answer is the new grid state as a bytestream
        answer_from_server = GameOfLife.receive_complete_bytestream(client_socket, MESSAGE_SIZE=40113, MAX_BUFFER_SIZE=65536)

        try:
            grid_by_server = np.load(BytesIO(answer_from_server)) #deserialize byte server reply to a np array
            print("Server Reply:\n", grid_by_server)
        except ValueError:
            print("Value error occured")

        #update grid states
        self.new_grid = grid_by_server
        self.old_grid = self.new_grid

        client_socket.close()



        '''
         for i in range(self.N):
            for j in range(self.N):
               live = self.live_neighbours(i, j)
               if(self.old_grid[i][j] == 1 and live < 2):
                  self.new_grid[i][j] = 0 # Dead from starvation.
               elif(self.old_grid[i][j] == 1 and (live == 2 or live == 3)):
                  self.new_grid[i][j] = 1 # Continue living.
               elif(self.old_grid[i][j] == 1 and live > 3):
                  self.new_grid[i][j] = 0 # Dead from overcrowding.
               elif(self.old_grid[i][j] == 0 and live == 3):
                  self.new_grid[i][j] = 1 # Alive from reproduction.
                  
         # The new configuration becomes the old configuration for the next generation.      
         self.old_grid = self.new_grid
         '''

    @staticmethod
    def receive_complete_bytestream(client_socket, MESSAGE_SIZE, MAX_BUFFER_SIZE):
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

            # Did we receive the whole message? How much did we receive?
            current_input_size = sys.getsizeof(current_input)
            print(current_input_size, " bytes received")

            #if we receive an empty message something is odd
            if current_input == b'':
                raise RuntimeError("socket connection broken")


            #Update size condition to exit the loop
            bytes_received = bytes_received + current_input_size
            #appending current input to whole input byte message
            input_from_server_bytes = input_from_server_bytes + current_input

        return input_from_server_bytes
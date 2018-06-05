# -*- coding: utf-8 -*-
"""
Created on Thu May 31 13:56:41 2018

@author: Kathrin
"""

import tkinter
import time
import threading
import random
import queue
from Client import GameOfLife


class Gui:
    def __init__(self, master, queue, startCommand, stopCommand):
        self.queue = queue
        # grid on canvas
        self.dim = 100
        self.canvas = tkinter.Canvas(master,
                                     width=self.dim*5,
                                     height=self.dim*5,
                                     background='white')
        self.canvas.grid(row=0, column=1)
        self.rect = [[None for row in range(self.dim)] for col in range(self.dim)]
        for row in range(self.dim):
            for col in range(self.dim):
                self.rect[row][col] = self.canvas.create_rectangle(row*5, col*5,
                                                                  (row+1)*5,
                                                                  (col+1)*5,
                                                                  width=1,
                                                                  fill='white',
                                                                  outline='grey')
        # start and stop button
        frame = tkinter.Frame(master)
        frame.grid(row=0, column=0)
        start_button = tkinter.Button(frame,
                                      text="Start",
                                      command=startCommand)
        start_button.pack()
        stop_button = tkinter.Button(frame,
                                     text="Stop",
                                     command=stopCommand)
        stop_button.pack()

    def processIncoming(self):
        """Handle all messages currently in the queue, if any."""
        while self.queue.qsize():
            try:
                msg = self.queue.get(0)
                # Check contents of message and do whatever is needed. As a
                # simple test, print it (in real life, you would
                # suitably update the GUI's display in a richer fashion).
                for row in range(self.dim):
                    for col in range(self.dim):
                        if msg[row][col] == 1:
                            self.canvas.itemconfig(self.rect[row][col],
                                                   fill='blue',
                                                   outline='grey')
                        if msg[row][col] == 0:
                            self.canvas.itemconfig(self.rect[row][col],
                                                   fill='white',
                                                   outline='grey')
                self.canvas.update()
            except queue.Empty:
                # just on general principles, although we don't
                # expect this branch to be taken in this case
                pass


class ThreadedClient:
    """
    Launch the main part of the GUI and the worker thread. periodicCall and
    endApplication could reside in the GUI part, but putting them here
    means that you have all the thread controls in a single place.
    """
    def __init__(self, master):
        """
        Start the GUI and the asynchronous threads. We are in the main
        (original) thread of the application, which will later be used by
        the GUI as well. We spawn a new thread for the worker (I/O).
        """

        self.master = master

        # create the queue
        self.queue = queue.Queue()

        # set up the GUI
        self.gui = Gui(master,
                       self.queue,
                       self.startApplication,
                       self.stopApplication)

        # Set up the thread to do asynchronous I/O
        # More threads can also be created and used, if necessary
        self.running = 0
        
        # Start the periodic call in the GUI to check if the queue contains
        # anything
        self.periodicCall()

    def periodicCall(self):
        """
        Check every 200 ms if there is something new in the queue.
        """
        if self.running:
            self.gui.processIncoming()
        if not self.running:
            # This is the brutal stop of the system. You may want to do
            # some cleanup before actually shutting it down.
            print("not running")
        self.master.after(200, self.periodicCall)

    def workerThread(self):
       
        game = GameOfLife.GameOfLife(self.gui.dim)
        generation = 0
        while self.running:
            print("generation", generation)
            if generation == 0:
                msg = game.old_grid
            else:
                time.sleep(0.5)
                game.update_grid()
                msg = game.new_grid
            generation += 1
            self.queue.put(msg)

    def stopApplication(self):
        self.running = 0
        with self.queue.mutex:
            self.queue.queue.clear()
        print("stopped")

    def startApplication(self):
        self.running = 1
        self.thread = threading.Thread(target=self.workerThread)
        self.thread.start()
        print("started")

if __name__== '__main__':
    rand = random.Random()
    root = tkinter.Tk()
    root.title('Conway\'s Game of Life')
    client = ThreadedClient(root)
    root.mainloop()

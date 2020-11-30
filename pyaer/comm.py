"""Communication Module.

This script includes class definitions for communication
between processes. Example usage is to have a process for
fetching data from the event cameras and other processes for
processing the data.
The communication protocol is implemented through zeromq package.

Author: Yuhuang Hu
Email : yuhuang.hu@ini.uzh.ch
"""

from __future__ import print_function, absolute_import

import os
import time
import subprocess
import zmq
from threading import Thread, Event


class EventPublisher(object):
    def __init__(self, device, port, topic=b''):
        """EventPublisher.

        # Arguments
            device: A DVS/DAVIS/DYNAP-SE device.
                This is a valid device that has been opened.
            port : int
                port number
        """

        self.port = str(port)
        self.device = device
        self.topic = topic

        # initialize socket for publisher
        self.init_socket()

    def init_socket(self):
        """Initialize zmq socket, override for your own use."""
        self.context = zmq.Context.instance()
        self.socket = self.context.socket(zmq.PUB)

        self.socket.bind("tcp://*:{}".format(self.port))
        time.sleep(1)

    def process_data(self, data):
        """Pre-process data object.

        # Arguments
            data: to be processed data.
                This is publisher side pre-process,
                could be some very low latency processing.
                Simply return the data for now.
        """
        return data

    def send_data(self):
        """Publish data main loop.

        Reimplement to your need.
        """
        while True:
            try:
                data = self.device.get_data()

                data = self.process_data(data)

                self.socket.send_multipart(
                    [self.topic, data])
            except KeyboardInterrupt:
                break


class EventSubscriber(object):
    def __init__(self, port, topic=b''):
        """EventSubscriber.

        # Arguments
            port : int
                port number
        """
        self.port = str(port)
        self.topic = topic

        # initialize socket for subscriber
        self.init_socket()

    def init_socket(self):
        """Initialize zmq socket, override for your own use."""
        self.context = zmq.Context.instance()
        self.socket = self.context.socket(zmq.SUB)

        self.socket.setsockopt(zmq.SUBSCRIBE, self.topic)
        self.socket.connect("tcp://localhost:{}".format(self.port))

    def process_data(self, data):
        """Process data object.

        # Arguments
            data: to be processed data.
                This is subscriber side pre-process,
                could be some specific processing.
                Simply return the data for now.
        """
        return data

    def recv_data(self):
        """Subscribe data main loop.

        Reimplement to your need.
        """
        while True:
            topic, data = self.socket.recv_multipart()

            data = self.process_data(data)


class DaemonProcess(Thread):
    def __init__(self, port):
        super().__init__()

        self.port = port
        self.event = Event()
        self.daemon = True

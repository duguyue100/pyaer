"""Communication Module.

This script includes class definitions for communication
between processes. Example usage is to have a process for
fetching data from the event cameras and other processes for
processing the data.
The communication protocol is implemented through zeromq package.

The design principle is similar to ROS where there is a hub for
central scheduling, a group of publishers for sending data, and
a group of subscribers to get/process data.

Author: Yuhuang Hu
Email : yuhuang.hu@ini.uzh.ch
"""

from __future__ import print_function, absolute_import

import os
import sys
import time
import json
import subprocess
from threading import Thread, Event
import numpy as np
import zmq

from pyaer import log


class AERHub(object):
    def __init__(self, url="tcp://127.0.0.1",
                 hub_pub_port=5099,
                 hub_sub_port=5100,
                 aer_hub_name="PyAER Message Hub"):
        """AER Hub.

        A central relay that allows multiple publisher and
        subscriber to use a common port.
        """
        self.url = url
        self.aer_hub_name = aer_hub_name
        self.hub_pub_port = hub_pub_port
        self.hub_sub_port = hub_pub_port
        self.hub_pub_url = url+":{}".format(hub_pub_port)
        print(self.hub_pub_url)
        self.hub_sub_url = url+":{}".format(hub_sub_port)

        # logger
        self.logger = log.get_logger(
            aer_hub_name, log.INFO, stream=sys.stdout)

        # Initialize sockets
        self.init_socket()

    def init_socket(self):
        """Initialize zmq socket, override for your own use."""
        self.context = zmq.Context.instance()

        self.hub_pub = self.context.socket(zmq.XPUB)
        self.hub_sub = self.context.socket(zmq.XSUB)

        self.hub_pub.bind(self.hub_pub_url)
        self.hub_sub.bind(self.hub_sub_url)

        self.poller = zmq.Poller()
        self.poller.register(self.hub_pub, zmq.POLLIN)
        self.poller.register(self.hub_sub, zmq.POLLIN)

        self.logger.info("="*50)
        self.logger.info("{} Initialized.".format(self.aer_hub_name))
        self.logger.info("="*50)
        self.logger.info("Subscribe message at {}".format(self.hub_pub_url))
        self.logger.info("Publish message at {}".format(self.hub_sub_url))

    def run(self):
        while True:
            try:
                events = dict(self.poller.poll())

                if self.hub_pub in events:
                    data = self.hub_pub.recv_multipart()
                    self.hub_pub.send_multipart(data)
                elif self.hub_sub in events:
                    data = self.hub_sub.recv_multipart()
                    self.hubsub.send_multipart(data)
            except KeyboardInterrupt:
                self.logger.info("{} Existing...".format(self.aer_hub_name))
                break


class AERPublisher(object):
    def __init__(self, device,
                 url="tcp://127.0.0.1",
                 port=5100, topic=b''):
        """AERPublisher.

        # Arguments
            device: A DVS/DAVIS/DYNAP-SE device.
                This is a valid device that has been opened.
            port : int
                port number
        """
        # AER device
        self.device = device

        self.topic = topic
        self.url = url
        self.port = port
        self.pub_url = url+":{}".format(port)

        # initialize socket for publisher
        self.init_socket()

    def init_socket(self):
        """Initialize zmq socket, override for your own use."""
        self.context = zmq.Context.instance()
        self.socket = self.context.socket(zmq.PUB)

        self.socket.bind(self.pub_url)
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

    def pack_np_array(self, data_array):
        """Pack numpy array for sending.

        # Arguments
            data_array: numpy.ndarray
                the numpy array to append.

        # Returns
            packed_data_array: list
                The array and its data type, shape information.
        """
        if data_array is None:
            return [b'None', b'None']

        md = dict(
            dtype=str(data_array.dtype),
            shape=data_array.shape)

        return [data_array, bytes(json.dumps(md), "utf-8")]

    def pack_data(self, data):
        """Packing DVS or DAVIS data.

        This function sends all outputs (assume everything is open),
        if you only need to send part of the data,
        simply override this function

        # Arguments
            data: tuple
                The data to pack for sending.
                The resulting data list is ordered.

        # Returns
            packed_data: list
                the data to send.
                DAVIS LIST ORDER:
                    - polarity events
                    - special events
                    - frame timestamps
                    - frames
                    - imu events
                The number of events are all omitted.

                DVS LIST ORDER:
                    - polarity events
                    - special events
        """

        packed_data = [self.topic]
        if len(data) == 8:
            # DAVIS
            packed_data += self.pack_np_array(data[0])  # polarity events
            packed_data += self.pack_np_array(data[2])  # special events
            packed_data += self.pack_np_array(data[4])  # frame time stamps
            packed_data += self.pack_np_array(data[5])  # frames
            packed_data += self.pack_np_array(data[6])  # imu events
        else:
            # DVS128
            packed_data += self.pack_np_array(data[0])  # polarity events
            packed_data += self.pack_np_array(data[2])  # special events

        return packed_data

    def run(self):
        """Publish data main loop.

        Reimplement to your need.
        """
        while True:
            try:
                data = self.device.get_event()
                if data is not None:
                    data = self.pack_data(data)

                    data = self.process_data(data)

                    self.socket.send_multipart(data)
            except KeyboardInterrupt:
                self.close()
                break

    def close(self):
        """Properly close the socket."""
        self.device.shutdown()


class AERSubscriber(object):
    def __init__(self, url="tcp://127.0.0.1",
                 port=5099, topic=b''):
        """AERSubscriber.

        # Arguments
            port : int
                port number
        """
        self.url = url
        self.port = port
        self.sub_url = url+":{}".format(port)
        self.topic = topic

        # initialize socket for subscriber
        self.init_socket()

    def init_socket(self):
        """Initialize zmq socket, override for your own use."""
        self.context = zmq.Context.instance()
        self.socket = self.context.socket(zmq.SUB)

        self.socket.setsockopt(zmq.SUBSCRIBE, self.topic)
        self.socket.connect(self.sub_url)

    def process_data(self, data):
        """Process data object.

        # Arguments
            data: to be processed data.
                This is subscriber side pre-process,
                could be some specific processing.
                Simply return the data for now.
        """
        return data

    def unpack_np_array(self, packed_data_array):
        """Unpack a numpy array list from buffer.

        # Arguments
            packed_data_array: list
                two element list, the first is a data array buffer,
                the second is attributes to reconstruct array.
        # Returns
            unpacked_data_array: numpy.ndarray
                the reconstructed array.
        """
        assert len(packed_data_array) == 2

        try:
            md = json.loads(packed_data_array[1])

            buf_array = memoryview(packed_data_array[0])
            return np.frombuffer(
                buf_array, dtype=md['dtype']).reshape(md['shape'])
        except Exception:
            return None

    def unpack_data(self, packed_data):
        """Packing DVS or DAVIS data.

        This function sends all outputs (assume everything is open),
        if you only need to send part of the data,
        simply override this function

        # Arguments
            packed_data: list
                the data to send.
                DAVIS LIST ORDER:
                    - polarity events
                    - special events
                    - frame timestamps
                    - frames
                    - imu events

                DVS LIST ORDER:
                    - polarity events
                    - special events

        # Arguments
            unpacked_data: tuple
                unpacked data
                The resulting data list is ordered.
        """

        unpacked_data = [packed_data[0]]
        if len(packed_data) == 11:
            # DAVIS
            unpacked_data.append(
                self.unpack_np_array(packed_data[1:3]))  # polarity events
            unpacked_data.append(
                self.unpack_np_array(packed_data[3:5]))  # special events
            unpacked_data.append(
                self.unpack_np_array(packed_data[5:7]))  # frame time stamps
            unpacked_data.append(
                self.unpack_np_array(packed_data[7:9]))  # frames
            unpacked_data.append(
                self.unpack_np_array(packed_data[9:11]))  # imu events
        else:
            # DVS128
            unpacked_data.append(
                self.unpack_np_array(packed_data[1:3]))  # polarity events
            unpacked_data.append(
                self.unpack_np_array(packed_data[3:5]))  # special events

        return unpacked_data

    def run(self):
        """Subscribe data main loop.

        Reimplement to your need.
        """
        while True:
            data = self.socket.recv_multipart()

            data = self.unpacked_data(data)

            data = self.process_data(data)


class AERHDF5Saver(object):
    def __init__(self):
        """AERHDF5Saver.

        A high performance AER HDF5 saver for events.

        """
        pass


class AERZarrSaver(object):
    def __init__(self):
        """AERZarrSaver.

        A high performance AER Zarr saver for events.

        """
        pass


class DaemonProcess(Thread):
    def __init__(self, port):
        super().__init__()

        self.port = port
        self.event = Event()
        self.daemon = True

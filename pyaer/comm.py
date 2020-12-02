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
from pyaer.utils import get_nanotime


def encode_topic_name(topic_names, to_byte=True):
    """Create topic name.

    Mainly used for creating a topic name for publisher.

    # Arguments
        topic_names: list
            a list of strings
    # Returns
        topic_name: byte string
            the topic name separated by "/"
    """
    topic_name = "/".join(topic_names)
    if to_byte is True:
        return topic_name.encode("utf-8")
    else:
        return topic_name


def decode_topic_names(topic_name):
    """Separate topic names.

    # Arguments
        topic_name: byte string
            subscribed topic name

    # Returns
        topic_names: list
            a list of strings
    """
    tmp_topic_name = topic_name.decode("utf-8")

    return tmp_topic_name.split("/")


def create_timestamp_group_name(topic_name, timestamp):
    """Create timestamp group name.

    This is a preferred way to create timestamped group name
    when needed. E.g.,

    topic_name = b'davis-1/imu_event'
    timestamp = b'1606830270019276544'

    This function returns:

    group_name = 'davis-1/1606830270019276544/imu_event'

    # Arguments
        topic_name: byte string
            topic name byte string to be decoded
        timestamp: byte string
            time stamp coded in byte string

    # Returns
        group_name: string
            the timestamp group name
    """
    topic_names = decode_topic_names(topic_name)

    return encode_topic_name(
        [topic_names[0], timestamp.decode("utf-8"),
         topic_names[1]], to_byte=False)


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
                    self.hub_sub.send_multipart(data)
                elif self.hub_sub in events:
                    data = self.hub_sub.recv_multipart()
                    self.hub_pub.send_multipart(data)
            except KeyboardInterrupt:
                self.logger.info("{} Existing...".format(self.aer_hub_name))
                break


class AERPublisher(object):
    def __init__(self, device=None,
                 url="tcp://127.0.0.1",
                 port=5100, master_topic=''):
        """AERPublisher.

        Topics are organized in the following way:
        1. There is a master topic name, e.g., davis-1
        2. Each type of data has its own topic, displayed as
            "master topic name/data type", e.g.,
            "davis-1/polarity_events", "davis-1/frame_events", etc.
        3. Each data packet is tagged with timestamps in nanosecs (wall clock).
           To limit number of topics, this is a part of data instead of
           a topic name.
        4. On the receiving end. For hierarchical data structure such
           as HDF5 and Zarr, the grouping strategy is:
            "master topic name/timestamp/data type"
        5. When saving, ensure ordering.
        6. "/" is a defined separator, do not use in topic name.

        # Arguments
            device: A DVS/DAVIS/DYNAP-SE device.
                This is a valid device that has been opened.
            url: str
                tcp address
            port : int
                port number connected by publisher
            master_topic : str
                the master topic name, such as davis-1
                This is usually a device level identifier.
                There can be sub-topics under this identifier
        """
        # AER device
        self.device = device

        self.master_topic = master_topic
        self.url = url
        self.port = port
        self.pub_url = url+":{}".format(port)

        # initialize socket for publisher
        self.init_socket()

    def init_socket(self):
        """Initialize zmq socket, override for your own use."""
        self.context = zmq.Context.instance()
        self.socket = self.context.socket(zmq.PUB)

        self.socket.connect(self.pub_url)
        time.sleep(1)

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

        return [data_array, json.dumps(md).encode("utf-8")]

    def pack_data_by_topic(self, data_topic_name, timestamp, packed_data_list):
        """Packing data by its topic name.

        # Arguments
            data_topic_name: str
                the topic name for this data.
                E.g., polarity_events, frame_events, imu_events
            timestamp: byte string
                a byte string
            packed_data_list: byte list
                a list of packed data without topic name

        # Returns:
            packed_data: byte list
                a list of packed data ready to be sent.
        """
        return [encode_topic_name([self.master_topic, data_topic_name]),
                timestamp]+packed_data_list

    def pack_polarity_events(self, timestamp, packed_event,
                             data_topic_name="polarity_events"):
        """Pack polarity events."""
        return self.pack_data_by_topic(
            data_topic_name, timestamp, packed_event)

    def pack_frame_events(self, timestamp, packed_event, frame_timestamp,
                          data_topic_name="frame_events"):
        """Pack frame events.

        timestamp is the packet level nano second resolution tag.
        frame_timestamp is the list of timestamps for frames supplied
            by the device.
        """
        return self.pack_data_by_topic(
            data_topic_name, timestamp, packed_event+frame_timestamp)

    def pack_imu_events(self, timestamp, packed_event,
                        data_topic_name="imu_events"):
        return self.pack_data_by_topic(
            data_topic_name, timestamp, packed_event)

    def pack_special_events(self, timestamp, packed_event,
                            data_topic_name="special_events"):
        return self.pack_data_by_topic(
            data_topic_name, timestamp, packed_event)

    def run(self, verbose=False):
        """Publish data main loop.

        Reimplement to your need.
        """
        while True:
            try:
                data = self.device.get_event()
                timestamp = get_nanotime()
                if data is not None:
                    # You can manipulate data here before sending,
                    # note that this is a publisher side
                    # pre-processing, it may slowdown the publishing rate.

                    # send polarity events
                    polarity_data = self.pack_polarity_events(
                        timestamp,
                        self.pack_np_array(data[0]))
                    self.socket.send_multipart(polarity_data)

                    if verbose:
                        print(polarity_data[0].decode("utf-8"),
                              timestamp.decode("utf-8"))

                    # send special events
                    special_data = self.pack_special_events(
                        timestamp,
                        self.pack_np_array(data[2]))
                    self.socket.send_multipart(special_data)

                    if verbose:
                        print(special_data[0].decode("utf-8"))

                    if len(data) > 4:
                        # DAVIS related device

                        # send frame events
                        frame_data = self.pack_frame_events(
                            timestamp,
                            self.pack_np_array(data[5]),
                            self.pack_np_array(data[4]))
                        self.socket.send_multipart(frame_data)

                        if verbose:
                            print(frame_data[0].decode("utf-8"))

                        # send IMU events
                        imu_data = self.pack_imu_events(
                            timestamp,
                            self.pack_np_array(data[6]))
                        self.socket.send_multipart(imu_data)

                        if verbose:
                            print(imu_data[0].decode("utf-8"))
            except KeyboardInterrupt:
                self.close()
                break

    def close(self):
        """Properly close the socket."""
        self.device.shutdown()


class AERSubscriber(object):
    def __init__(self, url="tcp://127.0.0.1",
                 port=5099, topic=''):
        """AERSubscriber.

        A subscriber can subscribe to a specific topic or all
        topics. When received a message, it needs to unpack
        the first two elements: topic name and timestamp

        When saving, make sure the naming strategy is:
        "master topic name/timestamp/data type"

        # Arguments
            url: str
                address to subscribe
            port: int
                port number to listen
            topic: string
                set to "" (default) to listen everything.
                subscribe to specific topics otherwise
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

        self.socket.setsockopt(zmq.SUBSCRIBE, self.topic.encode("utf-8"))
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

    def unpack_data_name(self, data_id_infos, topic_name_only=False):
        """Get either data packet topic name or identifier."""
        if topic_name_only is True:
            return data_id_infos[0].decode("utf-8")

        return create_timestamp_group_name(
            data_id_infos[0], data_id_infos[1])

    def unpack_array_data_by_name(self, packed_data):
        """Unpack a data packet.

        A standard packed data has the following format:
        [topic_name, timestamp, rest of data]

        # Arguments
            packed_data: byte list
                data to be unpacked.

        # Returns
            unpacked_data: list
                [data_identifier (str), data]
        """
        data_identifier = self.unpack_data_name(packed_data[:2])

        array_data = self.unpack_np_array(packed_data[2:])

        return data_identifier, array_data

    def unpack_polarity_events(self, packed_polarity_events):
        return self.unpack_array_data_by_name(packed_polarity_events)

    def unpack_special_events(self, packed_special_events):
        return self.unpack_array_data_by_name(packed_special_events)

    def unpack_frame_events(self, packed_frame_events):
        data_identifier = self.unpack_data_name(packed_frame_events[:2])

        frame_data = self.unpack_np_array(packed_frame_events[2:4])
        frame_ts_data = self.unpack_np_array(packed_frame_events[4:])

        return data_identifier, frame_data, frame_ts_data

    def unpack_imu_events(self, packed_imu_events):
        return self.unpack_array_data_by_name(packed_imu_events)

    def run(self, verbose=True):
        """Subscribe data main loop.

        Reimplement to your need.
        """
        while True:
            data = self.socket.recv_multipart()

            topic_name = self.unpack_array_data_by_name(
                data[:2], topic_name_only=True)

            # you can select some of these functions to use
            if "polarity" in topic_name:
                data_id, polarity_events = self.unpack_polarity_events(data)
            elif "special" in topic_name:
                data_id, special_events = self.unpack_special_events(data)
            elif "frame" in topic_name:
                data_id, frame_events, frame_ts = \
                    self.unpack_frame_events(data)
            elif "imu" in topic_name:
                data_id, imu_events = self.unpack_imu_events(data)

            # your processing pipe line here
            data = self.process_data(data)


class AERHDF5Saver(object):
    def __init__(self):
        """AERHDF5Saver.

        A high performance AER HDF5 saver for events.

        WARNING: The use of latest lib version is intended for
        better performance in IO. This may made the saved volume
        not compatible with older libraries.

        """
        pass


class AERZarrSaver(object):
    def __init__(self):
        """AERZarrSaver.

        A high performance AER Zarr saver for events.

        """
        pass


class AERProcess(Thread):
    def __init__(self, cmd, daemon=True):
        """AER Process.

        # Arguments
            cmd: list
                command list that can be processed by subprocess module.
        """
        super().__init__()

        self.event = Event()
        self.daemon = daemon

        self.cmd = cmd
        self.program_name = cmd[0]

    def create_process(self):
        pid = subprocess.Popen(self.cmd)
        time.sleep(3)
        assert pid.poll() is None, 'Process {} launch failed'.format(
            self.program_name)

        return pid

    def run(self):
        pid = self.create_process()

        while not self.event.is_set():
            time.sleep(1)
            assert pid.poll() is None, "Process {} was killed".format(
                self.program_name)

        pid.terminate()
        pid.communicate()

    def stop(self):
        self.event.set()
        self.join()

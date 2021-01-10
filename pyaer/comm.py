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

import sys
import time
import json
import subprocess
import signal
from collections import OrderedDict
from datetime import datetime
import numpy as np
import zmq
import h5py
try:
    import zarr
except Exception:
    pass

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


class Publisher(object):
    def __init__(self, url="tcp://127.0.0.1",
                 port=5100, master_topic="",
                 name=""):
        """Publisher.

        A abstract publisher implementation.

        # Arguments
            url: str
                tcp address
            port : int
                port number connected by publisher
            master_topic : str
                the master topic name, such as davis-1
                This is usually a device level identifier.
                There can be sub-topics under this identifier
            name : str
                the name of the publisher
        """

        self.url = url
        self.port = port
        self.pub_url = url+":{}".format(port)
        self.master_topic = master_topic
        self.name = name

        self.logger = log.get_logger(
            "Publisher-{}".format(self.name),
            log.INFO, stream=sys.stdout)

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

    def run(self):
        """Implement your publishing method."""
        raise NotImplementedError


class AERPublisher(Publisher):
    def __init__(self, device=None,
                 url="tcp://127.0.0.1",
                 port=5100, master_topic='',
                 name=""):
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
            name : str
                the name of the publisher
        """
        super(AERPublisher, self).__init__(
            url=url, port=port, master_topic=master_topic,
            name=name)
        # AER device
        self.device = device

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
                        self.logger.debug("{} {}".format(
                            polarity_data[0].decode("utf-8"),
                            timestamp.decode("utf-8")))

                    # send special events
                    special_data = self.pack_special_events(
                        timestamp,
                        self.pack_np_array(data[2]))
                    self.socket.send_multipart(special_data)

                    if verbose:
                        self.logger.debug(
                            "{}".format(special_data[0].decode("utf-8")))

                    if len(data) > 4:
                        # DAVIS related device

                        # send frame events
                        frame_data = self.pack_frame_events(
                            timestamp,
                            self.pack_np_array(data[5]),
                            self.pack_np_array(data[4]))
                        self.socket.send_multipart(frame_data)

                        if verbose:
                            self.logger.debug("{}".format(
                                frame_data[0].decode("utf-8")))

                        # send IMU events
                        imu_data = self.pack_imu_events(
                            timestamp,
                            self.pack_np_array(data[6]))
                        self.socket.send_multipart(imu_data)

                        if verbose:
                            self.logger.debug("{}".format(
                                imu_data[0].decode("utf-8")))
            except KeyboardInterrupt:
                self.logger.info("Shutting down publisher {}".format(
                    self.name))
                self.close()
                break

    def close(self):
        """Properly close the socket."""
        self.device.shutdown()


class Subscriber(object):
    def __init__(self, url, port, topic, name):
        """Subscriber.

        A general implementation of subscriber.

        # Arguments
            url : str
                address to subscribe
            port : int
                port number to listen
            topic : string
                set to "" (default) to listen everything.
                subscribe to specific topics otherwise
            name : str
                the name of the subscriber
        """
        self.url = url
        self.port = port
        self.sub_url = url+":{}".format(port)
        self.topic = topic
        self.name = name

        self.logger = log.get_logger(
            "Subscriber-{}".format(self.name),
            log.INFO, stream=sys.stdout)

        # initialize socket for subscriber
        self.init_socket()

    def init_socket(self):
        """Initialize zmq socket, override for your own use."""
        self.context = zmq.Context.instance()
        self.socket = self.context.socket(zmq.SUB)

        self.socket.setsockopt(zmq.SUBSCRIBE, self.topic.encode("utf-8"))
        self.socket.connect(self.sub_url)

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

    def run(self):
        raise NotImplementedError


class AERSubscriber(Subscriber):
    def __init__(self, url="tcp://127.0.0.1",
                 port=5099, topic='', name=""):
        """AERSubscriber.

        A subscriber can subscribe to a specific topic or all
        topics. When received a message, it needs to unpack
        the first two elements: topic name and timestamp

        When saving, make sure the naming strategy is:
        "master topic name/timestamp/data type"

        # Arguments
            url : str
                address to subscribe
            port : int
                port number to listen
            topic : string
                set to "" (default) to listen everything.
                subscribe to specific topics otherwise
            name : str
                the name of the subscriber
        """
        super(AERSubscriber, self).__init__(
            url=url, port=port, topic=topic, name=name)

    def process_data(self, data):
        """Process data object.

        # Arguments
            data: to be processed data.
                This is subscriber side pre-process,
                could be some specific processing.
                Simply return the data for now.
        """
        return data

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


class PubSuber(object):
    def __init__(self, url="tcp://127.0.0.1",
                 pub_port=5100,
                 pub_topic="", pub_name="",
                 sub_port=5099,
                 sub_topic="", sub_name=""):
        """Publisher-Subscriber.

        This is a shell implementation.

        Intend to use as a processing unit.
        First subscribe on a topic, process it, and then publish to
        a topic

        """
        self.url = url
        self.pub_port = pub_port
        self.pub_topic = pub_topic
        self.pub_name = pub_name
        self.sub_port = sub_port
        self.sub_topic = sub_topic
        self.sub_name = sub_name

        self.logger = log.get_logger(
            "PubSuber-{}-{}".format(self.pub_name, self.sub_name),
            log.INFO, stream=sys.stdout)

    def run(self):
        raise NotImplementedError


class AERHDF5Saver(object):
    def __init__(self, filename, mode="w-", libver="latest"):
        """AERHDF5Saver.

        A high performance AER HDF5 saver for events.

        WARNING: The use of latest lib version is intended for
        better performance in IO. This may made the saved volume
        not compatible with older libraries.

        # Arguments
        filename: str
            the absolute path of the file to be written.

        mode: str
            opening mode. We use "w-" as default, it means
            "create file, fail if exists".
            You can change to "w" or "a" for your own need.

        libver: str
            We use "latest" as default to get high performance,
            However, you can see this page to choose the HDF5 library version,
            See this page for detailed explanation:
            https://docs.h5py.org/en/stable/high/
                file.html?highlight=libver#file-version
        """
        self.filename = filename
        self.libver = libver

        self.aer_file = h5py.File(
            name=filename, mode=mode, libver=libver,
            rdcc_nbytes=50*1024**2,  # 50MB Cache
            track_order=True  # Follow the order of the message
            )

    def save(self, data_name, data):
        """Save data to a dataset.

        # Arguments
        data_name: str
            the dataset's name, usually has format
            master_topic/timestamp/topic
        data : numpy.ndarray
            the dataset's content.
        """
        # save data
        self.aer_file.create_dataset(
            data_name, data=data)

    def close(self):
        self.aer_file.close()


class AERHDF5Reader(object):
    def __init__(self, filename, mode="r", libver="latest",
                 use_wall_clock=True):
        """AERHDF5Reader.

        A high performance AER HDF5 Reader for events.

        WARNING: The use of latest lib version is intended for
        better performance in IO. This may made the saved volume
        not compatible with older libraries.

        We use the wall clock to determine the timestamp.

        # Arguments
        filename: str
            the absolute path of the file to be read.

        mode: str
            opening mode. We use "r" as default, it means
            "read-only, file must exist".
            You can change to "r+" or "a" for your own need.

        libver: str
            We use "latest" as default to get high performance,
            However, you can see this page to choose the HDF5 library version,
            See this page for detailed explanation:
            https://docs.h5py.org/en/stable/high/
                file.html?highlight=libver#file-version
        """
        self.filename = filename
        self.libver = libver

        self.aer_file = h5py.File(
            name=filename, mode=mode, libver=libver,
            rdcc_nbytes=50*1024**2,  # 50MB Cache
            track_order=True  # Follow the order of the message
            )

        self.logger = log.get_logger(
            "HDFReader", log.INFO, stream=sys.stdout)

        self.logger.info("Getting Device Keys")
        self.device_keys = self.aer_file.keys()

        self.logger.info("Getting group keys")
        self.group_keys = OrderedDict()

        for device in self.device_keys:
            self.group_keys[device] = self.aer_file[device].keys()

    def get_devices(self):
        return self.device_keys

    def get_keys(self):
        return self.group_keys

    def get_frame(self, device_name, group_name):
        """Get frame events at this packet."""

        try:
            frame_events = \
                self.aer_file[device_name][group_name]["frame_events"][()]

            if frame_events.size == 0:
                return None

            return frame_events
        except Exception:
            return None

    def get_polarity_events(self, device_name, group_name):
        """Get polarity events.

        Note that the time is converted to nanosecs.
        """
        try:
            polarity_events = \
                self.aer_file[device_name][group_name]["polarity_events"][()]

            # modify time
            polarity_events[:, 0] -= polarity_events[0, 0]
            polarity_events[:, 0] *= 1000
            polarity_events[:, 0] += int(group_name)

            return polarity_events
        except Exception:
            return None

    def get_imu_events(self, device_name, group_name):
        """Get IMU events."""
        try:
            imu_events = \
                self.aer_file[device_name][group_name]["imu_events"][()]

            # modify time
            imu_events[:, 0] -= imu_events[0, 0]
            imu_events[:, 0] *= 1000
            imu_events[:, 0] += float(group_name)

            return imu_events
        except Exception:
            return None

    def get_special_events(self, device_name, group_name):
        """Get spcial events."""
        try:
            special_events = \
                self.aer_file[device_name][group_name]["special_events"][()]

            # modify time
            special_events[:, 0] -= special_events[0, 0]
            special_events[:, 0] *= 1000
            special_events[:, 0] += int(group_name)

            return special_events
        except Exception:
            return None

    def get_time(self, device_name, group_name):
        return int(group_name)

    def get_wall_time(self, nanosecs):
        dt = datetime.fromtimestamp(float(nanosecs)/1e9)
        return dt.strftime('%Y-%m-%dT%H:%M:%S.%f')

    def close(self):
        self.aer_file.close()


class AERZarrSaver(object):
    def __init__(self, filename, mode="w-"):
        """AERZarrSaver.

        A high performance AER Zarr saver for events.

        """
        self.filename = filename

        self.aer_file = zarr.open_group(
            store=filename, mode=mode)

    def save(self, data_name, data):
        """Save data to a dataset.

        # Arguments
        data_name: str
            the dataset's name, usually has format
            master_topic/timestamp/topic
        data : numpy.ndarray
            the dataset's content.
        """
        # save data
        self.aer_file.create_dataset(
            data_name, data=data)

    def close(self):
        self.aer_file.close()


class AERProcess(object):
    def __init__(self, cmd):
        """AER Process.

        # Arguments
            cmd: list
                command list that can be processed by subprocess module.
        """
        super().__init__()

        self.cmd = cmd
        self.program_name = cmd[0]

    def create_process(self):
        pid = subprocess.Popen(self.cmd)
        time.sleep(0.5)
        assert pid.poll() is None, 'Process {} launch failed'.format(
            self.program_name)

        return pid

    def run(self):
        self.pid = self.create_process()

    def stop(self):
        self.pid.send_signal(signal.SIGINT)
        self.pid.terminate()
        self.pid.communicate()

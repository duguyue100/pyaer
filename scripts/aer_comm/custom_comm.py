"""Custom Publisher and Subscriber.

Author: Yuhuang Hu
Email : yuhuang.hu@ini.uzh.ch
"""

from __future__ import print_function, absolute_import

import time
import cv2

from pyaer.comm import AERPublisher, AERSubscriber


class CustomPublisher(AERPublisher):

    def __init__(self, device, url, port, master_topic, name, **kwargs):
        super().__init__(
            device=device, url=url, port=port, master_topic=master_topic,
            **kwargs)

    def run_once(self, verbose=False):
        data = self.device.get_event()

        if data is not None:
            #  data = self.pack_frame_events
            #
            #  self.socket.send_multipart(data)

            t = time.localtime()

            curr_time = time.strftime("%H:%M:%S", t)

            print("Publishing {}".format(curr_time))


class CustomSubscriber(AERSubscriber):

    def __init__(self, url, port, topic, name, **kwargs):
        super().__init__(url, port, topic, name, **kwargs)

        for arg in kwargs.values():
            print(arg)

    def run_once(self, verbose=False):
        data = self.socket.recv_multipart()

        topic_name = self.unpack_data_name(
            data[:2], topic_name_only=True)

        if "frame" in topic_name:
            data_id, frame_events, frame_ts = \
                self.unpack_frame_events(data)

            if frame_events is not None:
                try:
                    cv2.imshow(
                        "frame",
                        cv2.cvtColor(
                            frame_events[0],
                            cv2.COLOR_BGR2RGB))
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        return
                except Exception:
                    pass


class DVViewerSubscriber(AERSubscriber):

    def __init__(self, url, port, topic, name, **kwargs):
        super().__init__(url, port, topic, name, **kwargs)

        for arg in kwargs.values():
            print(arg)

    def run_once(self, verbose=False):
        data = self.socket.recv_multipart()

        topic_name = self.unpack_data_name(
            data[:2], topic_name_only=True)

        if "frame" in topic_name:
            data_id, frame_events, frame_ts = \
                self.unpack_frame_events(data)

            if frame_events is not None:
                try:
                    cv2.imshow(
                        "frame",
                        cv2.cvtColor(
                            frame_events[0],
                            cv2.COLOR_BGR2RGB))
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        return
                except Exception:
                    pass

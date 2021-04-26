"""Event Container.

Motivation: After the events are read from the event packet,
it's difficult to use and less informative to return them
as single variables, therefore, I decide to introduce a
container that can manage all the returned Python variables.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""


class EventContainer(object):
    """Event container that packs everything."""

    def __init__(self, pol_events,
                 special_events=None,
                 frames=None, frames_ts=None,
                 imu_events=None):
        """Event Container.

        # Arguments
            pol_events: numpy.ndarray
                polarity events array
            special_events: numpy.ndarray
                special events
            frames: numpy.ndarray
                APS frame events
            frames_ts: numpy.ndarray
                APS frame time stamp
            imu_events: numpy.ndarray
                IMU events
        """

        self.pol_events = pol_events
        self.num_pol_events = 0 if pol_events is None else \
            pol_events.shape[0]
        self.compute_event_stats()

        self.special_events = special_events
        self.num_special_events = None if special_events is None else \
            special_events.shape[0]

        self.frames = frames
        self.frames_ts = frames_ts

        self.imu_events = imu_events
        self.num_imu_events = None if imu_events is None else \
            imu_events.shape[0]

    def compute_event_stats(self):
        """Calculate event stats."""
        self.pol_event_duration = None
        self.pol_event_rate = None

        self.num_valid_pol_events = None
        self.num_invalid_pol_events = None
        self.valid_pol_events_rate = None
        self.invalid_pol_events_rate = None

        if self.num_pol_events > 1:
            # in seconds
            self.pol_event_duration = \
                (self.pol_events[-1, 0]-self.pol_events[0, 0])/1e6

            self.pol_event_rate = self.num_pol_events/self.pol_event_duration

            # additional stats if has background filter
            if self.pol_events.shape[1] == 5:
                self.num_valid_pol_events = self.pol_events[:, -1].sum()
                self.num_invalid_pol_events = \
                    self.num_pol_events-self.num_valid_pol_events

                self.valid_pol_events_rate = \
                    self.num_valid_pol_events/self.pol_event_duration
                self.invalid_pol_events_rate = \
                    self.num_invalid_pol_events/self.pol_event_duration

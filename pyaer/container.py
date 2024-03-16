from __future__ import annotations

from typing import Optional

import numpy as np


class EventContainer(object):
    """Event container that packs everything.

    Args:
        pol_events: polarity events array.
        special_events: special events.
        frames: APS frame events.
        frames_ts: APS frame time stamp.
        imu_events: IMU events.
    """

    def __init__(
        self,
        pol_events: np.ndarray,
        special_events: Optional[np.ndarray] = None,
        frames: Optional[np.ndarray] = None,
        frames_ts: Optional[np.ndarray] = None,
        imu_events: Optional[np.ndarray] = None,
    ) -> None:
        self.pol_events = pol_events
        self.num_pol_events = 0 if pol_events is None else pol_events.shape[0]
        self.compute_event_stats()

        self.special_events = special_events
        self.num_special_events = (
            None if special_events is None else special_events.shape[0]
        )

        self.frames = frames
        self.frames_ts = frames_ts

        self.imu_events = imu_events
        self.num_imu_events = None if imu_events is None else imu_events.shape[0]

    def compute_event_stats(self) -> None:
        """Calculate event stats."""
        self.pol_event_duration = None
        self.pol_event_rate = None

        self.num_valid_pol_events = None
        self.num_invalid_pol_events = None
        self.valid_pol_events_rate = None
        self.invalid_pol_events_rate = None

        if self.num_pol_events > 1:
            # in seconds
            self.pol_event_duration = (
                self.pol_events[-1, 0] - self.pol_events[0, 0]
            ) / 1e6

            self.pol_event_rate = self.num_pol_events / self.pol_event_duration

            # additional stats if has background filter
            if self.pol_events.shape[1] == 5:
                self.num_valid_pol_events = self.pol_events[:, -1].sum()
                self.num_invalid_pol_events = (
                    self.num_pol_events - self.num_valid_pol_events
                )

                self.valid_pol_events_rate = (
                    self.num_valid_pol_events / self.pol_event_duration
                )
                self.invalid_pol_events_rate = (
                    self.num_invalid_pol_events / self.pol_event_duration
                )

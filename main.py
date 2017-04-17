from datetime import datetime, timedelta, timezone
import logging
from typing import Optional, Iterable, Callable, TypeVar

logging.basicConfig(level=logging.DEBUG)

from aw_client import ActivityWatchClient

T = TypeVar("T")


def find(pred: Callable[[T], Optional[T]], seq: Iterable[T]):
    for elem in seq:
        if pred(elem):
            return elem
    return None


class Detector:
    def __init__(self):
        self.client = ActivityWatchClient("status-checker")
        buckets = self.client.get_buckets()
        self.window_bucket_id = find(lambda bucket_id: "window" in bucket_id, buckets.keys())

    def detect(self, filter_str: str):
        dt_1min_ago = datetime.now(timezone.utc) - timedelta(minutes=1)
        last_events = self.client.get_events(self.window_bucket_id, start=dt_1min_ago.isoformat(), limit=1)
        if last_events:
            last_event = last_events[0]
            # print(last_event.timestamp)
            # print(last_event.labels)

            # This assert fails sometimes, something is wrong somewhere...
            assert dt_1min_ago < last_event.timestamp

            found = find(lambda label: filter_str in label, last_event.labels)
            if found:
                print("{} seems to be active!".format(filter_str))


detector = Detector()
detector.detect("status-checker")
detector.detect("zsh")
detector.detect("chrome")

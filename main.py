import logging
from typing import Optional, Iterable, Callable, TypeVar

logging.basicConfig(level=logging.DEBUG)

from aw_core.models import Event
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

    def get_bucket_id(self, type):
        # TODO: We need a better way to query buckets
        # TODO: Doesn't care about hostname
        buckets = self.client.get_buckets()
        # print(buckets)
        window_bucket = find(lambda bucket: bucket["type"] == type and "testing" not in bucket["id"], buckets.values())
        if window_bucket is None:
            raise Exception("Bucket not found")
        return window_bucket["id"]

    # TODO: Move to aw-client?
    def get_last_event(self, bucket_id):
        last_events = self.client.get_events(bucket_id, limit=1)
        if last_events:
            return last_events[0]

    def detect(self, bucket_id: str, filter_str: str) -> Optional[Event]:
        last_event = self.get_last_event(bucket_id)
        if last_event is None:
            raise Exception("no event found")
        # print(last_event)

        return last_event if find(lambda label: filter_str in label.lower(), last_event.labels) else None


if __name__ == "__main__":
    activities = ["aw-detector", "fish", "vim", "chrome"]

    detector = Detector()

    window_bucket_id = detector.get_bucket_id(type="currentwindow")
    afk_bucket_id = detector.get_bucket_id(type="afkstatus")

    not_afk = detector.detect(afk_bucket_id, "not-afk")
    for activity in activities:
        if not_afk and detector.detect(window_bucket_id, activity):
            print("{} seems to be active!".format(activity))

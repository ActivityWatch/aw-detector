import logging
from typing import Optional, Iterable, Callable, TypeVar, Dict

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
    def __init__(self) -> None:
        self.client = ActivityWatchClient("status-checker")

    # TODO: Move to aw-client?
    # TODO: Doesn't care if the event was old (as can happen if you have a dead watcher)
    def _get_last_event(self, bucket_id: str) -> Event:
        last_events = self.client.get_events(bucket_id, limit=1)
        if last_events:
            return last_events[0]
        else:
            raise Exception("no event found")

    def get_bucket_id(self, type: str) -> str:
        # TODO: Doesn't care about hostname
        # TODO (maybe): Create a better way to query buckets
        buckets = self.client.get_buckets()
        # print(buckets)
        window_bucket = find(lambda bucket: bucket["type"] == type and "testing" not in bucket["id"], buckets.values())
        if window_bucket is None:
            raise Exception("Bucket not found")
        return window_bucket["id"]

    def detect(self, bucket_id: str, filter_str: str) -> Optional[Event]:
        last_event = self._get_last_event(bucket_id)
        return last_event if find(lambda label: filter_str in label.lower(), last_event.labels) else None


class LockableDetector(Detector):
    """Identical to Detector, but provides a lock on the last event in a bucket to do multiple checks on the same event"""

    def __init__(self) -> None:
        Detector.__init__(self)
        self.last_event_locked = False
        self.locked_last_events = {}  # type: Dict[str, Event]

    def __enter__(self):
        self.last_event_locked = True

    def __exit__(self, *args, **kwargs):
        self.last_event_locked = False
        self.locked_last_events = {}

    def _get_last_event(self, bucket_id: str) -> Optional[Event]:
        if self.last_event_locked:
            if bucket_id not in self.locked_last_events:
                self.locked_last_events[bucket_id] = Detector._get_last_event(self, bucket_id)
            return self.locked_last_events[bucket_id]
        else:
            return Detector._get_last_event(self, bucket_id)


example_activities = ["aw-detector", "fish", "vim", "chrome", "python"]


def lockable_detector_example() -> None:
    """
    Without the lockable detector, a new currentwindow event right at the time of detection might invalidly
    detect more than one "activity" since multiple calls to `detect` would do one event fetch each.

    An alternative solution would be to write a new function `detect_many` that could be used to detect
    multiple activities with a single event fetch.
    """
    detector = LockableDetector()

    window_bucket_id = detector.get_bucket_id(type="currentwindow")
    afk_bucket_id = detector.get_bucket_id(type="afkstatus")

    not_afk = detector.detect(afk_bucket_id, "not-afk")
    with detector:
        for activity in example_activities:
            if not_afk and detector.detect(window_bucket_id, activity):
                print("{} seems to be active!".format(activity))


def main():
    lockable_detector_example()


if __name__ == "__main__":
    main()

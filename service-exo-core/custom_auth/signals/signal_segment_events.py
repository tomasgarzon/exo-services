from utils.segment import SegmentAnalytics


def signal_segment_event_user_save_handler(sender, instance, created, *args, **kwargs):
    SegmentAnalytics.identify(instance)

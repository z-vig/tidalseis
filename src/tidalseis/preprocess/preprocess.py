from obspy.core import Trace  # type: ignore


def preprocess(tr: Trace):
    tr.detrend()
    tr.filter()
    tr.remove_response()

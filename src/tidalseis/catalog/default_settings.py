from .triggering import TriggeringConfig
from .preprocess import PreprocessingConfig

DEFAULT_TRIGGERING = TriggeringConfig(
    trigger_type="classicstalta",
    trigger_on_threshold=6,
    trigger_off_threshold=5,
    num_coincident_stations=2,
    long_term_average_length=60,
    short_term_average_length=2,
)

DEFAULT_PREPROCESSING = PreprocessingConfig(
    detrend=True,
    filter_type="Bandpass",
    low_frequency_cutoff=5,
    high_frequency_cutoff=20,
)

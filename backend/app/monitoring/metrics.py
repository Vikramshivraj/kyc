from prometheus_client import Counter, Gauge, Histogram


jobs_processed_total = Counter(
    "kyc_jobs_processed_total",
    "Total number of successfully processed KYC jobs"
)

jobs_failed_total = Counter(
    "kyc_jobs_failed_total",
    "Total number of failed KYC jobs"
)

jobs_processing = Gauge(
    "kyc_jobs_processing",
    "Number of KYC jobs currently being processed"
)

job_processing_seconds = Histogram(
    "kyc_job_processing_seconds",
    "Time spent processing a KYC job"
)
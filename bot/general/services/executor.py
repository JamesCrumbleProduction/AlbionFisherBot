from concurrent.futures import ThreadPoolExecutor

SCANNER_EXECUTOR: ThreadPoolExecutor = ThreadPoolExecutor(
    max_workers=2, thread_name_prefix='SCANNER_EXECUTOR'
)

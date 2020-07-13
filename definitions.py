import os
import logging


def get_logger():
  crawler_log = logging.getLogger('crawler')
  crawler_log.setLevel(logging.DEBUG)
  stream_handler = logging.StreamHandler()
  stream_handler.setFormatter(logging.Formatter('[%(asctime)s][%(levelname)s][%(filename)s:%(lineno)d] %(message)s'))
  crawler_log.addHandler(stream_handler)

  return crawler_log


log = get_logger()
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCE_DIR = os.path.join(ROOT_DIR, 'resources')
ERROR_FILE_DIR = os.path.join(ROOT_DIR, 'error_pages')
TEST_RESOURCE_DIR = os.path.join(ROOT_DIR, 'tests', 'test_resources')

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

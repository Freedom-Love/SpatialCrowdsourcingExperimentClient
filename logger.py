import logging



logger = logging.getLogger('default')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('default.log')
formatter = logging.Formatter('%(asctime)s - %(module)s(%(filename)s:%(lineno)d) - %(levelname)s - %(message)s')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)

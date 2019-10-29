import logging

class LogClass:

    def __init__(self,name,file):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        fh = logging.FileHandler(file)
        fh.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def __del__(self):
        pass


    def info(self,message):
        self.logger.info(message)


    def debug(self,message):
        self.logger.debug(message)




























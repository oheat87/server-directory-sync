import json
import logging
import datetime
import os
import traceback

BASE_DIR=os.path.abspath(os.getcwd())
LOG_DIR=os.path.join(BASE_DIR,"saveLog")

JSON_LOGGING_FORMAT=json.dumps({
    "time": "%(asctime)s",
    "filename":"%(filename)s",
    "process":"%(name)s",
    "logType":"%(levelname)s",
    "flag":"%(flag)s"
}, indent=4)

class JsonLoggingFilter(logging.Filter):
    def __init__(self, name, filename, flag):
        logging.Filter.__init__(self, name=name)
        self.filename = filename
        self.flag = flag

    def filter(self, record):
        record.filename = self.filename
        record.flag = self.flag
        if hasattr(record, "stack_msg") and hasattr(record, "stack_trace"):
            return True

        if record.exc_info:
            ex_type, ex_val, ex_stack = record.exc_info
            stack_list = []
            for stack in traceback.extract_tb(ex_stack):
                stack_list.append("%s" % stack)

            record.stack_msg = ex_val
            record.stack_trace = "#".join(stack_list)
        else:
            record.stack_msg, record.stack_trace = "", ""

        return True


class JsonFormatter(logging.Formatter):
    def __init__(self, fmt=None):
        logging.Formatter.__init__(self, fmt=fmt)


    def format(self, record):
        record.message = record.getMessage()
        filename, flag=record.message.split("/")
        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)

        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info).replace("\n", " ").replace("\"", "'")

        s = self.formatMessage(record)

        # add filename & flag
        s=eval(s)
        s["filename"]=filename
        s["flag"]=flag

        return str(s)


class JsonLogger(logging.Logger):
    logger = None
    level = None
    mode = None

    def __init__(self, time, process, level=logging.INFO, console_level=logging.INFO, mode="w"):
        self.name = time
        self.time = time

        logging.Logger.__init__(self, name=process)

        self.logger = logging.Logger(name=process)
        self.logger.setLevel(level)

        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)
        log_file_path = os.path.join(LOG_DIR, "%s.json" % time)
        json_logging_filter = JsonLoggingFilter(time,filename=None,flag=None)
        json_formatter = JsonFormatter(JSON_LOGGING_FORMAT)

        # file log
        file_handle = logging.FileHandler(log_file_path, mode=mode)
        file_handle.setLevel(level)
        file_handle.setFormatter(json_formatter)
        file_handle.addFilter(json_logging_filter)

        # console log
        console_handle = logging.StreamHandler()
        console_handle.setLevel(console_level)
        console_handle.setFormatter(json_formatter)
        console_handle.addFilter(json_logging_filter)

        self.logger.addHandler(file_handle)
        self.logger.addHandler(console_handle)

    def getLogger(self):
        return self.logger

    def setLevel(self, level):
        self.logger.level = level


def run(process):
    time = str(datetime.datetime.now()).replace(":", "-")[:-3]
    my_logger = JsonLogger(f"{time}",process).getLogger()

    return my_logger

    # my_logger.info(info)

    #try:
    #    open('./my-log.json', 'rb')
    #except FileNotFoundError as e:
    #    my_logger.exception("file exception", exc_info=e)

from loguru import logger
from types import SimpleNamespace

DEBUG = False
INFO = False
WARNING = False
TRACE = False
ERROR = False

name_space = SimpleNamespace(**{"uid": "| internal call |"})
req = SimpleNamespace(**{"state": name_space})

def setMode(mode):
    if "debug" in mode:
        global DEBUG
        DEBUG=True
    if "info" in mode:
        global INFO
        INFO = True
    if "warning" in mode:
        global WARNING
        WARNING=True
    if "trace" in mode:
        global TRACE
        TRACE= True
    if "error" in mode:
        global ERROR
        ERROR = True


def file_path(path):
    # every day new log file is created
    # 3 log files will be kept, older files will be deleted
    logger.add(path, rotation="00:10", retention="5 days")

def info(msg=str,request=req):
    if INFO :
        logger.opt(ansi=True).info(f"<bg #2f3640><fg #fbc531> {request.state.uid} </fg #fbc531></bg #2f3640> {msg}")

def debug(msg=str,request=req):
    if DEBUG:
        logger.opt(ansi=True).debug(f"<bg #2f3640><fg #fbc531> {request.state.uid} </fg #fbc531></bg #2f3640> {msg}")

def warning(msg=str,request=req):
    if WARNING:
        logger.opt(ansi=True).warning(f"<bg #2f3640><fg #fbc531> {request.state.uid} </fg #fbc531></bg #2f3640> {msg}")

def trace(msg=str,request=req):
    if TRACE:
        logger.opt(ansi=True).trace(f"<bg #2f3640><fg #fbc531> {request.state.uid} </fg #fbc531></bg #2f3640> {msg}")

def error(msg=str,request=req):
    if ERROR:
        logger.opt(ansi=True).error(f"<bg #2f3640><fg #fbc531> {request.state.uid} </fg #fbc531></bg #2f3640> {msg}")


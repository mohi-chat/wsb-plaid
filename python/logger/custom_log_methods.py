from fastapi import Request
from datetime import datetime
import pytz

from logger import log

log.file_path("logs/backend_log_{time:DD_MM_YY!UTC}.log") # log file path
log.setMode(['error','info'])

from pydantic import BaseModel

fmt = '%Y-%m-%d %H:%M:%S %Z%z'

class FunctionLog(BaseModel):
    error_msg : str
    exception_msg: str
    function: str
    parent_route: str
    add_info: str


def logAPIError(request: Request):  # the request parameter is necessary while using log function
    timestamp = datetime.now(tz=pytz.utc).strftime(fmt)
    log.error({"Error Message": request.state.error_msg, "Exception Message": request.state.exception_msg, "Method": request.method, "Route": request.url.path, "UserId": request.state.user_id,  "DateTime": timestamp}, request)

def logFunctionError(fnLog: FunctionLog):
    timestamp = datetime.now(tz=pytz.utc).strftime(fmt)
    fnLog['timestamp'] = timestamp
    log.error(fnLog)
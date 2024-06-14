import logging
from threading import local as Local
import time

from metering_billing.utils import get_client_ip

logger = logging.getLogger(__name__)
local = Local()


class LogRequestMiddleware:
    logger = logging.getLogger("log.request")

    def get_log_message(self, request, response, duration):
        user = getattr(request, 'user', None)
        message = 'method=%s path=%s status=%s duration=%sms' % (
            request.method, request.get_full_path(), response.status_code, int(duration * 1000)
        )
        if user:
            message += f' user={user.id} username={user.username}'

        client_ip = get_client_ip(request)
        if client_ip:
            message += f' client_ip={client_ip}'

        return message

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        local.start_time = time.time()
        response = self.get_response(request)
        duration = time.time() - local.start_time
        self.logger.info(self.get_log_message(request, response, duration))
        return response

"""Query MTA's API in an interval and update them accordingly in Redis."""

import requests
import redis
import time

from containerlog import get_logger

logger = get_logger()
cache = redis.Redis(host='redis', port=6379)

STATUS_DELAY = 'Delays'
STATUS_OK = 'OK'

READ_INTERVAL = 60

URL = 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/camsys%2Fsubway-status.json'
API_KEY = 'D0XYDKjtK55mrKe6Lu7OJ1OSxQpStvz39s9OmDLt'


def init_cache():
    r = new_request()
    for route in r.get('routeDetails'):
        if route.get('statusDetails') is not None:
            rid = route.get('route')
            cache.set(rid, STATUS_OK)
            cache.set(f'{rid}_downtime', 0)


def new_request():
    return requests.get(URL, headers={'x-api-key': API_KEY}).json()


def check(details):
    for status in details:
        if status.get('statusSummary') == STATUS_DELAY:
            return STATUS_DELAY

    return STATUS_OK


def run():
    while True:
        r = new_request()
        last_updated = r.get('lastUpdated')
        cache.set('last_updated', last_updated)
        logger.debug('last updated timestamp', last_updated=last_updated)

        for route in r.get('routeDetails'):
            if route.get('statusDetails') is not None:
                rid = route.get('route')
                status = check(route.get('statusDetails'))

                if cache.get(rid) == STATUS_DELAY and status == STATUS_OK:
                    logger.info(f'Line {rid} is now recovered', route=rid, status=status)

                if cache.get(rid) == STATUS_OK and status == STATUS_DELAY:
                    logger.info(f'Line {rid} is experiencing delays', route=rid, status=status)

                if status == STATUS_DELAY:
                    cache.set(rid, STATUS_DELAY)
                    cache.incrby(f'{rid}_downtime', READ_INTERVAL)
                else:
                    cache.set(rid, STATUS_OK)

                logger.debug('updating cache', route=rid, status=status)

        time.sleep(READ_INTERVAL)


if __name__ == "__main__":
    init_cache()
    run()

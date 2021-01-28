"""Server definitions"""

import redis
import time

from fastapi import FastAPI

app = FastAPI()

cache = redis.Redis(host='redis', port=6379)
start_time = time.time()


@app.get('/status/{route_number}')
def status(route_number: str):
    payload = {
        'status': 'Not Found',
        'last_updated': cache.get('last_updated')
    }

    status = cache.get(route_number)
    if status is not None:
        payload['status'] = status

    return payload


@app.get('/uptime/{route_number}')
def uptime(route_number: str):
    total_time = time.time()-start_time

    payload = {
        'total_time': total_time,
        'downtime': 0,
        'uptime': 0,
    }

    downtime = cache.get(f'{route_number}_downtime')
    if downtime is not None:
        payload['downtime'] = int(downtime)
        payload['uptime'] = 1-(int(downtime)/total_time)

    return payload

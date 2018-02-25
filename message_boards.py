import redis
from  redis_connect import connectRedis
import constants

conn = connectRedis()

conn.set('foo', 'bar')
value = conn.get('foo')
print(value)
value = conn.get('sports')
print(value)



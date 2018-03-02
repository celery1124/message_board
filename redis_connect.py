import redis
import constants

def connectRedis():
	connection = redis.Redis(
    host=constants.redis_host,
    port=constants.redis_port)
	return connection


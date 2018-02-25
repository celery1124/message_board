import redis
import constants

def connectRedis():
	connection = redis.Redis(
    host=constants.host,
    port=constants.port)
	return connection


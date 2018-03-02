import redis
from  redis_connect import connectRedis
import constants
import time
from mongo_connect import connectMongo
import pymongo
import json
import pprint

def print_usage():
	print 'usage:\tselect <board_name> (select board)'
	print '\t read (read messages in current board)'
	print '\t write <message> (write message to current board)'
	print '\t listen (listen to current board)'
	print '\t stop (stop listening)'
	print '\t quit'

mongo_collection = connectMongo()
conn = connectRedis()
board = ''

def event_handler(msg):  
    print(msg)
    print(msg['data'])

while True:
	cmd = raw_input('> ')
	cmd = cmd.split()
	if len(cmd) > 2:
		print_usage()
		continue
	if len(cmd) == 2 and cmd[0] == 'select':
		board = cmd[1]
	elif len(cmd) == 1 and cmd[0] == 'read':
		if len(board) == 0:
			print 'please choose a board using select command'
		else:
			message = conn.get(board)
			print message
	elif len(cmd) == 2 and cmd[0] == 'write':
		if len(board) == 0:
			print 'please choose a board using select command'
		else:
			conn.append(board, cmd[1])
	elif len(cmd) == 1 and cmd[0] == 'listen':
		if len(board) == 0:
			print "please choose a board using select comman"
		else:
			pubsub = conn.pubsub()
			pubsub.psubscribe(**{'__keyspace@0__:'+board: event_handler})  
			thread = pubsub.run_in_thread(sleep_time=0.01)
	elif len(cmd) == 1 and cmd[0] == 'quit':
		print 'bye bye'
		break
	else:
		print_usage()

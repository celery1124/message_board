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

def list_all(collection):
  RQ0 = collection.find()
  for data in RQ0:
    pprint.pprint(data)

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
			## first try read from redis
			numOfMsg = int(conn.get(board))
			print numOfMsg
			# use pipeline to shorten latancy increase throughput
			pipe = conn.pipeline()
			for i in range(1,numOfMsg+1):
				pipe.get(board+'_'+str(i))
			ret = pipe.execute()
			print ret

			## then read message not in redis from mongodb
			for i in range(i,numOfMsg+1):
				if ret[i-1] == None:
					RQ = mongo_collection.find({"board":board,"id":str(i)})
					pprint.pprint(RQ)
				else:
					print ret[i-1]

	elif len(cmd) == 2 and cmd[0] == 'write':
		if len(board) == 0:
			print 'please choose a board using select command'
		else:
			## first handle redis side
			# increase the counter
			suffix = conn.incr(board,1)
			print board+'_'+str(suffix)
			print cmd[1]
			# set key associate with counter
			conn.set(board+'_'+str(suffix), cmd[1])

			## then handle mongodb side
			doc = {'board':board, 'id':str(suffix), 'message':cmd[1]}
			mongo_collection.insert(doc)
			mongo_collection.find()
			list_all(mongo_collection)

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

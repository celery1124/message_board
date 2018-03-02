import redis
from  redis_connect import connectRedis
import constants
import time
from mongo_connect import connectMongo
import pymongo
import json

def print_usage():
	print 'usage:\tselect <board_name> (select board)'
	print '\t read (read messages in current board)'
	print '\t write <message> (write message to current board)'
	print '\t listen (listen to current board)'
	print '\t stop (stop listening)'
	print '\t quit'

def event_handler(msg):
	op = msg['data']
	if op == 'set':
	    key = msg['channel']
	    key = key.split(':')
	    print  conn.get(key[1])

mongo_collection = connectMongo()
conn = connectRedis()
board = ''
listen_flag = False

while True:
	try:
		if listen_flag == False:
			cmd = raw_input('> ')
		else:
			cmd = raw_input('')
		cmd = cmd.split()
	except EOFError:
		print("Stop listening")
		listen_flag = False
		pubsub.unsubscribe('__keyspace@0__:'+board+'_*')
		thread.stop()
		continue
	
	if len(cmd) > 2:
		print_usage()
		continue
	if len(cmd) == 2 and cmd[0] == 'select':
		board = cmd[1]
	elif len(cmd) == 1 and cmd[0] == 'read':
		if len(board) == 0:
			print 'Please choose a board using select command'
		else:
			## first try read from redis
			numOfMsg = int(conn.get(board))
			# use pipeline to shorten latancy increase throughput
			pipe = conn.pipeline()
			for i in range(1,numOfMsg+1):
				pipe.get(board+'_'+str(i))
			ret = pipe.execute()

			## then read message not in redis from mongodb
			for i in range(1,numOfMsg+1):
				if ret[i-1] == None:
					RQ = mongo_collection.find({"board":board,"id":str(i)})
					for data in RQ:
						print data['message']
				else:
					print ret[i-1]

	elif len(cmd) == 2 and cmd[0] == 'write':
		if len(board) == 0:
			print 'Please choose a board using select command'
		else:
			## first handle redis side
			# increase the counter
			suffix = conn.incr(board,1)
			# set key associate with counter
			conn.set(board+'_'+str(suffix), cmd[1])

			## then handle mongodb side
			doc = {'board':board, 'id':str(suffix), 'message':cmd[1]}
			mongo_collection.insert(doc)

			print "write "+cmd[1]+" success!"

	elif len(cmd) == 1 and cmd[0] == 'listen':
		listen_flag = True
		if len(board) == 0:
			print "Please choose a board using select command"
		else:
			pubsub = conn.pubsub()
			pubsub.psubscribe(**{'__keyspace@0__:'+board+'_*': event_handler})  
			thread = pubsub.run_in_thread(sleep_time=0.01)
	elif len(cmd) == 1 and cmd[0] == 'stop':
		print 'Stop listening'
		listen_flag = False
		pubsub.unsubscribe('__keyspace@0__:'+board+'_*')
		thread.stop()
	elif len(cmd) == 1 and cmd[0] == 'quit':
		try:
			pubsub.unsubscribe('__keyspace@0__:'+board+'_*')
		    thread.stop()
		except NameError:
			tread = None
		print 'bye bye'
		break
	else:
		print_usage()

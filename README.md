## Prerequisite
1. [Redis](https://redis.io/).  
2. [MongoDB](https://www.mongodb.com/)  

## Instructions to run the code
1. Start Redis locally with notification enabled  
Install Redis in your local machine and add Redis binary directory to your environment
path, then in the shell run (or you can run in the binary directory similarly)
```shell
$ redis-server --notify-keyspace-events KEA
```
2) Run application
In the application directory, run
```shell
$ python message_boards.py
```
3) Usage instructions
The application provides enough error handling and are friendly to user.


Detailed implementation notes please reference the [report](./report.pdf)
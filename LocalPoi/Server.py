import pymongo
import json
import socket
import threading
"""
this is the local version of poi , 
this version should only be used to build profiles on
your local machine , for remote use check the 'CommandClientRemote' client
"""
class MongoHandler:
		def __init__(self):
		self.client = pymongo.MongoClient("mongodb://localhost:27017/")
		self.db = client['persons']
		self.collection = self.db["profiles"]
	def create_profile(data,client):
		del data["type"]
		result = self.collection.insert_one(data)
		status = result.acknowledged 
		if status == True :#if the insertion was successful
			client.send("ACCEPTED_CREATION".encode('ascii'))
		else:
			client.send("error".encode("ascii"))


				
			
		client.send("ACCEPTED_CREATION".encode("ascii"))
	def send_profile_data(data,client):
		pass #send client profile data size and then the data

class Server :
	def __init__(self):
		self.host = '127.0.0.1' #localhost
		self.port = 50222
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.running = True
		self.mongo_handler = MongoHandler()

	def route_type(self, data,client,thread_running,addr):
		try:
			if data["type"] == "PROFILE_CREATION" :
				self.mongo_handler.create_profile(data,client)
			elif data["type"] == "PROFILE_REQUEST":
				self.mongo_handler.send_profile_data(data,client)
				
		except:
			print("")

		
	def client_thread(self,client , addr ):
		thread_running = True
		while thread_running == True :
			data_size = int(client.recv(100).decode("ascii"))
			data = client.recv(data_size).decode("ascii")
			new_dict = json.loads(data)
			self.route_type(new_dict,client,thread_running,addr)

	def start_server():
		while self.running == True:
			client , addr = self.server.accept()
			#start new thread to avoid blocking new connections!
			thread = threading.Thread(target =self.client_thread, args = (client,addr,))
			thread.start()



			


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
        self.db = self.client['persons']
        self.collection = self.db["profiles"]

    def send_crud_status(self,client,message,status):
        if status == True :#if the crud operation was successful
            client.send(message.encode('ascii'))
        else:
            client.send("error".encode("ascii"))

    def create_profile(self,data,client):
        del data["type"]
        result = self.collection.insert_one(data)
        status = result.acknowledged 
        self.send_crud_status(client,"ACCEPTED_CREATION",status)
    
    def send_profile_data(self,data,client):
        del data["type"] # we only need the first/last name for query
        profile = self.collection.find_one(data,{"_id" :0 })

        if profile == None:
            client.send("error".encode("ascii"))
        else:
            formatted_profile = json.dumps(profile) #convert to string
            data_size = len(formatted_profile.encode("ascii"))
            client.send("PROFILE_FOUND".encode("ascii"))
            client.send(str(data_size).encode("ascii")) #send size of the data for clean data transfer
            response = client.recv(70).decode("ascii")

            if response == "GOT":
                client.send(formatted_profile.encode("ascii"))

    def edit_profile_data(self,data,client):
        query = {"firstname" : data["firstname"],
                 "lastname" : data["lastname"]}

        new_value = {"$set" :{data["field"] : data["value"]}}
        status = self.collection.update_one(query,new_value).acknowledged
        self.send_crud_status(client,"SUCCESSFUL_EDIT",status)

    def delete_profile(self,data,client):
        del data["type"]
        status = self.collection.delete_one(data).acknowledged
        self.send_crud_status(client,"DELETION_ACCEPTED",status)

    def add_entry(self,data,client):
        query = {
            "firstname" : data["firstname"],
            "lastname" : data["lastname"]
        }

        path ="entries."+data["label"] #creating a child structure 
        new_value = {"$set" :{path : data["data"]}} #setting new value(must be unique)

        status = self.collection.update_one(query ,new_value  )
        self.send_crud_status(client,"ENTRY_ACCEPTED")
        




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
            elif data["type"] == "PROFILE_EDIT":
                self.mongo_handler.edit_profile_data(data,client)
            elif data["type"] == "REQUEST_DELETION":
                self.mongo_handler.delete_profile(data,client)

                
        except Exception as e:
            print("issue")
            print(e)

        
    def client_thread(self,client , addr ):
        thread_running = True
        while thread_running == True :
            data_size = int(str(client.recv(100).decode("ascii")))
            data = client.recv(data_size).decode("ascii")
            new_dict = json.loads(data)

            if new_dict["type"] == "DICONNECT_":
                thread_running = False
            else:
                self.route_type(new_dict,client,thread_running,addr)

    def start_server(self):
        self.server.bind((self.host,self.port))
        self.server.listen()
        while self.running == True:
            client , addr = self.server.accept()
            #start new thread to avoid blocking new connections!
            thread = threading.Thread(target =self.client_thread, args = (client,addr,))
            thread.start()


if __name__ == '__main__':
    server = Server()
    server.start_server()

            


import pymongo,json,socket,threading,smtplib
from email.message import EmailMessage
"""
this is the local version of poi , 
this version should only be used to build profiles on
your local machine , for remote use check the 'CommandClientRemote' client
"""

class EmailHandler:
    def __init__(self,collection):
        self.collection = collection
    def create_temp_email_data(self):
        cursor =  self.collection.find()
        with open("temp.txt" , "w") as file:
            for profile in cursor:
                file.write(str(profile))

    def temp_data(self):
        with open("temp.txt" , "rb") as file:
            return file.read()


    def send_email(self,data,client):
        self.create_temp_email_data() #getting all the profiles
        msg = EmailMessage()
        msg["Subject"] = 'POI Data'
        msg["From"] = data["sender"]
        msg["To"] = data["receiver"]
        msg.add_attachment(self.temp_data(),maintype = 'text'  , subtype = "plain", filename = "data.txt")
        with smtplib.SMTP_SSL('smtp.gmail.com' ,465) as smtp:
            try:
                smtp.login(data["sender"],self.temp_email_password)
                smtp.send_message(msg)
                client.send("EMAIL_SENT".encode("ascii"))              
            except :
                client.send("ISSUE".encode("ascii"))
                



class MongoHandler:
    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.client['persons']
        self.collection = self.db["profiles"] #main collection
        self.email_collection = self.db["emailconfig"]
        self.breach_collection = self.db["breachconfig"]
        self.ssl_port = 466
        self.email_handler = EmailHandler(self.collection)
    
    def profile_query(self,data):
        query = {"firstname" : data["firstname"],
                 "lastname" : data["lastname"]}
        return query

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
       
        new_value = {"$set" :{data["field"] : data["value"]}}
        status = self.collection.update_one(self.profile_query(data),new_value).acknowledged
        self.send_crud_status(client,"SUCCESSFUL_EDIT",status)

    def delete_profile(self,data,client):
        del data["type"]
        status = self.collection.delete_one(data).acknowledged
        self.send_crud_status(client,"DELETION_ACCEPTED",status)

    def modify_entry(self,data,client,message,set_type,value):
        path ="entries."+data["label"] #creating a child structure 
        new_value = {set_type :{path : value}} #setting new value(must be unique)
        status = self.collection.update_one(self.profile_query(data) ,new_value  ).acknowledged
        self.send_crud_status(client, message,status)
    
    def add_parent_email(self,data,client):
        status = self.email_collection.insert_one({"parentconfigv" : data["email"] , "parentpass" : data["password"]}).acknowledged
        self.send_crud_status(client, "CONFIG_COMPLETE",status)

    def delete_email_recipient(self,data,client):

        status = self.email_collection.delete_one({"nickname" : data["nickname"] })
        self.send_crud_status(client,"EMAIL_RECIPIENT_REMOVED",status)

    def add_email_recipient(self,data,client):
        new_value = {
            "email" : data["email"],
            "nickname": data["email_name"]
        }
        status = self.email_collection.insert_one( new_value).acknowledged
        self.send_crud_status(client,"EMAIL_RECIPIENT_ADDED" , status)

    def email_exists(self,email):
        data = self.email_collection.find_one({"parentconfigv" : email})
        if data == None:
            return False
        else:
            self.email_handler.temp_email_password = data["parentpass"]#avoiding a second query to get password
            self.email_handler.temp_email = data["parentconfigv"]
            return True

    def send_profile_list(self,client):
        data  = list(self.collection.find({} , {"_id" :0 , "firstname":1 , "lastname":1 , "entries":1}))
        if len(data)< 1:
            client.send("50".encode("ascii"))
            client.send("NONE".encode("ascii"))
        else:
            client.send(str(len(json.dumps(data).encode("ascii"))).encode("ascii")) #sending the size of bytes encoded
            client.send(json.dumps(data).encode("ascii")) #sending actual data
    def breach_code(self):
        code = self.breach_collection.find()
        if len(list(code)) < 1 :
            return None

        else:
            return code["breachcode"]

    def breach_delete(self):
        profile_status = self.collection.delete_many({}).acknowledged
        email_status = self.email_collection.delete_many({}).acknowledged
        breach_status = self.breach_collection.delete_many({}).acknowledged
        if profile_status == False or email_status == False or breach_status == False:
            return False
        else:
            return True

    def breach_delete_check(self,client,code):
        if self.breach_code() == None: # there is no code setup
            client.send("error".encode("ascii"))
        else: 
            if self.breach_code() == code: # correct code was entered
                if self.breach_delete() == False: # an error occured
                    client.send("BREACH_PROTOCOL_SUCCESSFUL".encode("ascii"))
                else:
                    client.send("error".encode("ascii"))
            else:
                client.send("error".encode("ascii"))

    def remove_all(self,client,collection):
        if collection == "email" :
            email_status =  self.email_collection.delete_many({}).acknowledged
            self.send_crud_status(client,"DELETED_EVERYTHING",email_status)
        else:
            profile_status =  self.collection.delete_many({}).acknowledged
            self.send_crud_status(client,"DELETED_EVERYTHING",profile_status)

    def change_breach_code(self,client,data):
        if self.breach_code() == data["code"]:#correct code verification
                status = self.breach_collection.update_one({"breachcode": data["code"]} , 
                    {"$set" :{"breachcode":data["newcode"]}}).acknowledged
                self.send_crud_status(client,"BREACH_UPDATED",status)
        else:
            client.send("issue".encode("ascii"))

    def change_email_password(self,client,data):
        status = self.email_collection.find_one({"parentconfigv":data["email"]} , 
            {"$set":{"parentpass":data["newpass"]}}).acknowledged
        self.send_crud_status(client,"PASSWORD_UPDATED",status)

    def send_profiles_to_parent(self,client,data):
        email_data = {
                "sender":data["sender"],
                "receiver": data["receiver"]
        }
        self.email_handler.send_email(email_data)



            


    def filter_recipients(self):
        emails = list(self.email_collection.find())
        for email in emails:
            if "parentconfigv" in email: #the parent email that is used for sending.
                    emails.remove(email)
        return emails

    def send_email_to_all(self,client):
        emails = self.filter_recipients()#list of dictionaries
        for email_entry in emails:
            address = email_entry["email"] # actual email address
            send_email_data = {
                "sender": self.email_handler.temp_email,
                "receiver":address
            }
            self.email_handler.send_email(send_email_data,client)


    def configure_breach(self,client,code):
        if self.breachcode == None:
            status = self.breach_collection.insert_one({"breachcode" : code }).acknowledged
            self.send_crud_status(client,"BREACH_CONFIGED",status)
        else:
            client.send("issue".encode("ascii")) 





class Server :
    def __init__(self):
        self.host = '127.0.0.1' #localhost
        self.port = 50222
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = True
        self.mongo_handler = MongoHandler()



    def routing_third_tier(self,data,client):
            if data["type"] == "EMAIL_RECIPIENT_ADD":
                self.mongo_handler.add_email_recipient(data,client)
            elif data["type"] == "REMOVE_EMAIL_RECIPIENT":
                self.mongo_handler.delete_email_recipient(data,client)
            elif data["type"] == "ALL":
                self.mongo_handler.send_profile_list(client)
            elif data["type"] == "DEL_ALL_EMAILS":
                self.remove_all(client,"email")
            elif data["type"] == "DEL_ALL_PROFILES":
                self.remove_all(client,"profiles")
            elif data["type"] == "BREACHED":
                self.breach_delete_check(client,data["code"])
        

    def routing_second_tier(self,data,client):
            if data["type"] == "DELETE_ENTRY":
                self.mongo_handler.modify_entry(data,client,"ENTRY_DELETED","$unset", "")
            elif data["type"] == "EMAIL_CONFIG":
                self.mongo_handler.add_parent_email(data,client)
            elif data["type"] == "SEND_EMAIL":
                if self.mongo_handler.email_exists(data["sender"]) == True:  
                        self.mongo_handler.email_handler.send_email(data,client)
                else:
                    client.send("EMAIL_DONT_EXIST".encode("ascii"))
            else:
                self.routing_third_tier(data,client)


        
    def route_type(self, data,client):
    
            if data["type"] == "PROFILE_CREATION" :
                self.mongo_handler.create_profile(data,client)
            elif data["type"] == "PROFILE_REQUEST":
                self.mongo_handler.send_profile_data(data,client)
            elif data["type"] == "PROFILE_EDIT":
                self.mongo_handler.edit_profile_data(data,client)
            elif data["type"] == "REQUEST_DELETION":
                self.mongo_handler.delete_profile(data,client)
            elif data["type"] == "ENTRY_REQUEST":
                self.mongo_handler.modify_entry(data,client,"ENTRY_ACCEPTED","$set",data["data"])
            else:
                self.routing_second_tier(data,client) # avoiding long blocks of code


        
    def client_thread(self,client , addr ):
        thread_running = True
        while thread_running == True :
            data_size = int(str(client.recv(100).decode("ascii"))) 
            data = client.recv(data_size).decode("ascii")
            new_dict = json.loads(data)

            if new_dict["type"] == "DICONNECT_":
                thread_running = False
            else:
                self.route_type(new_dict,client)

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

            


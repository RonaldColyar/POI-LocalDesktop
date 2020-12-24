
import socket
import base64
import json
import tkinter
import atexit
from termcolor import colored
from colorama import init
from tkinter import filedialog 





init()#allow colored text to run on windows machines

class ResultWindow:
    
    def __init__(self,master,first,last,location,reason,race,image):

        if image == "NOT_PRESENT":
            self.formatted_image = tkinter.PhotoImage(file = 'defaultimage.png') #anonymous photo

        else:
            self.formatted_image = tkinter.PhotoImage(master = master,data = image)

        formatted_first = "First Name: " + first
        formatted_last = "Last Name: " + last
        formatted_location = "Location: " + location
        formatted_reason = "Why?:" + reason
        formatted_race = "Race/Skin Tone:" + race
        #widgets
        master.config(bg = "#222")
        picture = tkinter.Label(master , image = self.formatted_image,bg = "#222" , fg = "#fff" ).pack()
        first_name = tkinter.Label(master,text = formatted_first,bg = "#222", fg = "#fff",font=("Courier", 20)).pack()
        last_name = tkinter.Label(master,text = formatted_last,bg = "#222", fg = "#fff",font=("Courier", 20)).pack()
        race = tkinter.Label(master,text = formatted_race,bg = "#222", fg = "#fff",font=("Courier", 20)).pack()
        known_location = tkinter.Label(master, text = formatted_location,bg = "#222", fg = "#fff",font=("Courier", 15)).pack()
        reason_why = tkinter.Message(master,text= formatted_reason,bg = "#222", fg = "#fff",font=("Courier", 10)).pack()


    def display_tree(self,data):
        pass
    def gather_tree_entries(self,username):
        request = {
            "type":"tree_data",
            "name":username
                }
        formatted_request  = json.dump(request)
        send_size = len(formatted_request.encode("ascii"))
        self.client.send(send_size)
        self.client.send(formatted_request)
        incoming_size = int(self.client.recv(100).decode("ascii"))
        if incoming_size == 0:
            pass#dont exist
        else:
            data = self.client.recv(incoming_size).decode("ascii")
            self.display_tree(data)

            
        
        
        
"""
    Client Checks the commands by the user and maps
    to the correct function execution/sends requests 
    to the server on the user behalf!
"""
class Client:
    def __init__(self):
        self.running = True
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.connect(('127.0.0.1',50222))
        except:
            self.running = False
            #notifying the server we are disconnecting!
            diconnect_message = {"type":"DISCONNECT_"}
            self.client.send(json.dumps(diconnect_message).encode("ascii")) 
            #update user
            print("Issue Connecting to Your Local Server!!")
            print("Enter to Exit!")


    def display_welcome_message(self):
            path = 'C:/Users/ronald/Git/Git Repos/POI/AsciiArt/Builder.txt'
            with open( path, "r") as file: #ascii art
                for i in file.readlines():
                    print(i)
            print(colored("#Welcome To Persons Of Interest!!" , "green"))
            print("-----------------------------------------------------")
            print(colored("#Build Profiles On Suspicious Characters!","red"))
            print(colored("--help for command listings" , "red"))


    def create_profile(self):
            firstname = input("First Name:")
            lastname = input("Last Name:")
            location = input("Location:")
            reason = input("Reason:")
            race = input("Race/Skin Tone:")
            profile_data = {"type" : "PROFILE_CREATION","firstname" : firstname,"lastname" : lastname,
                         "location" : location,"reason" : reason,"race" : race
                        }
            picture_prompt = input("would you like to include a picture?[y/n]:")
            if picture_prompt == "y" or  picture_prompt == "Y":
               profile_data["image"] =self.select_image()
               self.send_request(profile_data,"profile_creation")
            else:
                profile_data["image"] = "NOT_PRESENT"
                self.send_request(profile_data,"profile_creation")

    def display_profile(self,response):

        new_dict = json.loads(response)
        master = tkinter.Tk()
        result_window = ResultWindow(master,new_dict["firstname"],new_dict["lastname"],
                                     new_dict["location"],new_dict["reason"],new_dict["race"],new_dict["image"])
        master.mainloop()


    def check_profile_exist_reponse(self,response):
        if response == "PROFILE_FOUND":
                data_size = int(str(self.client.recv(70).decode("ascii")))#size
                self.client.send("GOT".encode("ascii"))
                data = self.client.recv(data_size).decode("ascii")
                self.display_profile(data)
        else:
            print("Profile Doesn't exist!")

    def check_status_response(self,response ,server_accept_message,success_message):
        if response == server_accept_message:
                print(success_message)
        else:
                print("Error From Server!")


    def check_response(self,request,response):
        if request == "profile_creation" :
            self.check_status_response(response,"ACCEPTED_CREATION",
                "Profile Successfully Created!! ,View it with the command(view)")
        elif request == "profile_view":
            self.check_profile_exist_reponse(response)
            
        elif request == "profile_deletion":
            self.check_status_response(response,"DELETION_ACCEPTED",colored("Profile Successfully Removed!!" , "red"))
        elif request == "entry_request" :
            self.check_status_response(response,"ENTRY_ACCEPTED" ,
             colored("Entry Successfully Added!! View it with the command(view)" , "green"))


                


    def send_request(self,data,message_type):
        message = json.dumps(data) #json string
        message_size = len(message.encode("ascii")) # get the size for the first message
        self.client.send(str(message_size).encode("ascii")) #sending size
        self.client.send(message.encode("ascii"))#sending real data
        response = self.client.recv(70).decode("ascii")
        self.check_response(message_type,response)

    def select_image(self):
        profile_path = filedialog.askopenfilename( initialdir= "/",title='Persons Image' , filetypes = [("PNG FILES" , "*.png")])
        with open(profile_path, "rb") as file:
            encoded_image = base64.b64encode(file.read()).decode("ascii")
        return encoded_image

    def view_profile(self):
        first_name = input("First Name:")
        last_name = input("Last Name:")
        profile_data = {
            "type" : "PROFILE_REQUEST",
            "firstname":first_name,
            "lastname" :last_name
        }
        self.send_request(profile_data,"profile_view")

    def check_edit_response(self,response):
        if response == "SUCCESSFUL_EDIT":
            print("You Have Successfully Edited The Profile!")
        else:
            print("Issue Editing Profile!")

    
    def send_edit_request(self,edit_data):
        data = json.dumps(edit_data)
        data_size = len(data.encode("ascii"))
        self.client.send(str(data_size).encode("ascii"))
        self.client.send(data.encode("ascii"))
        response = self.client.recv(100).decode("ascii")
        self.check_edit_response(response)

    def edit_profile(self):
        first = input("First Name:")
        last = input("Last Name:")
        field = input("What Field Would you like to edit/update?:")
        if field == "image":
            image = self.select_image()
            edit_data = {
            "type" : "PROFILE_EDIT","firstname" : first,"lastname"  : last,
            "field" : field,"value":image
                }
        else:
            new_value = input(f"New Field Value for {first + '' + last + field}: ")
            edit_data = {
                "type" : "PROFILE_EDIT", "firstname" : first, "lastname"  : last,
                "field" : field,"value":new_value
                  }
        self.send_edit_request(edit_data)


    def delete_profile(self):
        first = input("First Name:")
        last = input("Last Name:")
        confirmation = input("Are you sure?[y/n]")
        if confirmation == "y" or confirmation == "Y":
            delete_data = {
              "type" : "REQUEST_DELETION",
              "firstname" : first,
              "lastname" : last,
            }
            self.send_request(delete_data,"profile_deletion" )
        else:
            print(colored("Aborted Deletion!"))


    def help(self):
        print(colored("[1]","green") 
            + " create-Allows you to create a new profile")
        print(colored("[2]","green") 
            + " delete-Allows you to delete a profile")
        print(colored("[3]","green") 
            + " view-Allows you to view a profile in a gui")
        print(colored("[4]","green") 
            + " edit-Allows you to edit a profile's attribute or add a new attribute!")
        
    def add_entry(self):
        first = input("First Name:")
        last = input("Last Name:")
        label = input("Label of entry(unique):")
        data = input("Data:")
        entry_data = {
            "type": "ENTRY_REQUEST",
            "firstname":first,
            "lastname":last,
            "label" : label,
            "data" : data
        }
        self.send_request(entry_data , "entry_request")


    def command_check(self,command):
        if  command == "create" or command == "1":
            self.create_profile()
        elif command == "view" or command == "3":
            self.view_profile()
        elif command == "edit" or command == "4":
            self.edit_profile()
        elif command == "delete" or command == "2":
            self.delete_profile()
        elif command == "entry":
            self.add_entry()
        elif command == "--help" or command == "help":
            self.help()
        else:
            print("unknow command")




        
        
    def Start(self):
        self.display_welcome_message()
        while self.running == True:
                print(" ")
                print(colored("#Persons Of Interest~","green") + "Version 1.0" )
                command = input(">")
                print(" ")
                self.command_check(command)


client = Client()
client.Start()
        
        


        

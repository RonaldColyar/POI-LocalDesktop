
import socket
import os
import base64
import json
import tkinter
import atexit
import pymsgbox
from tkinter import ttk
from functools import partial
from termcolor import colored
from colorama import init
from tkinter.filedialog import askopenfilename






init()#allow colored text to run on windows machines

class ResultWindow:
    def image_check(self,data):
        if data["image"] == "NOT_PRESENT":
            self.formatted_image = tkinter.PhotoImage(file = 'defaultimage.png') 
            #only display race if there is no photo of subject
            race = tkinter.Label(self.master,text ="Race/Skin Color:"+ data["race"],
                 bg = "#222", fg = "#fff",font=("Courier", 20),relief = "ridge").pack()
        else:
            self.formatted_image = tkinter.PhotoImage(master = self.master,data = data["image"])

    def create_files(self,dir_name):
        try:
            os.mkdir(dir_name)
            with open(dir_name+"/profilepic.png" , "wb") as file:
                file.write(base64.b64decode(self.data["image"]))
            with open(dir_name+"/profiledata.txt" , "w") as file:
                #write all data that isn't the image
                for key in self.data:
                    if key != "image":
                        file.write(key+":"+self.data[key])
                        file.write("\n")

        except :
            pymsgbox.alert(
                text = "directory already exist",
                title = "Issue.." ,
                button = "Ok")
            
        

    def download_profile(self):
        download_window = tkinter.Toplevel()
        heading = tkinter.Label(download_window, 
            text = "Name Of New Directory(for profile content) make sure the directory do not exist!").pack()
        data_input = ttk.Entry(heading)
        data_input.pack()
        download_button = tkinter.Button(download_window, text = "Download" ,
                 command = lambda: self.create_files(data_input))



    
    def __init__(self,master,data):
        self.master = master
        self.image_check(data)
        self.data = data
        #widgets
        master.config(bg = "#222")
        picture = tkinter.Label(master , image = self.formatted_image ,bg = "#222" ).pack()
        download_button = tkinter.Label(master , text = "Download Entry" ,
            bg = "#666", fg = "#fff" ,borderwidth = 0.5 , command = self.download_profile())
        first_name = tkinter.Label(master,text ="First:"+ data["firstname"],
            bg = "#222", fg = "#fff",font=("Courier", 20),relief = "ridge").pack()
        last_name = tkinter.Label(master,text = "Last:"+ data["lastname"],
            bg = "#222", fg = "#fff",font=("Courier", 20),relief = "ridge").pack()
        known_location = tkinter.Label(master, text ="Location:"+ data["location"],
            bg = "#222", fg = "#fff",font=("Courier", 15),relief = "ridge").pack()
        reason_why = tkinter.Message(master,text="Reason For Profile:" +data["reason"],
            bg = "#222", fg = "#fff",font=("Courier", 10),relief = "ridge").pack()
        self.insert_entries(data)

    def insert_entries(self,data):
        #create a button for all entries
        if "entries" in data:
            tkinter.Label(self.master,text="Entries:",
            bg = "#222", fg = "green",font=("Courier", 30),relief = "ridge").pack()
            for key in data["entries"]: 
               tkinter.Button(self.master ,text = key , 
                command = partial(self.display_entry_data,data["entries"][key],key),
                borderwidth = 0.5,
                fg = "#fff" ,
                bg = "#555" ,
                width = 40).pack()

    def display_entry_data(self,data,label) :
        child = tkinter.Toplevel()
        child.config(bg = "#222")
        tkinter.Label(child,text = label+":" , font=("Courier", 30) , fg = "#d3d3d3",bg = "#222" ).pack()
        tkinter.Message(child,text = data , font=("Courier", 20), fg = "#d3d3d3",bg = "#222").pack()
        child.mainloop()


        
        
        
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


    #profiles
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


    def display_profile(self,response):

        new_dict = json.loads(response)
        master = tkinter.Tk()
        result_window = ResultWindow(master,new_dict)
        master.mainloop()


    def check_profile_exist_reponse(self,response):
        if response == "PROFILE_FOUND":
                data_size = int(str(self.client.recv(70).decode("ascii")))#size
                self.client.send("GOT".encode("ascii"))
                data = self.client.recv(data_size).decode("ascii")
                self.display_profile(data)
        else:
            print("Profile Doesn't exist!")


    def view_profile(self):
        first_name = input("First Name:")
        last_name = input("Last Name:")
        profile_data = {
            "type" : "PROFILE_REQUEST",
            "firstname":first_name,
            "lastname" :last_name
        }
        self.send_request(profile_data,"profile_view")
    def display_all_profiles(self, incoming_data):
           profiles= json.loads(incoming_data)
           for profile in profiles:
                print("First Name:"+profile["firstname"])
                print("Last Name:"+profile["lastname"])
                if "entries" in profile:
                    print("Entries:"+str(len(list(profile["entries"])))) # number of entries
                print("__________________________")


    def gather_full_list(self):
        formatted_request = json.dumps({"type" : "ALL"})
        data_size = len(formatted_request)
        #send size and then data
        self.client.send(str(data_size).encode("ascii"))
        self.client.send(formatted_request.encode("ascii"))
        #receive size and then data
        incoming_data_size = self.client.recv(60).decode("ascii")
        incoming_data = self.client.recv(int(incoming_data_size)).decode("ascii")
        if incoming_data == "issue":
            print("issue gathering list")
        elif incoming_data == "NONE":
            print("no profiles")
        else:
            self.display_all_profiles(incoming_data)

    # Request routing
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
        elif request == "entry_deletion":
            self.check_status_response(response,"ENTRY_DELETED" ,
             colored("Entry Successfully Deleted!! View the profile with the command(view)" , "green"))
        elif request == "email_config":
             self.check_status_response(response,"CONFIG_COMPLETE" ,
             colored("Email Configuration Complete! You can now broadcast your data to your target audience!" , "green"))
        elif request == "email_recipient_add":
            self.check_status_response(response,"EMAIL_RECIPIENT_ADDED",
               colored("Recipient Added!" , "green")  )
        elif request ==  "email_recipient_remove":
            self.check_status_response(response,"EMAIL_RECIPIENT_REMOVED",
               colored("Recipient Removed!" , "green")  )
        elif request == "breached":
            self.check_status_response(response,"BREACH_PROTOCOL_SUCCESSFUL",
               colored("Breach Protocol Complete!! Check the success with (VIEW ALL)" , "green")  )
        elif request == "send_email":
            print("Make sure you turn on to use this feature without errors : 'Less secure app access'")
            self.check_status_response(response,"EMAIL_SENT",
               colored("Email Successful Sent!!" , "green")  )






    def send_request(self,data,message_type):
        message = json.dumps(data) #json string
        message_size = len(message.encode("ascii")) # get the size for the first message
        self.client.send(str(message_size).encode("ascii")) #sending size
        self.client.send(message.encode("ascii"))#sending real data
        response = self.client.recv(70).decode("ascii")
        self.check_response(message_type,response)



    #EDIT SECTION
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




    def help(self):
        print(colored("[1]","green") 
            + " create-Allows you to create a new profile")
        print(colored("[2]","green") 
            + " delete-Allows you to delete a profile")
        print(colored("[3]","green") 
            + " view-Allows you to view a profile in a gui")
        print(colored("[4]","green") 
            + " edit-Allows you to edit a profile's attribute or add a new attribute!")
        print(colored("[5]","green") 
            + " entry-Allows you to make a information entry on a profile")
    #ENTRIES SECTION
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
    def delete_entry(self):
        first = input("First Name:")
        last =  input("Last Name:")
        label = input("Name Of Entry(the command to check all entry names is [view]):")
        entry_data={
            "type":"DELETE_ENTRY",
            "firstname":first,
            "lastname" :last,
            "label" : label
        }
        self.send_request(entry_data,"entry_deletion")

    #BREACH SECTION
    def breach_protocol(self):
        confirmation = input("Are you sure you would like to delete all data?[y/n]:")
        if confirmation == "y" or confirmation == "Y":
            confirmation2 = input("Are you very very sure? this process can not be reversed!![y/n]")
            if confirmation2 == "y" or confirmation2 == "Y":
                security_code = input("What is the security code??")
            else:
                print("Breach Aborted!!")
        else:
            print("Breach Aborted!!")
    def send_breach_request(self,code):
        breach_data = {
            "type": "BREACHED",
            "code": code
        }
        self.send_request(breach_data , "breached")
        



    #EMAIL SECTION
    def configure_email(self):
        email = input("Email Address:")
        password = input(f"Password for {email}:")
        email_data = {
            "type" : "EMAIL_CONFIG",
            "email" : email,
            "password" :password
        }
        self.send_request(email_data , "email_config")
    def add_email_recipient(self):
        new_email  = input("New Person Email:")
        email_nickname = input("New Person Nick Name:")
        email_data = {
            "type": "EMAIL_RECIPIENT_ADD",
            "email": new_email,
            "email_name" : email_nickname
        }
        self.send_request(email_data,"email_recipient_add")
    def remove_email_recipient(self):
        email_nickname = input("Nick Name you would like to remove:")
        remove_data = {
                "type":"REMOVE_EMAIL_RECIPIENT",
                "nickname": email_nickname
        }
        self.send_request(remove_data,"email_recipient_remove")

    def send_profiles(self):
        sender = input("what email would you like to send from?:")
        receiver = input("who would you like to receive this profile?:")
        email_data = {
                "type":"SEND_EMAIL",
                "sender":sender,
                "receiver":receiver
        }
        self.send_request(email_data,"send_email")

    #GENERAL PURPOSE SECTION
    def command_check(self,command):
        if  command == "create" or command == "1":
            self.create_profile()
        elif command == "view" or command == "3":
            self.view_profile()
        elif command == "edit" or command == "4":
            self.edit_profile()
        elif command == "delete" or command == "2":
            self.delete_profile()
        elif command == "entry" or command == "5":
            self.add_entry()
        elif command == "delete entry":
            self.delete_entry()
        elif command == "configure email":
            self.configure_email()
        elif command == "add recipient":
            self.add_email_recipient()
        elif command == "remove recipient":
            self.remove_email_recipient()
        elif command == "view profiles":
            self.gather_full_list()
        elif command == "send profiles":
            self.send_profiles()

        elif command == "--help" or command == "help":
            self.help()
        else:
            print("unknow command")

    def display_welcome_message(self):
            path = 'C:/Users/ronald/Git/Git Repos/POI/AsciiArt/Builder.txt'
            with open( path, "r") as file: #ascii art
                for i in file.readlines():
                    print(i)
            print(colored("#Welcome To Persons Of Interest!!" , "green"))
            print("-----------------------------------------------------")
            print(colored("#Build Profiles On Suspicious Characters!","red"))
            print(colored("--help for command listings" , "red"))

    def select_image(self):
        tkinter.Tk().withdraw()#avoid auto root level window
        profile_path = askopenfilename( initialdir= "/",title='Persons Image' , filetypes = [("PNG FILES" , "*.png")])
      
        if profile_path == "":
            return "NOT_PRESENT"
        else:
            with open(profile_path, "rb") as file:
                encoded_image = base64.b64encode(file.read()).decode("ascii")
            return encoded_image

    def Start(self):
        self.display_welcome_message()
        while self.running == True:
                print(" ")
                print(colored("#Persons Of Interest~","green") + "Version 1.0" )
                command = input(">")
                print(" ")
                self.command_check(command)


if __name__ == '__main__':
    client = Client()
    client.Start()
            
            


        

import base64
import socket
import json
import tkinter
import atexit
from tkinter import ttk
from termcolor import colored
from colorama import init
from tkinter.filedialog import askopenfilename
#classes:
import Help
import responsechecker
import commandchecker




init()#allow colored text to run on windows machines
        
"""
    Client Checks the commands by the user and maps
    to the correct function execution/sends requests 
    to the server on the user behalf!
"""
class Client:
    def __init__(self):
        self.running = True
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.help = Help.Help()
        self.command_checker = commandchecker.CommandChecker(self)
        self.response_checker = responsechecker.ResponseChecker()
        try:
            self.client.connect(('127.0.0.1',50222))
        except:
            self.running = False
            print(" ")
            print("Issue Connecting to Your Local Server!!")
            print("Could mean that the server isn't running!!")


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

    def send_request_size(self,request):
        formatted_request = json.dumps(request)
        data_size = len(formatted_request)
        #send size and then data
        self.client.send(str(data_size).encode("ascii"))
        self.client.send(formatted_request.encode("ascii"))

    def gather_full_list(self):
        self.send_request_size({"type" : "ALL"})
        #receive size and then data
        incoming_data_size = self.client.recv(60).decode("ascii")
        incoming_data = self.client.recv(int(incoming_data_size)).decode("ascii")
        if incoming_data == "issue":
            print("issue gathering list")
        elif incoming_data == "NONE":
            print("no profiles")
        else:
            self.display_all_profiles(incoming_data)

    def send_general_command(self , message,server_success_message,print_statement):
        self.send_request_size({"type": message})
        response = self.client.recv(70).decode("ascii")
        if response == server_success_message:
            print(print_statement)
        else:
            print("issue from server")

    def send_profiles_to_all(self):
        self.send_request_size({"type"})


    def send_request(self,data,message_type):
        self.send_request_size(data)
        response = self.client.recv(70).decode("ascii")
        print(response)
        self.response_checker.check_response(message_type,response, self.client)



    #EDIT SECTION
    def check_edit_response(self,response):
        if response == "SUCCESSFUL_EDIT":
            print("You Have Successfully Edited The Profile!")
        else:
            print("Issue Editing Profile!")

    
    def send_edit_request(self,edit_data):
        self.send_request_size(edit_data)
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
                self.send_breach_request("BREACHED","breached")
            else:
                print("Breach Aborted!!")
        else:
            print("Breach Aborted!!")
    def send_breach_request(self,type_message,request_type):
        code = input("what is your code?(security):")
        breach_data = {
            "type": type_message,
            "code": code
        }
        self.send_request(breach_data , request_type)

    def change_breach_code(self):
        original_code = input("what is your old code?:")
        new_code = input("what is your new code?:")
        breach_data = {
            "type": "BREACH_CHANGE",
            "code":original_code,
            "new_code" : new_code
        }
        self.send_request(breach_data,"breach_change")

        



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
    
   
           

    def display_welcome_message(self):
            path = 'C:/Users/ronald/Git/Git Repos/POI-LocalDesktop/AsciiArt/Builder.txt'
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
        if self.running == True:
            self.display_welcome_message()
        while self.running == True:
                print(" ")
                print(colored("#Persons Of Interest~","green") + "Version 1.0" )
                command = input(">")
                print(" ")
                self.command_checker.command_check(command)


if __name__ == '__main__':
    client = Client()
    client.Start()
            
            


        

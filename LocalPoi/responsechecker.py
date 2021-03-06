import json
import tkinter
import socket
import resultwindow
from termcolor import colored
from colorama import init
"""
ResponseChecker checks the response 
from client's request to server and
updates the user interface based on
the response

"""
class ResponseChecker:
    @staticmethod
    def display_profile(response):
        new_dict = json.loads(response)
        master = tkinter.Tk()
        result_window = resultwindow.ResultWindow(master,new_dict)
        master.mainloop()


    def check_profile_exist_reponse(self,response,client ):
        if response == "PROFILE_FOUND":
                data_size = int(str(client.recv(70).decode("ascii")))#size
                client.send("GOT".encode("ascii"))
                data = client.recv(data_size).decode("ascii")
                self.display_profile(data)
        else:
            print("Profile Does not exist!!")


    def check_status_response(self,response ,server_accept_message,success_message):
        if response == server_accept_message:
                print(success_message)
        else:
                print("Error From Server!")

    def check_response_tier_3(self,request,response):
        if request == "breach_change":
            pass

    def check_response_tier_2(self,request,response):
        if request == "email_recipient_add":
            self.check_status_response(response,"EMAIL_RECIPIENT_ADDED",
               colored("Recipient Added!" , "green")  )
        elif request ==  "email_recipient_remove":
            self.check_status_response(response,"EMAIL_RECIPIENT_REMOVED",
               colored("Recipient Removed!" , "green")  )
        elif request == "breached":
            print("You must configure breach before using (breached) with the command(config breach)")
            self.check_status_response(response,"BREACH_PROTOCOL_SUCCESSFUL",
               colored("Breach Protocol Complete!! Check the success with (VIEW ALL)" , "green")  )

        elif request == "send_email":
            print("Make sure you turn on to use this feature without errors : 'Less secure app access'")
            self.check_status_response(response,"EMAIL_SENT",
               colored("Email Successful Sent!!" , "green")  )
        elif request == "breach_config":
            self.check_status_response(response,"BREACH_CONFIGED",
               colored("Breach Protocol Setup!!" , "green")  )
        else:
            self.check_response_tier_3(request,response)



    def check_response(self,request,response,client):
        if request == "profile_creation" :
            self.check_status_response(response,"ACCEPTED_CREATION",
                "Profile Successfully Created!! ,View it with the command(view)")
        elif request == "profile_view":
            self.check_profile_exist_reponse(response,client)
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
        else:
            self.check_response_tier_2(request,response)
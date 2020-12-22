
import socket
import base64
import json
import tkinter
from termcolor import colored
from colorama import init
from tkinter import filedialog 





init()#allow colored text to run on windows machines

class ResultWindow:
	
	def __init__(self,master,first,last,location,reason,race,image):

		if image == "NOT_PRESENT":
			formatted_image = tkinter.PhotoImage(file = 'defaultimage.png') #anonymous photo

		else:
			formatted_image = tkinter.PhotoImage(data = image)

		formatted_first = "First Name: " + first
		formatted_last = "Last Name: " + last
		formatted_location = "Location: " + location
		formatted_reason = "Reason:" + reason
		formatted_race = "Race:" + race
		#widgets
		picture = tkinter.Label(master , image = formatted_image).pack()
		first_name = tkinter.Label(master,text = formatted_first).pack()
		last_name = tkinter.Label(master,text = formatted_first).pack()
		known_location = tkinter.Label(master, text = formatted_location).pack()
		reason_why = tkinter.Label(master,text= formatted_reason).pack()


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
	to the correct function execution!!
"""
class Client:
	def __init__(self):
		self.running = True
		self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.client.connect(('127.0.0.1',50222))
	def display_welcome_message():
			with open("Builder.txt" , "r") as file:
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
			race = input("Race/Skin Tone(ignore if you have picture):")
			profile_data = {"type" : "PROFILE_CREATION","firstname" : firstname,"lastname" : lastname,
    					 "location" : location,"reason" : reason,"race" : race
						}
			picture_prompt = input("would you like to include a picture?[y/n]:")
			if picture_prompt == "y" or  picture_prompt == "Y":
				self.profile_creation_with_image(profile_data)
			else:
				profile_data["image"] = "NOT_PRESENT"
				send_request(profile_data,"profile_creation")

	def display_profile(response):
		new_dict = json.loads(response)
		master = tkinter.Tk()
		result_window = ResultWindow(master,new_dict["firstname"],new_dict["lastname"],
									 new_dict["location"],new_dict["reason"],new_dict["race"],new_dict["image"])

	def check_response(request,response):
		if request == "profile_creation" :
			if response  == "ACCEPTED_CREATION":
				print("Profile Successfully Created!! ,View it with the command(view profile)")
			else:
				print("Error From Server!")
		elif request == "profile_view":
			if response == "PROFILE_FOUND":
				data_size = int(self.client.recv(70).decode("ascii"))#size
				data = self.client.recv(data_size).decode("ascii")
				self.display_profile(data)
			else:
				print("Profile Doesn't exist!")
				


	def send_request(self,data,message_type):
		message = json.dumps(data) #json string
    	message_size = len(message.encode("ascii")) # get the size for the first message
    	self.client.send(str(message_size)).encode("ascii") #sending size
    	self.client.send(message).encode("ascii")#sending real data
    	response = self.server_handler.client.recv(70).decode("ascii")
    	self.check_response(message_type,response)

	def profile_creation_with_image(self,user_data):
		profile_path = filedialog.askopenfilename( initialdir= "/",title='Persons Image')
		with open(profile_path, "rb") as file:
    		encoded_image = base64.b64encode(file.read())
    	user_data["image"] = encoded_image
    	self.send_request(user_data,"profile_creation")

    def view_profile(self):
    	first_name = input("First Name:")
    	last_name = input("Last Name:")
    	profile_data = {
    		"type" : "PROFILE_REQUEST",
    		"firstname":first_name,
    		"lastname" :lastname
    	}
    	send_request(profile_data,"profile_view")

    def check_edit_response(self,response):
    	if response == "SUCCESSFUL_EDIT":
    		pass
    	else:
    		pass
    def send_edit_request(self,edit_data):
    	data = json.dump(edit_data)
 		data_size = len(data.encode("ascii"))
 		self.client.send(data_size.encode("ascii"))
    	self.client.send(data.encode("ascii"))
    	incoming_size = int(self.client.recv(100).decode("ascii"))
    	if incoming_size == 0:
    		pass
    	else:
    		reponse = 	self.client.recv(incoming_size).decode("ascii")
    		self.check_edit_response(response)


 	def edit_profile(self):
 		first = input("First Name:")
 		last = input("Last Name:")
 		field = input("What Field Would you like to edit/update?:")
 		new_value = input(f"New Field Value for ${first + " " + last + "'s " field}: ")
 		edit_data = {
 			"type" : "PROFILE_EDIT",
 			"firstname" : first,
 			"lastname"  : last,
 			"field" : field,
 			"value":new_value
 		}
 		




	def command_check(self,command):
		if  command == "create profile":
			self.create_profile()
		elif command == "view profile":
			self.view_profile()
		elif command == "edit":




		
		
	def Start(self):
		self.display_welcome_message()
		while self.running == True:
				command = input(">")



        
        


        

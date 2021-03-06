from tkinter import ttk
import tkinter
import pymsgbox
import os
import base64
from functools import partial
"""

ResultWindow Displays a G.U.I for
the requested profile by the client
, and handles functionality for the
widgets.

"""

class ResultWindow:

    def image_check(self,data):
        if data["image"] == "NOT_PRESENT":
            self.formatted_image = tkinter.PhotoImage(file = 'defaultimage.png') 
            #only display race if there is no photo of subject
            race = tkinter.Label(self.master,text ="Race/Skin Color:"+ data["race"],
                 bg = "#222", fg = "#fff",font=("Courier", 20),relief = "ridge").pack()
        else:
            self.formatted_image = tkinter.PhotoImage(master = self.master,data = data["image"])

    def write_file_data(self,file,key):
      if key == "entries": 
            file.write("Entries:")
            file.write("\n")
            for entry in self.data["entries"]:
                value  = self.data["entries"][entry]
                file.write("  ")#making indentation for easy readying
                file.write(entry +":"+value) #writing the key value pair
                file.write("\n") # new line for next entry
      else:
            value = self.data[key]
            file.write(key + ":"+value)
            file.write("\n")
      pymsgbox.alert(
                text = "Finished!!",
                title = "success" ,
                button = "Ok")

    def create_files(self,dir_name):
        try:
            os.mkdir(dir_name)
            with open(dir_name+"/profilepic.png" , "wb") as file:
                file.write(base64.b64decode(self.data["image"]))
            with open(dir_name+"/profiledata.txt" , "w") as file:
                
                for key in self.data:#dict
                    #write all data that isn't the image
                    if key != "image":
                        self.write_file_data(file,key)


        except Exception as e :
            print(e)
            pymsgbox.alert(
                text = "directory already exist",
                title = "Issue.." ,
                button = "Ok")
            
        

    def download_profile(self):
        download_window = tkinter.Toplevel()
        heading = tkinter.Label(download_window, 
            text = "Name Of New Directory(for profile content) make sure the directory do not exist!").pack()
        data_input = ttk.Entry(download_window,heading)
        data_input.pack()
        download_button = tkinter.Button(download_window, text = "Download" ,
                 command = lambda: self.create_files(data_input.get())).pack()
        download_window.mainloop()



    
    def __init__(self,master,data):
        self.master = master
        self.image_check(data)
        self.data = data
        #widgets
        master.config(bg = "#222")
        picture = tkinter.Label(master , image = self.formatted_image ,bg = "#222" ).pack()
        download_button = tkinter.Button(master , text = "Download Picture" ,
            bg = "#666", fg = "#fff" ,borderwidth = 0.5 , command = lambda : self.download_profile()).pack()
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

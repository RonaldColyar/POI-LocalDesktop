
from termcolor import colored
from colorama import init
class Help:
    def help_tier_2(self):
        print(colored("[6]","green") 
            + " view profiles-prints a list of all profiles")
        print(colored("[7]","green") 
            + " config breach-Sets up a security protocol for you to remove all data")
        print(colored("[8]","green") 
            + " breached-Removes all data in seconds to avoid security breach!!")
        print(colored("[9]","green") 
            + " configure email-Creates a parent email that will be used to send profiles")
        print(colored("[11]","green") 
            + " send profiles-Sends all profile data to a chosen email")
        print(colored("[12]","green") 
            + " add recipient-adds an email to your contacts")
        print(colored("[13]","green") 
            + " send profiles to all-sends profiles to all emails in your contacts")
        
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
        self.help_tier_2()

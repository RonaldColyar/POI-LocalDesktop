class CommandChecker:
     def __init__(self, parent):
        self.parent = parent

     def third_tier_command_check(self,command):
            if command == "remove data":
                del_type = input("What data would you like to remove?(profile,email):")
                if del_type == "email":
                    self.parent.send_general_command("DEL_ALL_EMAILS", "DELETED_EVERYTHING","successfully deleted all!!")
                else:
                    self.parent.send_general_command("DEL_ALL_PROFILES","DELETED_EVERYTHING", "successfully deleted all!!")
            elif command == "config breach":
                self.parent.send_breach_request("BREACH_CONFIG","breach_config")
            elif command == "breached":
                self.parent.breach_protocol()
            elif command == "--help" or command == "help":
                self.parent.help.help()
            else:
                print("command unknown")


     def second_tier_command_check(self,command):
            if command == "delete entry":
                self.parent.delete_entry()
            elif command == "configure email":
                self.parent.configure_email()
            elif command == "add recipient":
                self.parent.add_email_recipient()
            elif command == "remove recipient":
                self.parent.remove_email_recipient()
            elif command == "view profiles":
                self.parent.gather_full_list()
            elif command == "send profiles":
                self.parent.send_profiles()
            elif command == "send profiles to all":
                self.parent.send_general_command("ALL_RECIPIENTS", "SENT_TO_ALL","Successfully Sent!!")
            else:
                self.third_tier_command_check(command)

        
     def command_check(self,command):
            if  command == "create" or command == "1":
                self.parent.create_profile()
            elif command == "view" or command == "3":
                self.parent.view_profile()
            elif command == "edit" or command == "4":
                self.parent.edit_profile()
            elif command == "delete" or command == "2":
                self.parent.delete_profile()
            elif command == "entry" or command == "5":
                self.parent.add_entry()

            else:
                self.second_tier_command_check(command)
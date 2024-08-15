# This Module will automate files transfer to Dolphin (by using a dedicated Riivolution Patch for separate Randomizer from nsmb file replacer)
import os
import shutil
from json import loads

config = {
    "enable_auto_copy":False,
    "riivolution_folder":""
}

class dolphinAutoTransfer:
    def __init__(self):
        pass

    def readAutoCopyConfig():
        global config
        rf = open("config_autoCopy.json")
        config = loads(rf.read())
        rf.close()
    
    def verify_autotransfer_status():
        if "enable_auto_copy" in config and (config["enable_auto_copy"]):
            return True
        else:
            return False
        
    def verify_transfer_settings():
        # Load Auto Copying Config File
            if "riivolution_folder" in config:
            # Verify if "riivolution_folder" is not empty and verify if custom path exist
                if config["riivolution_folder"] != "" and os.path.exists(config["riivolution_folder"]):
                    print("Auto Copying : A valid Riivolution folder has been provided on config_autoCopy.json")
                    return True    
                else:
                    print("Auto Copying : Dolphin Riivolution folder is not provided or incorrect, Trying to Locate Dolphin User Folder")
                    try:
                        if os.path.exists(os.path.join(os.environ['APPDATA'],"Dolphin Emulator","Load","Riivolution")):
                            print("Auto Copying : A Dolphin Riivolution folder has been located in your filesystem")
                            config["riivolution_folder"] = os.path.join(os.environ['APPDATA'],"Dolphin Emulator","Load","Riivolution")
                            return True
                        else:
                            print("Auto Copying : Cannot find a valid Dolphin Riivolution Folder")
                            return False
                    except KeyError:
                        print("Auto Copying : Cannot find a valid Dolphin Riivolution Folder")
                        return False
            else:
                print("The key 'riivolution_folder' is missing in the configuration file")
                return False
            
    def start_transfer(STG_NEW):
        # Load Auto Copying Config File
        print("Auto Copying : Starting File Transfer to Riivolution Folder...")
        # Verify if randomized files already exist
        if os.path.exists(config["riivolution_folder"] + "/nsmb_randomized"):
            # Remove old randomized files
            shutil.rmtree(config["riivolution_folder"] + "/nsmb_randomized")
        # Verify if riivolution subfolder exist (needed for auto find Riivolution XML files on Dolphin)
        if not os.path.exists(config["riivolution_folder"] + "/riivolution"):
            # Try to create riivolution subfolder
            print("Auto Copying : Cannot find riivolution subfolder, trying to create it")
            try:
                os.mkdir(config["riivolution_folder"] + "/riivolution")
            except:
                # if this directory didn't existe the script cannot continue, abort the transfer
                print("Auto Copying : Unable to create riivolution subfolder, cannot transfer")
                return False
        # Trying to transfer necessary files
        try:  
            shutil.copytree(STG_NEW, config["riivolution_folder"] + "/nsmb_randomized") #Copy Shuffled NSMB Files
            shutil.copyfile("nsmb_randomizer.xml", config["riivolution_folder"] + "/riivolution/nsmb_randomizer.xml") #Copy Riivolution XML
            return True
        except:
            return False
        

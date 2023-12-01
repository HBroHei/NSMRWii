# This Module will automate files transfer to Dolphin (by using a dedicated Riivolution Patch for separate Randomizer from nsmb file replacer)
import os
import shutil
from json import loads
rf = open("dolphinAutoTransfer_config.json")
config = loads(rf.read())
rf.close()
class dolphinAutoTransfer:
    def __init__(self):
        pass
    
    def verify_autotransfer_status():
        if "enable_transfer" in config and config["enable_transfer"] == True:
            return True
        else:
            return False
        
    def verify_transfer_settings():
        # Load Dolphin AutoTransfer Config File
            if "dolphin_riivolution_folder" in config:
            # Verify if "dolphin_riivolution_folder" is not empty and verify if custom path exist
                if config["dolphin_riivolution_folder"] != "" and os.path.exists(config["dolphin_riivolution_folder"]):
                    print("Dolphin AutoTransfer : A valid Dolphin Riivolution folder has been provided on dolphinAutoTransfer_config.json")
                    return True    
                else:
                    print("Dolphin AutoTransfer : Dolphin Riivolution folder is not provided or incorrect, Trying to Locate Dolphin User Folder")
                    if os.path.exists(os.path.join(os.environ['APPDATA'],"Dolphin Emulator","Load","Riivolution")):
                        print("Dolphin AutoTransfer : A Dolphin Riivolution folder has been located in your filesystem")
                        config["dolphin_riivolution_folder"] = os.path.join(os.environ['APPDATA'],"Dolphin Emulator","Load","Riivolution")
                        return True
                    else:
                        print("Dolphin AutoTransfer : Cannot find a valid Dolphin Riivolution Folder")
                        return False
            else:
                print("The key 'dolphin_riivolution_folder' is missing in the configuration file")
                return False
            
    def start_transfer(STG_NEW):
        # Load Dolphin AutoTransfer Config File
        print("Dolphin AutoTransfer : Starting File Transfer to Dolphin Riivolution Folder...")
        # Verify if randomized files already exist
        if os.path.exists(config["dolphin_riivolution_folder"] + "/nsmb_randomized"):
            # Remove old randomized files
            shutil.rmtree(config["dolphin_riivolution_folder"] + "/nsmb_randomized")
        # Verify if riivolution subfolder exist (needed for auto find Riivolution XML files on Dolphin)
        if not os.path.exists(config["dolphin_riivolution_folder"] + "/riivolution"):
            # Try to create riivolution subfolder
            print("Dolphin AutoTransfer : Cannot find riivolution subfolder, trying to create it")
            try:
                os.mkdir(config["dolphin_riivolution_folder"] + "/riivolution")
            except:
                # if this directory didn't existe the script cannot continue, abort the transfer
                print("Dolphin AutoTransfer : Unable to create riivolution subfolder, cannot transfer")
                return False
        # Trying to transfer necessary files
        try:  
            shutil.copytree(STG_NEW, config["dolphin_riivolution_folder"] + "/nsmb_randomized") #Copy Shuffled NSMB Files
            shutil.copyfile("nsmb_randomizer.xml", config["dolphin_riivolution_folder"] + "/riivolution/nsmb_randomizer.xml") #Copy Riivolution XML
            return True
        except:
            return False
        
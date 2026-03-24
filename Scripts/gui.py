import tkinter as tk
from tkinter import filedialog, ttk
from tkinter import messagebox as mb

from Util import convertToJson
import randomise_zones_main
import read_zones

import webbrowser
from json import load, dump
from os import listdir
from pathlib import Path
from threading import Thread
from traceback import format_exception

config_json = {}
stage_json = {}
stage_path = ""
rii_path = ""

root = tk.Tk()
root.title("NSMRW GUI")

# Override Exception handling
def show_exception(*args):
    mb.showerror("An error has occured!", "".join(format_exception(*args)))
    print("".join(format_exception(*args)))
root.report_callback_exception = show_exception

def check_enable_start():
    if config_json!={} and stage_json!={} and stage_path!="": btn_start["state"] = "normal"

# Left side texts and checkbox
lbl_generator = ttk.Label(root, text="1. Generate and download \"config.json\": ")
lbl_generator.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 0))
def btn_generator_onclick():
    webbrowser.open("https://hbrohei.github.io/NSMRWii/generator/")
btn_generator = ttk.Button(root, text="Go", command=btn_generator_onclick)
btn_generator.grid(row=0, column=1, sticky="e", padx=10, pady=(10, 0))

# Config.json related setting
tb_seed_sv = tk.StringVar()

lbl_config_sv = tk.StringVar()
lbl_config_sv.set("2. Load the downloaded config.json file here: ")
lbl_config = ttk.Label(root, textvariable=lbl_config_sv)
lbl_config.grid(row=1, column=0, sticky="w", padx=10)
def btn_config_onclick():
    global config_json
    f = filedialog.askopenfile()
    if f is None: return
    config_json = load(f)
    if "Skip But Randomise" not in config_json or "Group Tag" not in config_json:
        mb.showwarning("Missing parameters",'"Skip Bur Randomise" and / or "Group Tag" is missing from the config.json. ' \
        'Make sure you have enabled "Version 2" in the generator. Try re-generating config.json from the generator above.')
        config_json = {}
        return
    lbl_config_sv.set(f"2. Loaded {f.name} as config.json")
    tb_seed_sv.set(config_json["Seed"])
    f.close()
    check_enable_start()
    if config_json!={} and stage_path!="": btn_jsongen["state"] = "normal"
btn_config = ttk.Button(root, text="Load", command=btn_config_onclick)
btn_config.grid(row=1, column=1, sticky="e", padx=10)

# Seed textbox
vdigit = root.register(lambda P : str.isdigit(P) or P=="")
lbl_seed = ttk.Label(root, text="Seed: ")
lbl_seed.grid(row=2, column=0, sticky="w", padx=40)
tb_seed = ttk.Entry(root, width=30, textvariable=tb_seed_sv, validate="all", validatecommand=(vdigit, "%P"))
tb_seed.grid(row=2, column=1, sticky="e", padx=10, pady=5)

# Riivolution Path
cb_userii_sv = tk.StringVar()
cb_userii_sv.set("Automatically load to Riivolution")
check_var = tk.BooleanVar()
def cb_userii_onchange():
    btn_userii["state"] = "normal" if check_var.get() else "disabled"
cb_userii = ttk.Checkbutton(root, textvariable=cb_userii_sv, variable=check_var, onvalue=True, offvalue=False, command=cb_userii_onchange)
cb_userii.grid(row=4, column=0, sticky="w", padx=40)
def btn_userii_onclick():
    # Opens the directory for the Riivolution root path
    global rii_path
    rii_path = filedialog.askdirectory()
    if rii_path=="":
        return
    rii_paths = Path(rii_path)
    # Check if path is valid
    if rii_paths.parent.name=="Riivolution":
        mb.showinfo("Info","Path is selected to a Dolphin Riivolution path. Make sure to enable the patch to play the randomised stages!")
    elif "riivolution" not in listdir(rii_path) :
        mb.showwarning("Warning",'The selected folder does not have "riivolution" folder in it. Please select a folder with the "riivolution" folder in it.')
        rii_path = ""
        return
    cb_userii_sv.set(f"Riivolution path set to {rii_path}")
btn_userii = ttk.Button(root, text="Set Riivolution Path", state=tk.DISABLED, command=btn_userii_onclick)
btn_userii.grid(row=4, column=1, sticky="e", padx=10, pady=5)

frame_stage = tk.Frame(root)
frame_stage.grid(row=5, column=1, padx=10)

# Stage folder selection
lbl_stage_sv = tk.StringVar()
lbl_stage_sv.set("3. Select the \"Stage\" folder: ")
lbl_stage = ttk.Label(root, textvariable=lbl_stage_sv)
lbl_stage.grid(row=5, column=0, sticky="w", padx=10, pady=(10, 0))
def btn_stage_onclick():
    global stage_path
    # Select directory for the "Stage" folder
    stage_path = filedialog.askdirectory() + "/"
    if stage_path!="/":
        lbl_stage_sv.set(f"3. Stage folder set to {stage_path}")
        check_enable_start()
        if config_json!={} and stage_path!="": btn_jsongen["state"] = "normal"
btn_stage = ttk.Button(frame_stage, text="Select", command=btn_stage_onclick)
btn_stage.pack(side="right")
def btn_stagehelp_onclick():
    mb.showinfo("What's this?", "This is a required folder that contains all the stages files (that can be edited using level-editing softwares).\n\n" \
    "It can be obtained in various ways. As the process is the same as obtaining those files for level-editing in \"Reggie\" Level Editor," \
    "\"Stage\" folder obtained for Reggie Level Editing can be used directly here.\n\n" \
    "If the folder has not been obtained yet, follow the guide by clicking the \"Guide\"button. (No need to follow the next tutorial in that page.)")
btn_stagehelp = ttk.Button(frame_stage, text="What is this?", command=btn_stagehelp_onclick)
btn_stagehelp.pack(side="left")
def btn_stageguide_onclick():
    webbrowser.open("https://horizon.miraheze.org/wiki/Obtain_Original_Game_Files")
btn_stageguide = ttk.Button(frame_stage, text="Guide", command=btn_stageguide_onclick)
btn_stageguide.pack(side="left")

lbl_stageinfo = ttk.Label(root,text="4. Choose one of a or b:")
lbl_stageinfo.grid(row=6, columnspan=2, pady=(10,0))

def btn_json_help_onclick():
    mb.showinfo("What's this?", "This is a required file generated based on all the stages.\n\n" \
        "Do (a) if:\n  This is the first time randomising or the levels are modified since previous randomisation (such as importing custom levels) " \
        "such that a new stage.json will be generated for the main randomisation process.\n\n" \
        "Do (b) if:\n  \"stage.json\"has already been generated before and no new level modification has been made since.")
btn_json_help = ttk.Button(root, text="Which one should I choose?", command=btn_json_help_onclick)
btn_json_help.grid(row=7, columnspan=2, padx=10)

frame_stagegen = ttk.Frame(root)
frame_stagegen.grid(row=8, column=0, padx=10)

# Generate Stage.json
lbl_json_sv = tk.StringVar()
lbl_json_sv.set("a. Generate new stage.json: ")
lbl_json = ttk.Label(frame_stagegen, textvariable=lbl_json_sv)
lbl_json.grid(row=2, columnspan=2, padx=10, pady=(10,0))

def btn_jsongen_onclick():
    global config_json, stage_json
    # Generates the "stage.json" file
    stage_json = read_zones.process(config_json, stage_path)
    save_path = filedialog.asksaveasfilename(filetypes=[("JSON file", "*.json")], defaultextension=[("JSON file", "*.json")])
    if save_path:
        with open(save_path, 'w', encoding='utf-8') as f:
            dump(convertToJson(stage_json), f)
    lbl_json_sv.set(f"a. stage.json has been genereated")
    check_enable_start()
btn_jsongen = ttk.Button(frame_stagegen, text="Generate", command=btn_jsongen_onclick, state=tk.DISABLED)
btn_jsongen.grid(row=3, columnspan=2, padx=10, pady=(10,0))

frame_stageload = ttk.Frame(root)
frame_stageload.grid(row=8, column=1, padx=10)

# Load Stage.json
lbl_stageload_sv = tk.StringVar()
lbl_stageload_sv.set("b. Load existing stage.json: ")
lbl_stageload = ttk.Label(frame_stageload, textvariable=lbl_stageload_sv)
lbl_stageload.grid(row=0, columnspan=2, padx=10, pady=(10,0))
def btn_jsonload_onclick():
    global config_json, stage_json
    f = filedialog.askopenfile()
    stage_json = load(f)
    if f is None: return
    if stage_json:
        check_enable_start()
        lbl_stageload_sv.set(f"b. stage.json has been loaded")
    f.close()
btn_jsonload = ttk.Button(frame_stageload, text="Load", command=btn_jsonload_onclick)
btn_jsonload.grid(row=1, columnspan=2, padx=10, pady=(10,0))

no_exception = True

# When user choose to start randomisation
def btn_start_onclick():
    pbar_dialog = tk.Toplevel(root)
    pbar_dialog.title("Randomising...")
    pbar_dialog.resizable(False,False)
    lbl_loading = ttk.Label(pbar_dialog, text="Once the dialog is dismissed and no error occurs, your files will be ready.")
    lbl_loading.pack()
    pbar = ttk.Progressbar(pbar_dialog, mode="indeterminate", length=200)
    config_json["Seed"] = int(tb_seed_sv.get())

    # function to update the progress bar
    def update_pbar(randomise_thread):
        global no_exception
        if randomise_thread.is_alive():
            root.after(100,update_pbar, randomise_thread)
        else:
            pbar_dialog.destroy()
            # This is so jank but it will do for now
            if no_exception: mb.showinfo("Completed", f"Randomised stages has been saved to {rii_path if check_var.get() else "Stage_output"}")
            else: no_exception = True
    # Function to start randomising, ran on a thread.
    def start_randomise(stage_json, config_json, stage_path, autocopy_config):
        try:
            randomise_zones_main.main(stage_json, config_json, stage_path, autocopy_config)
        except Exception as e:
            # An exception has occured - show error message
            no_exception = False
            root.after(100, show_exception, e)
            
    pbar.start(10)
    pbar.pack()

    # Auto Copy dict config
    autocopy_config = {
        "enable_auto_copy":check_var.get(),
        "riivolution_folder":rii_path
    }
    randomise_thread = Thread(target=start_randomise, args=(stage_json, config_json, stage_path, autocopy_config))
    randomise_thread.start()
    
    update_pbar(randomise_thread)

btn_start = ttk.Button(root, text="Start Randomisation", command=btn_start_onclick, state=tk.DISABLED)
btn_start.grid(row=11, column=0, columnspan=2, sticky="ew", padx=10, pady=15)




# Make columns expand properly
root.grid_columnconfigure(0, weight=2)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)

root.mainloop()
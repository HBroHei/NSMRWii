from random import randint

final_lst = []

def func1():
    for i in range(0,3):
        for j in range(0,5):
            for k in range(0,16):
                for l in range(0,16):
                    final_str = ""

                    final_str += "00"
                    final_str += "00"
                    final_str += " "
                    final_str += "00"
                    final_str += "00"
                    final_str += " "
                    final_str += str(i) + f"{j:x}"
                    final_str += f"{k:x}{l:x}"

                    final_lst.append(final_str)

def func2():
    for i in range(0,4):
        for j in range(0,16):
            final_str = ""

            final_str += "xx"
            final_str += "xx"
            final_str += " "
            final_str += "xx"
            final_str += "xx"
            final_str += " "
            final_str += "xx"
            final_str += f"{i:x}{j:x}"

            final_lst.append(final_str)

def platform396():
    for length in range(1,16):
        for ret in range(0,2):
            for pnum in range(0,1):
                for dir in list(range(0,4))+["x"]:
                    for spd in range(1,16):
                        final_str = ""

                        final_str += "xx"
                        final_str += "xx"
                        final_str += " "
                        final_str += "xx"
                        final_str += str(dir)
                        final_str += f"{spd:x}"
                        final_str += " "
                        final_str += f"x{ret:x}"
                        final_str += f"{pnum:x}{length:x}"

                        final_lst.append(final_str)

# NOTE CHANGE HERE
platform396()

from tkinter import Tk
r = Tk()
r.clipboard_append(str(final_lst).replace("'","\""))
r.update() # now it stays on the clipboard after the window is closed
r.destroy()

# NOTE ALSO CHANGE HERE
with open("generator/variants/index_vars_396.js", "w") as f:
    f.write("const E_396_DATA = ")
    f.write(str(final_lst).replace("'","\""))
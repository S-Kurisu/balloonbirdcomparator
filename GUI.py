#https://www.geeksforgeeks.org/python/dropdown-menus-tkinter/
#https://www.geeksforgeeks.org/python/python-pack-method-in-tkinter/
import os
from tkinter import *
from PIL import Image, ImageTk
import Plot_Coord

script_dir = os.path.dirname(__file__)
maps_dir = os.path.join(script_dir, 'Maps/')

root = Tk()
root.title("Weather Balloon x Bird Geolocation Comparator")

listbox = Listbox(root)
listbox.pack(side=LEFT, expand=True, fill=BOTH)

canvas = Canvas(root, bg="white")
canvas.pack(side=LEFT, expand=True, fill=BOTH)

def on_click(event):
    selection = listbox.curselection()
    if not selection:
        return
    value = listbox.get(selection[0])
    img = Image.open(os.path.join(maps_dir, value))
    tk_img = ImageTk.PhotoImage(img)
    canvas.image = tk_img
    canvas.config(width=img.width, height=img.height)
    canvas.delete("all")
    canvas.create_image(0, 0, image=tk_img, anchor=NW)

listbox.bind("<<ListboxSelect>>", on_click)

#I initially thought about using a queue system to just pop the oldest map
#and push the most recent map, but because of the way that eBird API calls work
#I can't get 'only 1 hr' of data so this method wouldn't be significantly faster
#than the way i'm currently doing it
def update_maps():
    if os.path.isdir(maps_dir):
        for f in os.listdir(maps_dir):
            os.remove(os.path.join(maps_dir, f))

    Plot_Coord.plot_coord()

    listbox.delete(0, END)
    for f in os.listdir(maps_dir):
        listbox.insert(END, f)

def match_hour():
    current_time = datetime.datetime.now()
    if current_time.minute == 0 and current_time.second == 0:
        update_maps()

    root.after(1000, match_hour)

match_hour()
root.mainloop()

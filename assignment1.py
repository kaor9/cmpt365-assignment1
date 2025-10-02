# assignment1.py
# By James Cam, 301562474

import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

# get functions
def get_file_type(bmp_bytes):
  return int.from_bytes(bmp_bytes[0:2], 'little')

def get_file_size(bmp_bytes):
  return int.from_bytes(bmp_bytes[2:6], 'little')

def get_file_width(bmp_bytes):
  return int.from_bytes(bmp_bytes[18:22], 'little')

def get_file_height(bmp_bytes):
  return int.from_bytes(bmp_bytes[22:26], 'little')

def get_bits_per_pixel(bmp_bytes):
  return int.from_bytes(bmp_bytes[28:30], 'little')

# other functions
def browse_bmp_file():
  # we are only alowing the selections of .bmp files when pressing button. 
  filepath = filedialog.askopenfilename(title="Select a .bmp file", filetypes=[("BMP files", "*.bmp")])
  if filepath:
    file_path_entry.delete(0, tk.END)
    file_path_entry.insert(0, filepath)

def parse_bmp_file():
  # maybe also set a check to make sure its not empty or deal with empty
  # this also doesnt work for now
  if (file_path_entry.get() == ""):
    return # if no file is there currently, just dont do anything
  
  with open(f"{file_path_entry.get()}", "rb") as f:
    bmp_bytes = f.read()

  # if the first two bytes dont equal to 19778 (BM in little endian) let user know
  if get_file_type(bmp_bytes) != 19778:
    file_path_entry.delete(0, tk.END)
    file_path_entry.insert(0, "Invalid file, please insert a .bmp file.")
    file_size.config(text="")
    image_width.config(text="")
    image_height.config(text="")
    bits_per_pixel.config(text="")
    return # do some error handling later!
  
  file_size.config(text=f"{get_file_size(bmp_bytes)} bytes")
  image_width.config(text=f"{get_file_width(bmp_bytes)} px")
  image_height.config(text=f"{get_file_height(bmp_bytes)} px")
  bits_per_pixel.config(text=f"{get_bits_per_pixel(bmp_bytes)} bits per pixel")

def display_image():
  # https://stackoverflow.com/questions/65603857/how-to-display-an-image-in-tkinter-from-a-byte-array
  # https://stackoverflow.com/questions/10133856/how-to-add-an-image-in-tkinter
  # https://canvas.sfu.ca/courses/92560/discussion_topics/2014656 
  # https://pillow.readthedocs.io/en/stable/reference/Image.html check Image.frombytes or fromarray
  
  return

# Initialize window
root = tk.Tk()
root.title('Assignment 1')
root.geometry('900x700')

# Entry Section (Row 0)
tk.Label(root, text="File path:").grid(row=0, column=0, padx=10, pady=10)
file_path_entry = tk.Entry(root, width=80)
file_path_entry.grid(row=0, column=1, padx=10, pady=10) 
tk.Button(root, text="Browse", command=browse_bmp_file).grid(row=0, column=2, padx=10, pady=10)

# Parsing Button (Row 1)
tk.Button(root, text="Parse", command=parse_bmp_file).grid(row=1, column=1)

# Display Image (Row 2)
img = ImageTk.PhotoImage(Image.open("./PA1_Sample_Input/BIOS.bmp"))
tk.Label(root, image=img).grid(row=2, column=1, padx=10, pady=10)

# File size (Row 3)
tk.Label(root, text="File size:").grid(row=3, column=0, padx=10, pady=10)
file_size = tk.Label(root, text="")
file_size.grid(row=3, column=1, padx=10, pady=10)

# Image width (Row 4)
tk.Label(root, text="Image width:").grid(row=4, column=0, padx=10, pady=10)
image_width = tk.Label(root, text="")
image_width.grid(row=4, column=1, padx=10, pady=10)

# Image Height (Row 5)
tk.Label(root, text="Image height:").grid(row=5, column=0, padx=10, pady=10)
image_height = tk.Label(root, text="")
image_height.grid(row=5, column=1, padx=10, pady=10)

# Bits per pixel (Row 6)
tk.Label(root, text="Bits per pixel:").grid(row=6, column=0, padx=10, pady=10)
bits_per_pixel = tk.Label(root, text="")
bits_per_pixel.grid(row=6, column=1, padx=10, pady=10)


root.mainloop()
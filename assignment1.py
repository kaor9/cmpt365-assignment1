# assignment1.py
# By James Cam, 301562474

import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import numpy as np

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

def get_data_offset(bmp_bytes):
  return int.from_bytes(bmp_bytes[10:14], 'little')

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
  
  display_image(bmp_bytes)
  file_size.config(text=f"{get_file_size(bmp_bytes)} bytes")
  image_width.config(text=f"{get_file_width(bmp_bytes)} px")
  image_height.config(text=f"{get_file_height(bmp_bytes)} px")
  bits_per_pixel.config(text=f"{get_bits_per_pixel(bmp_bytes)} bits per pixel")

def display_image(bmp_bytes):
  # https://canvas.sfu.ca/courses/92560/discussion_topics/2014656 
  # https://pillow.readthedocs.io/en/stable/reference/Image.html check Image.frombytes or fromarray
  
  # this function will probably be ran in the parser too!
  # supposedly, the bits per field MUST mean something as we "must parse each byte differently" depending on the value (1,4,8,24)
  # 1 represents monochrome, while more bits means more color options
  # we must be careful for 1,4,8 bits per pixel as there is a color mapping!
  # also take notice of an offset for the "beginning of the bitmap data!"

  global img
  # img = ImageTk.PhotoImage(Image.open(file_path_entry.get()))
  # image.config(image=img)
  pixel_data = bmp_bytes[get_data_offset(bmp_bytes):] 
  bpp = get_bits_per_pixel(bmp_bytes)
  width = get_file_width(bmp_bytes)
  height = get_file_height(bmp_bytes)
  # (width + 7) // 8 gives the number of bytes width will use (without padding)
  # (((width + 7 // 8) + 3) // 4 ) * 4 gives the number of bytes for width (with padding)
  pixels = []
  if bpp == 1:
    # (width + 7 // 8) gives the number of bytes width will use (without padding)
    # (((width + 7 // 8) + 3) // 4 ) * 4 gives the number of bytes for width (with padding)
    # simplified: ((width + 31) // 32) * 4
    width_padded = ((width + 31) // 32) * 4
    for y in range(height):
      row_y = y * width_padded 
      for x in range(width):
        byte_i = row_y + x // 8
        bit_i = 7 - (x % 8)
        pixel_val = (pixel_data[byte_i] >> bit_i) & 1
        pixels.append(pixel_val * 255)
    
  pixel_array = np.array(pixels, dtype=np.uint8)
  pixel_array = pixel_array.reshape((height, width))
  pixel_array = np.flipud(pixel_array)

  img = ImageTk.PhotoImage(Image.fromarray(pixel_array, 'L'))
  image.config(image=img)



# Initialize window
root = tk.Tk()
root.title('Assignment 1')
root.geometry('1000x700')

# Entry Section (Row 0)
tk.Label(root, text="File path:").grid(row=0, column=0, padx=10, pady=10)
file_path_entry = tk.Entry(root, width=80)
file_path_entry.grid(row=0, column=1, padx=10, pady=10) 
tk.Button(root, text="Browse", command=browse_bmp_file).grid(row=0, column=2, padx=10, pady=10)

# Parsing Button (Row 1)
tk.Button(root, text="Parse", command=parse_bmp_file).grid(row=1, column=1)

# Display Image (Row 2)
image = tk.Label(root, image="")
image.grid(row=2, column=1, padx=10, pady=10)

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
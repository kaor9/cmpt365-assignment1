# assignment1.py
# By James Cam, 301562474

import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import numpy as np

# -- function definitions -- 

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

def get_color_table(bmp_bytes, bpp):
  # color table is 4 * numcolors
  # stored as B G R Reserved, and repeated for numcolor times
  if bpp == 1:
    num_colors = 2 # technically 1, but we want 0,1 later
  elif bpp == 4:
    num_colors = 16
  elif bpp == 8:
    num_colors = 256
  else:
    return None
  
  color_table = []
  for i in range(num_colors):
    offset = 54 + (i * 4)
    blue = bmp_bytes[offset]
    green = bmp_bytes[offset + 1]
    red = bmp_bytes[offset + 2]
    color_table.append((red, green, blue))
  
  return color_table


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
  global img # we will hold the 
  bpp = get_bits_per_pixel(bmp_bytes)
  width = get_file_width(bmp_bytes)
  height = get_file_height(bmp_bytes)
  pixel_data = bmp_bytes[get_data_offset(bmp_bytes):]
  color_table = get_color_table(bmp_bytes, bpp)
  pixels = [] # contains the pixels for numpy array to modify later

  # Note to self: probably try to shorten this function later, especially if were building on it for later assignments!
  if bpp == 1:
    # (width + 7) // 8 gives the number of bytes width will use (without padding)
    # (((width + 7) // 8 + 3) // 4 ) * 4 gives the number of bytes for width (with padding)
    # simplified: ((width + 31) // 32) * 4
    width_padded = ((width + 31) // 32) * 4
    for y in range(height):
      row_y_start = y * width_padded # gives us the byte index for the start of the yth row
      for x in range(width):
        byte_i = row_y_start + (x // 8)
        bit_i = 7 - (x % 8)
        pixel_val = (pixel_data[byte_i] >> bit_i) & 1 # either 0 or 1
        pixels.extend(color_table[pixel_val])
  elif bpp == 4:
    # (4w + 7) // 8 = bytes used (no padding)
    # (((4w + 7) // 8 + 3) // 4) * 4
    width_padded = (((4 * width + 7) // 8 + 3) // 4) * 4

    for y in range(height):
      row_y_start = y * width_padded
      for x in range(width):
        byte_i = row_y_start + (x // 2) # every pixel now occupies 4 bits vs 1 byte in 1ppx

        # traverse by 4 bits per byte now
        if x % 2 == 0:
          pixel_val = (pixel_data[byte_i] >> 4) & 0b1111
        else:
          # no need to shift for the last
          pixel_val = pixel_data[byte_i] & 0b1111
        
        pixels.extend(color_table[pixel_val])
  elif bpp == 8:
    # no need to account for bits when padding, only bytes itself.
    width_padded = (width + 3) // 4 * 4
    for y in range(height):
      row_y_start = y * width_padded
      for x in range(width):
        byte_i = row_y_start + x
        pixel_val = pixel_data[byte_i]
        pixels.extend(color_table[pixel_val])
  elif bpp == 24:
    # same formula like 8bpp, but each pixel (width) is 3 bytes!
    width_padded = ((3 * width) + 3) // 4 * 4
    for y in range(height):
      row_y_start = y * width_padded
      for x in range(width):
        byte_i = row_y_start + (3 * x) # 3 bytes per pixel, each byte stores color
        blue = pixel_data[byte_i]
        green = pixel_data[byte_i + 1]
        red = pixel_data[byte_i + 2]
        pixels.extend((red, green, blue))

  # modify array with numpy
  pixel_array = np.array(pixels, dtype=np.uint8) # match datatype to RGB (8 bits)
  pixel_array = pixel_array.reshape((height, width, 3))
  pixel_array = np.flipud(pixel_array)

  # For display purposes:
  array_img = Image.fromarray(pixel_array, 'RGB')
  img = ImageTk.PhotoImage(resize_for_display(array_img, width, height))
  image.config(image=img)

# function for resizing when displaying (seperate from resizing manually!)
def resize_for_display(img, width, height):
  if (width > 500 and height > 300) or width > 500:
    ratio = width/height
    return img.resize((500, int(round(500/ratio))))
  elif height > 300:
    ratio = height/width
    return img.resize((int(round(300/ratio), 300)))
    

# -- layout and main loop -- 


# Initialize window
root = tk.Tk()
root.title('Assignment 1')
root.geometry('1000x1000')

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

# Metadata sectioning (Row 3)
tk.Label(root, text="Metadata:").grid(row=3, column=1, padx=10, pady=10)

# File size (Row 4)
tk.Label(root, text="File size:").grid(row=4, column=0, padx=10, pady=10)
file_size = tk.Label(root, text="")
file_size.grid(row=4, column=1, padx=10, pady=10)

# Image width (Row 5)
tk.Label(root, text="Image width:").grid(row=5, column=0, padx=10, pady=10)
image_width = tk.Label(root, text="")
image_width.grid(row=5, column=1, padx=10, pady=10)

# Image Height (Row 6)
tk.Label(root, text="Image height:").grid(row=6, column=0, padx=10, pady=10)
image_height = tk.Label(root, text="")
image_height.grid(row=6, column=1, padx=10, pady=10)

# Bits per pixel (Row 7)
tk.Label(root, text="Bits per pixel:").grid(row=7, column=0, padx=10, pady=10)
bits_per_pixel = tk.Label(root, text="")
bits_per_pixel.grid(row=7, column=1, padx=10, pady=10)


root.mainloop()
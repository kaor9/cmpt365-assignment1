# assignment1.py
# By James Cam, 301562474

import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import numpy as np
import time

# -- Variables -- 

bmp_bytes_global = 0b0
start_time = 0
end_time = 0
total_time = 0
original_size = 0
compressed_size = 0

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
    # header and infoheader is 54 bytes
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
  if (file_path_entry.get() == ""):
    return # if no file is there currently, just dont do anything
  
  with open(f"{file_path_entry.get()}", "rb") as f:
    bmp_bytes = f.read()

  # if the first two bytes dont equal to 19778 (BM in little endian) let user know
  if get_file_type(bmp_bytes) != 19778:
    file_path_entry.delete(0, tk.END)
    file_path_entry.insert(0, "Invalid file, please insert a .bmp file.")
    image.delete("all")
    file_size.config(text="")
    image_width.config(text="")
    image_height.config(text="")
    bits_per_pixel.config(text="")
    return
  
  #track original file size for compression
  original_size = get_file_size(bmp_bytes)
  bmp_bytes_global = bmp_bytes

  display_image(bmp_bytes)
  file_size.config(text=f"{get_file_size(bmp_bytes)} bytes")
  image_width.config(text=f"{get_file_width(bmp_bytes)} px")
  image_height.config(text=f"{get_file_height(bmp_bytes)} px")
  bits_per_pixel.config(text=f"{get_bits_per_pixel(bmp_bytes)} bits per pixel")

def display_image(bmp_bytes):
  # This function will for sure be redone in future iterations in the case that we are extending
  # the current functionality of the current program. This is nightmare code written at 12am..

  global img # without it being global, image will not show
  bpp = get_bits_per_pixel(bmp_bytes)
  width = get_file_width(bmp_bytes)
  height = get_file_height(bmp_bytes)
  pixel_data = bmp_bytes[get_data_offset(bmp_bytes):]
  color_table = get_color_table(bmp_bytes, bpp)
  pixels = [] # contains the pixels for numpy array to modify later

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
        pixels.extend([red, green, blue])
  else:
    file_path_entry.delete(0, tk.END)
    file_path_entry.insert(0, "This program only accepts files of 1, 4, 8, and 24 bits per pixel!")
    image.config(image="")
    return


  # change size based on slider:
  scale = scale_slider.get()/100
  if scale < 1.0:
    new_pixels = []
    new_width = int(width * scale)
    new_height = int(height * scale)

    if new_height == 0 or new_width == 0:
      image.delete("all")
      return

    # calculate how many pixels to skip in the original
    x_skip = width / new_width
    y_skip = height / new_height

    for y in range(new_height):
      for x in range(new_width):
        orig_x = int(x * x_skip)
        orig_y = int(y * y_skip)
        pixel_i = (orig_y * width + orig_x) * 3
        new_pixels.extend([pixels[pixel_i], pixels[pixel_i+1], pixels[pixel_i+2]])
    pixels = new_pixels
    width = new_width
    height = new_height

  # change brightness here based on slider:
  brightness = brightness_slider.get()/100
  if brightness != 1.0:
    for i in range(0, len(pixels), 3):
      pixels[i] = max(0, min(255, int(pixels[i] * brightness)))
      pixels[i+1] = max(0, min(255, int(pixels[i+1] * brightness)))
      pixels[i+2] = max(0, min(255, int(pixels[i+2] * brightness)))

  # enable/disable RGB
  show_red, show_green, show_blue = red_channel.get(), green_channel.get(), blue_channel.get()
  if not show_red or not show_green or not show_blue:
    for i in range(0,len(pixels), 3):
      if not show_red:
        pixels[i] = 0
      if not show_green:
        pixels[i+1] = 0
      if not show_blue:
        pixels[i+2] = 0

  # shape and flip array
  pixel_array = np.array(pixels, dtype=np.uint8) # match datatype to RGB (8 bits)
  pixel_array = pixel_array.reshape((height, width, 3)) 
  pixel_array = np.flipud(pixel_array)

  # Displaying the image using canvas
  array_img = Image.fromarray(pixel_array, 'RGB')
  img = ImageTk.PhotoImage(array_img)
  image.delete("all")
  c_width = image.winfo_width()
  c_height = image.winfo_height()
  x = (c_width - width) // 2
  y = (c_height - height) // 2
  image.create_image(x, y, anchor=tk.NW, image=img)
    
def compress(bmp_bytes):
  start_time = time.perf_counter()

  # create header

  end_time = time.perf_counter()
  total_time = start_time - end_time
  return

# -- layout and main loop -- 


# Initialize window
root = tk.Tk()
root.title('Assignment 1')
root.geometry('1000x850')

# Entry Section (Row 0)
tk.Label(root, text="File path:").grid(row=0, column=0, padx=10, pady=10)
file_path_entry = tk.Entry(root, width=80)
file_path_entry.grid(row=0, column=1, padx=10, pady=10) 
tk.Button(root, text="Browse", command=browse_bmp_file).grid(row=0, column=2, padx=10, pady=10)

# Parsing Button (Row 1)
tk.Button(root, text="Parse", command=parse_bmp_file).grid(row=1, column=1)

# Sliders (Row 2)
# for brightness
brightness_slider = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL, label="Brightness %", 
                             command=lambda x: parse_bmp_file()) # lazy move on me i know
brightness_slider.grid(row=2, column=0, padx=10, pady=10)
brightness_slider.set(100)

# for scale
scale_slider = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL, label="Scale",
                        command=lambda x: parse_bmp_file()) # again very lazy
scale_slider.grid(row=2, column=2, padx=10, pady=10)
scale_slider.set(100)

# Display Image (Row 3)
image = tk.Canvas(root, width=600, height=450, bg="white")
image.grid(row=3, column=1, padx=10, pady=10)


# RGB Buttons (Row 4)
red_channel = tk.BooleanVar(value=True)
green_channel = tk.BooleanVar(value=True)
blue_channel = tk.BooleanVar(value=True)
red_button = tk.Checkbutton(root, text="Red", variable=red_channel)
red_button.grid(row=4, column=0, padx=10, pady=10)
green_button = tk.Checkbutton(root, text="Green", variable=green_channel)
green_button.grid(row=4, column=1, padx=10, pady=10)
blue_button = tk.Checkbutton(root, text="Blue", variable=blue_channel)
blue_button.grid(row=4, column=2, padx=10, pady=10)

# File size (Row 5)
tk.Label(root, text="File size:").grid(row=5, column=0, padx=10, pady=10)
file_size = tk.Label(root, text="")
file_size.grid(row=5, column=1, padx=10, pady=10)

# Image width (Row 6)
tk.Label(root, text="Image width:").grid(row=6, column=0, padx=10, pady=10)
image_width = tk.Label(root, text="")
image_width.grid(row=6, column=1, padx=10, pady=10)

# Image Height (Row 7)
tk.Label(root, text="Image height:").grid(row=7, column=0, padx=10, pady=10)
image_height = tk.Label(root, text="")
image_height.grid(row=7, column=1, padx=10, pady=10)

# Bits per pixel (Row 8)
tk.Label(root, text="Bits per pixel:").grid(row=8, column=0, padx=10, pady=10)
bits_per_pixel = tk.Label(root, text="")
bits_per_pixel.grid(row=8, column=1, padx=10, pady=10)

# Compression button (Row 9)
tk.Button(root, text="Compress", command="").grid(row=9, column=1, padx=10, pady=10)



root.mainloop()
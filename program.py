import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import numpy as np
import time
from collections import Counter
import os

# -- Classes --
class Node:
  def __init__(self, symbol, weight, left=None, right=None):
    self.symbol = symbol
    self.weight = weight
    self.left = left
    self.right = right

# -- Global Variables -- 

bmp_bytes_global = 0
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

def browse_file():
  # we are only alowing the selections of .bmp files when pressing button. 
  filepath = filedialog.askopenfilename(title="Select a .bmp file", filetypes=[("All files", "*.*"), ("BMP files", "*.bmp"), ("cmpt365 files", "*.cmpt365")])
  if filepath:
    file_path_entry.delete(0, tk.END)
    file_path_entry.insert(0, filepath)

def open_file():
  global bmp_bytes_global
  # checks the header of a .bmp and .cmpt365 file to choose how to handle it
  if (file_path_entry.get() == ""):
    return # if no file is there currently, just dont do anything
  
  with open(f"{file_path_entry.get()}", "rb") as f:
    bytes = f.read()

  file_type = get_file_type(bytes)
  if file_type == 19778: # for BM in hex (little endian)
    bmp_bytes_global = bytes
    parse_bmp_file(bytes)
  elif file_type == 19784: # for HM in hex
    decompress(bytes)
  else:
    bmp_bytes_global = 0
    file_path_entry.delete(0, tk.END)
    file_path_entry.insert(0, "Invalid file, please insert a .bmp or .cmpt365 file.")
    image.delete("all")
    file_size.config(text="")
    image_width.config(text="")
    image_height.config(text="")
    bits_per_pixel.config(text="")
    return

def parse_bmp_file(bmp_bytes):
  global original_size
  global bmp_bytes_global
  #track original file size for compression
  original_size = get_file_size(bmp_bytes)
  bmp_bytes_global = bmp_bytes

  display_image(bmp_bytes)
  file_size.config(text=f"{get_file_size(bmp_bytes)} bytes")
  image_width.config(text=f"{get_file_width(bmp_bytes)} px")
  image_height.config(text=f"{get_file_height(bmp_bytes)} px")
  bits_per_pixel.config(text=f"{get_bits_per_pixel(bmp_bytes)} bits per pixel")

def display_image(bmp_bytes):
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
    
def compress(output_name):
  global original_size
  global bmp_bytes_global
  global end_time
  global total_time
  global compressed_size
  global start_time
  # alg:
  # init: put symbols in a sorted list according to their frequency count
  # repeat:
  # pick two symbols with lowest frequency counts and form a subtree with both symbols as children.
  # the parent node should be assigned to the sum of the two symbols, and place the parent back into the list
  # delete the two children that were used for the list

  # 0 is nothing, if 0 do not compress the image
  if bmp_bytes_global == 0:
    file_path_entry.insert(0, "Please input a .bmp file to compress, to compress you must display the image first.")
    return 

  # grab pixels and header
  data_offset = get_data_offset(bmp_bytes_global)
  header = bmp_bytes_global[:data_offset]
  pixels = bmp_bytes_global[data_offset:]
  
  # count frequency
  frequency = Counter(pixels)
  nodes = []
  for s, c in frequency.items():
    nodes.append((Node(s, c), c))
  nodes.sort(key=lambda x: x[1])

  # take smallest two nodes, place into parent and back to list
  # should follow example like in class since the second pop will go on the right where its always the biggest
  while len(nodes) > 1:
    (n1, c1) = nodes.pop(0)
    (n2, c2) = nodes.pop(0)
    p = Node(None, c1+c2, n1, n2)
    nodes.append((p, p.weight))
    nodes.sort(key=lambda x: x[1])
  
  root = nodes[0][0]

  # map symbols to code
  codes = {}
  codes_len = {}

  def assign(node, bitstr):
    print(bitstr)
    if node.symbol is not None:
      codes[node.symbol] = bitstr
      codes_len[node.symbol] = len(bitstr)
      return
    assign(node.left, bitstr + "0")
    assign(node.right, bitstr + "1")

  assign(root, "")

  # get max code length
  l_max = max(codes_len.values())

  # create one big string for the pixels
  bitstring = "".join(codes[b] for b in pixels)
  padding = (8 - (len(bitstring) % 8)) % 8
  bitstring += "0" * padding

  compressed_pixels = bytearray(int(bitstring[i:i+8], 2) for i in range(0, len(bitstring), 8))

  # create the new file with the .cmpt365 extension
  with open(output_name + ".cmpt365", "wb") as f:
    f.write(b"HM")                                            # HM in hex
    f.write(len(bmp_bytes_global).to_bytes(4, 'little'))      # original size of bmp
    f.write(len(header).to_bytes(4, 'little'))                # original header len
    f.write(header)                                           # original header
    f.write(l_max.to_bytes(1, 'little'))                      # max bits length
    f.write(len(codes).to_bytes(2, 'little'))                 # number of symbols/codes

    # each symbol + code length + the bits
    for s, c in codes.items():                       
      f.write(s.to_bytes(1, 'little'))                                # symbol
      f.write(codes_len[s].to_bytes(1, 'little'))                     # code length
      f.write(int(c, 2).to_bytes((codes_len[s] + 7) // 8, 'big'))     # bits

    # padding bytes
    f.write(padding.to_bytes(1, 'little'))
    f.write(compressed_pixels)

  end_time = time.time() * 1000
  total_time = end_time - start_time

  compressed_size = os.path.getsize(output_name + ".cmpt365")

  orig_size.config(text=f"{original_size} bytes")
  comp_size.config(text=f"{compressed_size} bytes")
  comp_ratio.config(text=f"{original_size/compressed_size}")
  comp_time.config(text=f"{total_time} ms")


def run_compression():
  global start_time
  start_time = time.time() * 1000
  file_name = os.path.basename((file_path_entry.get().split(".", 1))[0]) # grab file name without extension
  compress(file_name)

def decompress(cmpt365_bytes):
  global bmp_bytes_global

  ind = 2 # since 0-1 are for HM which was checked before calling

  # original size
  orig_size = int.from_bytes(cmpt365_bytes[ind:ind+4], "little")
  ind += 4

  # original header length
  header_len = int.from_bytes(cmpt365_bytes[ind:ind+4], "little")
  ind += 4

  # original header when reconstructing
  header = cmpt365_bytes[ind:ind+header_len]
  ind += header_len

  # calculate table size
  l_max = cmpt365_bytes[ind]
  ind += 1
  table_size = 1 << l_max # calculate the max size of the table based on length

  num_symbols = int.from_bytes(cmpt365_bytes[ind:ind+2], "little")
  ind += 2

  codes = {}

  for _ in range(num_symbols):
    s = cmpt365_bytes[ind]
    ind += 1
    l = cmpt365_bytes[ind]
    ind += 1
    num_bytes = (l + 7)//8
    code_bits = cmpt365_bytes[ind:ind+num_bytes]
    ind += num_bytes
    code_int = int.from_bytes(code_bits, 'big')
    code_str = bin(code_int)[2:].zfill(num_bytes*8)[-l:]
    codes[code_str] = s

  # pad
  padding = cmpt365_bytes[ind]
  ind += 1

  payload = cmpt365_bytes[ind:]
  bitstring = "".join(bin(b)[2:].zfill(8) for b in payload)
  if padding:
    bitstring = bitstring[:-padding]

  # Huff decoder
  huff_dec = [None] * table_size

  for code_str, s in codes.items():
    l = len(code_str)
    code_int = int(code_str, 2) if l > 0 else 0
    start = code_int << (l_max - l)
    stop = (code_int + 1) << (l_max - l)
    for i in range(start, stop):
      huff_dec[i] = (s, l)
  
  # decode huffman
  ind = int(bitstring[:l_max], 2)
  pos = l_max
  decoded = bytearray()
  mask = (1 << l_max) - 1

  while pos <= len(bitstring):
    s, l = huff_dec[ind]
    if l == 0:
      break
    decoded.append(s)

    if pos + l > len(bitstring): 
      break
    
    next_bits = int(bitstring[pos:pos+l], 2)
    pos += l

    ind = ((ind << l) | next_bits) & mask

  reconstructed = header + decoded
  bmp_bytes_global = reconstructed

  display_image(reconstructed)



# -- Tkinter layout + main loop -- 


# Initialize root
root = tk.Tk()
root.title('Assignment 1')
root.geometry('1000x850')

# Create scrollable frame, (works only by clicking or hovering it then using scrollwheel)
# https://www.youtube.com/watch?v=0WafQCaok6g for scrollable
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=1)
my_canvas = tk.Canvas(main_frame)
my_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
my_scroll = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=my_canvas.yview)
my_scroll.pack(side=tk.RIGHT, fill=tk.Y)
my_canvas.configure(yscrollcommand=my_scroll.set)
my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion = my_canvas.bbox("all")))
second_frame = tk.Frame(my_canvas)
my_canvas.create_window((0,0), window=second_frame, anchor="nw")


# Entry Section (Row 0)
tk.Label(second_frame, text="File path:").grid(row=0, column=0, padx=10, pady=10)
file_path_entry = tk.Entry(second_frame, width=80)
file_path_entry.grid(row=0, column=1, padx=10, pady=10) 
tk.Button(second_frame, text="Browse", command=browse_file).grid(row=0, column=2, padx=10, pady=10)

# Parsing Button (Row 1)
tk.Button(second_frame, text="Display", command=open_file).grid(row=1, column=1)

# Sliders (Row 2)
# for brightness
brightness_slider = tk.Scale(second_frame, from_=0, to=100, orient=tk.HORIZONTAL, label="Brightness %", 
                             command=lambda x: open_file()) # lazy move on me i know
brightness_slider.grid(row=2, column=0, padx=10, pady=10)
brightness_slider.set(100)

# for scale
scale_slider = tk.Scale(second_frame, from_=0, to=100, orient=tk.HORIZONTAL, label="Scale",
                        command=lambda x: open_file()) # again very lazy
scale_slider.grid(row=2, column=2, padx=10, pady=10)
scale_slider.set(100)

# Display Image (Row 3)
image = tk.Canvas(second_frame, width=600, height=450, bg="white")
image.grid(row=3, column=1, padx=10, pady=10)

# RGB Buttons (Row 4)
red_channel = tk.BooleanVar(value=True)
green_channel = tk.BooleanVar(value=True)
blue_channel = tk.BooleanVar(value=True)
red_button = tk.Checkbutton(second_frame, text="Red", variable=red_channel)
red_button.grid(row=4, column=0, padx=10, pady=10)
green_button = tk.Checkbutton(second_frame, text="Green", variable=green_channel)
green_button.grid(row=4, column=1, padx=10, pady=10)
blue_button = tk.Checkbutton(second_frame, text="Blue", variable=blue_channel)
blue_button.grid(row=4, column=2, padx=10, pady=10)

# Original File Metadata
# File size (Row 5)
tk.Label(second_frame, text="File size:").grid(row=5, column=0, padx=10, pady=10)
file_size = tk.Label(second_frame, text="")
file_size.grid(row=5, column=1, padx=10, pady=10)
# Image width (Row 6)
tk.Label(second_frame, text="Image width:").grid(row=6, column=0, padx=10, pady=10)
image_width = tk.Label(second_frame, text="")
image_width.grid(row=6, column=1, padx=10, pady=10)
# Image Height (Row 7)
tk.Label(second_frame, text="Image height:").grid(row=7, column=0, padx=10, pady=10)
image_height = tk.Label(second_frame, text="")
image_height.grid(row=7, column=1, padx=10, pady=10)
# Bits per pixel (Row 8)
tk.Label(second_frame, text="Bits per pixel:").grid(row=8, column=0, padx=10, pady=10)
bits_per_pixel = tk.Label(second_frame, text="")
bits_per_pixel.grid(row=8, column=1, padx=10, pady=10)

# Compression Data Comparison
# Compression button (Row 9)
tk.Button(second_frame, text="Compress", command=run_compression).grid(row=9, column=1, padx=10, pady=10)
# Original BMP file size (Row 10)
tk.Label(second_frame,text="Original file size:").grid(row=10, column=0, padx=10, pady=10)
orig_size = tk.Label(second_frame, text="")
orig_size.grid(row=10, column=1, padx=10, pady=10)
# Comperssed file size (Row 11)
tk.Label(second_frame,text="Compressed file size:").grid(row=11, column=0, padx=10, pady=10)
comp_size = tk.Label(second_frame, text="")
comp_size.grid(row=11, column=1, padx=10, pady=10)
# Compression ratio (Row 12)
tk.Label(second_frame,text="Compression ratio:").grid(row=12, column=0, padx=10, pady=10)
comp_ratio = tk.Label(second_frame, text="")
comp_ratio.grid(row=12, column=1, padx=10, pady=10)
# Compression time in ms (Row 13)
tk.Label(second_frame,text="Compression time").grid(row=13, column=0, padx=10, pady=10)
comp_time = tk.Label(second_frame, text="")
comp_time.grid(row=13, column=1, padx=10, pady=10)


root.mainloop()
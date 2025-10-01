# assignment1.py
# By James Cam, 301562474

import tkinter as tk
from tkinter import filedialog

def browse_bmp_file():
  # might need to check whether file type is valid beyond checking extension name!
  # likely we can also check this thorugh the bits in the header! (0002h, look for 42 and 4D for BM)
  # when returning bytes [0:1], 19778 represents 4D42 (little endian)
  filepath = filedialog.askopenfilename(title="Select a .bmp file", filetypes=[("BMP files", "*.bmp")])
  if filepath:
    file_path_entry.delete(0, tk.END)
    file_path_entry.insert(0, filepath)

def parse_bmp_file():
  # maybe also set a check to make sure its not empty or deal with empty
  # this also doesnt work for now
  with open(f"{file_path_entry.get()}", "rb") as f:
    bmp_bytes = f.read()
    print(int.from_bytes(bmp_bytes[0:2], 'little'))

def get_file_type(self, bmp_bytes):
  return int.from_bytes(bmp_bytes[0:2], 'little')

def get_file_size(self, bmp_bytes):
  return int.from_bytes(bmp_bytes[14:18], 'little')

def get_file_width(self, bmp_bytes):
  return int.from_bytes(bmp_bytes[18:22], 'little')

def get_file_height(self, bmp_bytes):
  return int.from_bytes(bmp_bytes[22:26], 'little')

def get_bits_per_pixel(self, bmp_bytes):
  return int.from_bytes(bmp_bytes[28:30], 'little')

#init window
root = tk.Tk()
root.title('Assignment 1')
root.geometry('800x600')

# Entry Section (Row 0)
tk.Label(root, text="File path:").grid(row=0, column=0, padx=10, pady=10)
file_path_entry = tk.Entry(root, width=80)
file_path_entry.grid(row=0, column=1, padx=10, pady=10) 
tk.Button(root, text="Browse", command=browse_bmp_file).grid(row=0, column=2, padx=10, pady=10)

# Parsing (Row 1)
tk.Button(root, text="Parse", command=parse_bmp_file).grid(row=1, column=1)


# Display Image (Row 2)



# File size (Row 3)
tk.Label(root, text="File size:").grid(row=3, column=0, padx=10, pady=10)

# Image width (Row 4)
tk.Label(root, text="Image width:").grid(row=4, column=0, padx=10, pady=10)

# Image Height (Row 5)
tk.Label(root, text="Image height:").grid(row=5, column=0, padx=10, pady=10)

# Bits per pixel (Row 6)
tk.Label(root, text="Bits per pixel:").grid(row=6, column=0, padx=10, pady=10)




root.mainloop()
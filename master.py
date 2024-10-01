

import sys
import subprocess
import pandas as pd
import numpy as np
import re
import tifffile as tf
import os
from contextlib import contextmanager
import tkinter as tk
import cv2
from tkinter import filedialog, Listbox
from PIL import Image, ImageTk
import math
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

# Run install_dependency.py before importing any modules
subprocess.run([sys.executable, 'install_dependency.py'])


os.environ['PATH'] = "/usr/bin:" + os.environ['PATH']

# Function to check if a dependency is installed
def check_dependency(dependency_name, install_command):
    try:
        __import__(dependency_name)
    except ImportError:
        return False
    return True
    
# Function to check and install OpenCV
def check_and_install_opencv():
    try:
        import cv2
    except ImportError:
        print("Error: OpenCV is not installed.")
        choice = input("Do you want to install OpenCV? (y/n): ").lower()
        if choice == 'y':
            subprocess.run(['pip3', 'install', 'opencv-python'])
        else:
            print("Skipping OpenCV installation.")
            sys.exit(1)

# Check if tkinter is available
if not check_dependency('tkinter', 'sudo apt-get install python3-tk'):
    print("Error: tkinter is not installed.")
    choice = input("Do you want to install tkinter? (y/n): ").lower()
    if choice == 'y':
        subprocess.run(['sudo', 'apt-get', 'install', 'python3-tk'])
        # Import tkinter again to avoid NameError
        import tkinter as tk
    else:
        print("Skipping tkinter installation.")
        sys.exit(1)

# Check if exiftool is available in the system's PATH
def is_exiftool_installed():
    try:
        subprocess.run(['exiftool', '-ver'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        return False

if not is_exiftool_installed():
    print("Error: exiftool is not installed.")
    choice = input("Do you want to install exiftool? (y/n): ").lower()
    if choice == 'y':
        subprocess.run(['sudo', 'apt-get', 'install', 'libimage-exiftool-perl'])
    else:
        print("Skipping exiftool installation.")
        sys.exit(1)



def get_band_for_filename(filename, bands_df):
    row = bands_df[bands_df['filename'] == filename]
    if not row.empty:
        return row['band'].iloc[0]
    else:
        return "Filename not found in the dataframe"

def get_freq_for_filename(filename, bands_df):
    row = bands_df[bands_df['filename'] == filename]
    if not row.empty:
        return row['CentralWavelength'].iloc[0]
    else:
        return "CentralWavelength not found in the dataframe"


def parse_exif_files(exif_files):
    bands = pd.DataFrame(columns=['filename', 'band', 'frequency', 'CentralWavelength' ])
    for exif_file in exif_files:
        print("Get bandName from:", exif_file)

        exif_file = os.path.join(exif_file)
        if not os.path.exists(exif_file):
            print(f"Warning: EXIF file not found for {exif_file}. Expected path: {exif_file}. Skipping...")
            continue
        
        filename = os.path.basename(exif_file).split('.')[0]
        with open(exif_file, 'r') as file:
            bandName = ''
            bandFreq = ''
            centralWavelength = ''
            for line in file:
                if "BandName" in line:
                    bandName = line.split(":")[1].strip()
                if "BandFreq" in line:
                    bandFreq = line.split(":")[1].strip()
                if "CentralWavelength" in line:
                    centralWavelength = line.split(":")[1].strip()        
          
     
            bands.loc[len(bands.index)] = [filename, bandName, bandFreq, centralWavelength] 

    return bands


def parse_tif_files(tif_files, bands):
    dfs = []
    rows = 0
    cols = 0
    kernel = np.ones((3, 3)) / 9  
    for tif_file in tif_files:
        filename = os.path.basename(tif_file)
        pattern = r"^(.*?)_step\d+\.\d+\.TIF$"
        match = re.match(pattern, filename)
        if match:
            common_part = match.group(1)
            print("matched filename:", common_part)
        raster_data = tf.imread(tif_file)
        raster_data = raster_data / 65535.0 #Transform to reflectance

        height, width = raster_data.shape[:2]

        # Define the coordinates for the middle region
        top = (height - 250) // 2
        bottom = top + 250
        left = (width - 250) // 2
        right = left + 250

        # Slice the image data to select the middle region
        middle_region = raster_data[top:bottom, left:right]

        # Apply filter to the raster data
        filtered_raster_data = cv2.filter2D(middle_region, -1, kernel)
        rows, cols = filtered_raster_data.shape
        reshaped_data = filtered_raster_data.reshape((rows * cols, 1))
        
        df = pd.DataFrame(reshaped_data, columns=[get_freq_for_filename(common_part, bands)])
        dfs.append(df)
    
    merged_df = pd.concat(dfs, axis=1)
    sort_df = merged_df.sort_index(axis = 1)
    return sort_df, rows, cols

def populate_result(result_image_label, result_label, merged_df, rows, cols):
    
    #image_data = merged_df.to_numpy()
    #num_bands = len(merged_df.columns)  # Number of bands
    #reshaped_data = image_data.reshape((rows, cols, num_bands))


    color_data = np.array(merged_df['Colour'])
    #reshaped_data = color_data.reshape((rows, cols))


    add_plot_distribution(color_data, result_image_label)


    #height, width = reshaped_data.shape[:2]

    ## Define the coordinates for the middle region
    #top = (height - 250) // 2
    #bottom = top + 250
    #left = (width - 250) // 2
    #right = left + 250

    ## Slice the image data to select the middle region
    #middle_region = reshaped_data[top:bottom, left:right]

    ## Calculate the mean of the middle region
    #mean_value = np.mean(middle_region)
    #mean_value = np.mean(reshaped_data)

    #min_value = reshaped_data.min()
    #max_value = reshaped_data.max()
    #adjusted_data = (reshaped_data - min_value) / (max_value - min_value) * 255


    
    #image = Image.fromarray(np.uint8(adjusted_data), mode='L')
    #resized_image = image.resize((250, 200))
    #photoImage = ImageTk.PhotoImage(resized_image)
    #result_image_label.image = photoImage
    #result_image_label.configure(image=photoImage)
    #result_label.configure(text=f"Color mean: {mean_value:.2f}")

def add_plot_distribution(data, result_image_label):
    # Flatten the reshaped_data to a 1D array
    # Plot the histogram
    fig = Figure(figsize=(5, 4), dpi=100)
    ax = fig.add_subplot(111)


    counts, bins = np.histogram(data, bins='auto')
    filtered_counts = counts[counts > 200]
    filtered_bins = bins[:-1][counts > 200] 

    #ax.hist(data, bins='auto', alpha=0.7, rwidth=0.85)
    ax.bar(filtered_bins, filtered_counts, width=np.diff(bins)[0], align='edge', alpha=0.7)
    ax.set_title('Distribution of Water Color')
    ax.set_xlabel('Colour (mgPt/l)')
    ax.set_ylabel('Frequency')
    fig.savefig('plot.png')

    plot_image = Image.open('plot.png')
    plot_photo = ImageTk.PhotoImage(plot_image)
    result_image_label.config(image=plot_photo)
    result_image_label.image = plot_photo

def run(result_image_label, result_label, params):
  
    bands = parse_exif_files(params.exif_files)
    a0 = np.array([0.00345, -0.000005845])
    a1 = np.array([0.5592, 0.0006209])
    bands['frequency'] = bands['frequency'].str.extract(r'(\d+)')
    bands['frequency'] = bands['frequency'].astype(int)
    bands['a0'] = bands['frequency'].apply(lambda x: a0[0] + a0[1] * x)
    bands['a1'] = bands['frequency'].apply(lambda x: (a1[0] + a1[1] * x) - 0.093174)



    spectra, rows, cols = parse_tif_files(params.tif_files, bands)
    #TODO: here we should calculate water color with Niklas formula

    # Add data from Niklas doc
    niklas_row = pd.DataFrame({'560': [0.192655], '650': [0.141432], '730': [0.255875], '860': [0.234616]})
    # Add the new row at the top
    spectra = pd.concat([niklas_row, spectra], ignore_index=True)

    spectra_bands = spectra.columns
    for band in spectra_bands:
        a1 = bands.loc[bands['frequency'] == int(band), 'a1'].values[0]
        a0 = bands.loc[bands['frequency'] == int(band), 'a0'].values[0]
        spectra['Rs' + band] = spectra[spectra_bands[-1]].apply(lambda x: a1*x+a0)
      

    for band in spectra_bands:
        spectra['Rrs' + band] = spectra[band] - spectra['Rs' + band] 
        
    for band in spectra_bands:
        spectra['Rrs_aw' + band] = spectra['Rrs' + band].apply(lambda x: x/0.54)

    spectra['bbsp730'] = spectra['Rrs_aw730']*1.799/0.083
    spectra['bbsp560'] = spectra['bbsp730']*(560/730)**-1.4
    spectra['bbsp650'] = spectra['bbsp730']*(650/730)**-1.4
    spectra['bbsp860'] = spectra['bbsp730']*(840/730)**-1.4


    for band in spectra_bands:
        spectra['bsp' + band] = spectra['bbsp' + band].apply(lambda x: x/0.022)


    for band in spectra_bands:
        spectra['a' + band] = (0.083 * spectra['bbsp' + band] )/spectra['Rrs_aw' + band]

    
    spectra['a860'] = 4.3

    spectra['aCOM560'] = spectra['a560']-0.0724
    spectra['aCOM650'] = spectra['a650']-0.3445
    spectra['aCOM730'] = spectra['a730']-1.7990
    spectra['aCOM860'] = spectra['a860']-4.3

    spectra['AbsPCDOM560'] = 0.4343*spectra['aCOM560']*0.05
    spectra['AbsPCDOM410'] = spectra['AbsPCDOM560']*math.exp(-0.013*(410-560))

    spectra['Colour'] = spectra['AbsPCDOM410']*390


    spectra.head(3).to_csv('spectra_head.csv', index=False)

    populate_result(result_image_label, result_label, spectra, rows, cols)
   
   




class Params():
    exif_files = []
    tif_files = []
# GUI part
class GUI():


    def select_directory(self, label, filetypes, listbox):
        file_paths = filedialog.askopenfilenames(filetypes=filetypes)
        listbox.insert(tk.END, *file_paths) 
        if label.cget("text") == 'Select exif files':
            self.params.exif_files = file_paths
        elif label.cget("text") == 'Select tif files':
            self.params.tif_files = file_paths
        if self.params.exif_files and self.params.tif_files:
            self.button_run['state'] = 'normal'

    def __init__(self):
        root = tk.Tk()

        self.params = Params()
        root.title('WATER COLOR')

        window_width = 400
        window_height = 520

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        center_x = int(screen_width/2 - window_width / 2)
        center_y = int(screen_height/2 - window_height / 2)

        root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

        exif_label = tk.Label(root, text='Select exif files')
        exif_label.grid(row=0, column=0, padx=10)
        exif_button = tk.Button(root, text="Browse", command=lambda: self.select_directory(exif_label, [("Exif Files", "*.txt")], exif_listbox))
        exif_button.grid(row=2, column=0, padx=10)

        exif_listbox = Listbox(root)
        exif_listbox.grid(row=1, column=0, padx=10)



        tif_label = tk.Label(root, text='Select tif files')
        tif_label.grid(row=0, column=1)
        tif_button = tk.Button(root, text="Browse", command=lambda: self.select_directory(tif_label, [("TIFF Files", "*.TIF")], tif_listbox))
        tif_button.grid(row=2, column=1)

        tif_listbox = Listbox(root)
        tif_listbox.grid(row=1, column=1)

        self.result_image_label = tk.Label(root, text='Will present result here')
        self.result_image_label.grid(row=4, column=0, columnspan=3, pady=(10, 0))
        self.result_label = tk.Label(root, text='')
        self.result_label.grid(row=5, column=0, columnspan=3, pady=(10, 0))

        self.button_run = tk.Button(root, text="Run", command=lambda: run(self.result_image_label, self.result_label, self.params))
        self.button_run['state'] = 'disabled'
        self.button_run.grid(row=3, column=0, columnspan=2, pady=(10, 0))

       
        root.mainloop()


    


gui = GUI()
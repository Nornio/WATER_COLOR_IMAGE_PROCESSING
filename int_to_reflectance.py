from PIL import Image
import numpy as np
import os
import matplotlib.pyplot as plt

# Input and output folders
input_folder = '.'  # Use a relative path for the current directory
output_folder = 'output_folder'  # Specify the name of your output folder

# Ensure the output folder exists, create it if necessary
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# List all files in the input folder
file_list = os.listdir(input_folder)

# Process each TIFF image in the input folder
for filename in file_list:
    if filename.endswith('.tif') or filename.endswith('.TIF'):
        # Open the TIFF image using PIL (Pillow)
        image = Image.open(os.path.join(input_folder, filename))

        # Convert the image to a NumPy array
        image_array = np.array(image, dtype=np.uint16)

        # Calculate the span (range) of the pixel values in the original image
        value_range_original = np.ptp(image_array)

        # Scale the pixel values to the reflectance range [0, 1]
        image_array = image_array / 65535.0

        # Create a Matplotlib figure and axis
        fig, ax = plt.subplots()

        # Display the image with the "viridis" colormap
        im = ax.imshow(image_array, cmap='viridis', vmin=0, vmax=1)
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Reflectance Value')

        # Save the figure with the colorbar to the output folder
        output_path = os.path.join(output_folder, filename)
        plt.savefig(output_path)

        # Calculate the span (range) of the pixel values in the converted image
        value_range = np.ptp(image_array)
        print(f"Converted and saved: {output_path}")
        print(f"Value Range in {filename}: {value_range}")

        # Close the Matplotlib figure
        plt.close()

print("Conversion complete.")

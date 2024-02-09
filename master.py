

import sys
import subprocess

# Run install_dependency.py before importing any modules
subprocess.run([sys.executable, 'install_dependency.py'])

import subprocess
import os
import sys
from contextlib import contextmanager
import tkinter as tk
from tkinter import filedialog, messagebox

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

# Create and open the Sum_Script_Prints.txt file for writing
with open('Sum_Script_Prints.txt', 'w') as print_file:

    @contextmanager
    def suppress_output():
        # Redirect stdout and stderr to the Sum_Script_Prints.txt file
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        sys.stdout = print_file
        sys.stderr = print_file
        yield
        # Restore stdout and stderr
        sys.stdout = original_stdout
        sys.stderr = original_stderr

    def run_script(script_path, args=None):
        script_name = os.path.basename(script_path)  # Extract script name from script_path
        print(f'Running {script_path}')
        command = ['python3', script_path]
        if args:
            command.extend(args)


        try:
            with suppress_output():
                result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=os.environ, text=True, universal_newlines=True)

            script_output = result.stdout
            script_error = result.stderr

            # Split the script output by lines and filter/print desired lines
            lines = script_output.split('\n')
            for line in lines:
                if "Running..." in line or line.startswith("step"):
                    print(f'{script_name}: {line}')  # Include script_name before each line

            # Append script_error to the Sum_Script_Prints.txt file
            if script_error:
                print(f'{script_name}: Error: {script_error}')  # Include script_name before error message

            return script_output

        except Exception as e:
            print(f'Error running {script_path}: {str(e)}\n')

def select_directory(entry, is_file=False):
    if is_file:
        file_path = filedialog.askopenfilename(filetypes=[("TIFF Files", "*.TIF"), ("All Files", "*.*")])
        entry.delete(0, 'end')
        entry.insert(0, file_path)
    else:
        directory = filedialog.askdirectory()
        entry.delete(0, 'end')
        entry.insert(0, directory)


def select_directory(entry_widget):
    folder_path = filedialog.askdirectory()
    entry_widget.delete(0, tk.END)
    entry_widget.insert(tk.END, folder_path)


def run():
    global is_reference_panel_selected

    exif_dir_path = entry_exif_dir.get()
    tif_dir_path = entry_tif_dir.get()
    output_dir_path = entry_output_dir.get()

  

    os.environ['EXIF_DIR'] = exif_dir_path
    os.environ['TIF_DIR'] = tif_dir_path
    os.environ['OUTPUT_DIR'] = output_dir_path


    outputs = []

    

    # Save output to file
    output_text = '\n'.join(outputs)
    output_file = os.path.join(output_dir_path, 'Sum_Script_Prints.txt')
    try:
        with open(output_file, 'w') as f:
            f.write(output_text)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to write to output file: {str(e)}")
        return

    # Optionally, you could also create an entry in Sum_Script_Prints.txt
    try:
        with open(output_file, 'a') as f:
            f.write(f'\nSummary script created at: {output_file}\n')
    except Exception as e:
        messagebox.showerror("Error", f"Failed to write to output file: {str(e)}")

    print(f'Output written to {output_file}')
    root.destroy()
    os._exit(0)  # force exit

# GUI part
root = tk.Tk()


label_output_dir = tk.Label(root, text="Directory Path of output")
label_output_dir.pack()
entry_output_dir = tk.Entry(root)
entry_output_dir.pack()
button_output_dir = tk.Button(root, text="Browse", command=lambda: select_directory(entry_output_dir))
button_output_dir.pack()

label_exif_dir = tk.Label(root, text="Directory Path of exif")
label_exif_dir.pack()
entry_exif_dir = tk.Entry(root)
entry_exif_dir.pack()
button_exif_dir = tk.Button(root, text="Browse", command=lambda: select_directory(entry_exif_dir))
button_exif_dir.pack()


label_tif_dir = tk.Label(root, text="Image input Directory")
label_tif_dir.pack()
entry_tif_dir = tk.Entry(root)
entry_tif_dir.pack()
button_tif_dir = tk.Button(root, text="Browse", command=lambda: select_directory(entry_tif_dir))
button_tif_dir.pack()

button_run = tk.Button(root, text="Run", command=run)
button_run.pack()

root.mainloop()
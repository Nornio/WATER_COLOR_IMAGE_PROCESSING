# Script Description: This script checks for the presence of required Python dependencies and the exiftool utility. If any dependency is missing, it attempts to install it using pip. If exiftool is missing, it attempts to install it using the apt-get package manager on Ubuntu.

# The script performs the following steps:
# 1. Defines a dictionary (dependencies) that maps package names to module names.
# 2. Defines a function (is_module_installed) to check if a Python module is installed.
# 3. Defines a function (install_dependency) to install a Python package using pip.
# 4. Defines a function (install_exiftool) to install exiftool using apt-get on Ubuntu.
# 5. Defines a function (is_exiftool_installed) to check if exiftool is installed.
# 6. Initializes a variable (all_installed) to track if all dependencies are installed.
# 7. Checks and installs Python dependencies by looping through the dependencies dictionary.
# 8. Prints a message and attempts to install missing dependencies using pip.
# 9. Checks and installs exiftool if it is not installed.
# 10. Prints a confirmation message indicating the installation status of all dependencies.

# This script is useful for automating the installation of required Python dependencies and exiftool, ensuring that the necessary tools are available for subsequent processes.

# Script Developed by:
# Name: Mattias Tancred
# Organization: Structor Miljöteknik AB
# Contact Information:
# Email: mattias.tancred@structor.se



import sys
import subprocess

# Check if the required Python interpreter is available
if not hasattr(sys, 'executable'):
    print("Error: Python interpreter is not available.")
    print("Please install Python and then try again.")
    sys.exit(1)

# List of dependencies and their instructions
dependencies = {
    'numpy': 'numpy',
    'Pillow': 'PIL',
    'tifffile': 'tifffile',
    'matplotlib': 'matplotlib',
    'pyexifinfo': 'pyexifinfo',
    'imageio': 'imageio',
    'seaborn': 'seaborn',
    'folium': 'folium',
    'exifread': 'exifread',
    'scipy': 'scipy'
}

def is_module_installed(module_name):
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False

def install_dependency(package_name):
    subprocess.run(['pip3', 'install', package_name])

def prompt_install(dependency_name, install_command):
    choice = input(f"{dependency_name} is missing. Do you want to install it? (y/n): ").lower()
    if choice == 'y':
        subprocess.run(install_command, shell=True)
    else:
        print(f"Skipping {dependency_name} installation.")

def main():
    all_installed = True

    # Check and prompt user to install dependencies
    dependency_prompts = [('tkinter', 'sudo apt-get install python3-tk'),
                          ('exiftool', 'sudo apt-get install libimage-exiftool-perl'),
                          ('opencv', 'pip3 install opencv-python')]

    for dependency_name, install_command in dependency_prompts:
        if dependency_name in dependencies and not is_module_installed(dependencies[dependency_name]):
            prompt_install(dependency_name, install_command)
            if not is_module_installed(dependencies[dependency_name]):
                all_installed = False

    # Check and install Python dependencies
    for package_name, module_name in dependencies.items():
        if package_name not in ['tkinter', 'exiftool', 'opencv'] and not is_module_installed(module_name):
            print(f"Installing missing dependency: {package_name}")
            install_dependency(package_name)
            if not is_module_installed(module_name):
                all_installed = False

    # Check and prompt user to install OpenCV
    try:
        import cv2
    except ImportError:
        choice = input("OpenCV is missing. Do you want to install it? (y/n): ").lower()
        if choice == 'y':
            install_dependency('opencv-python')
            if not is_module_installed('cv2'):
                all_installed = False
        else:
            print("Skipping OpenCV installation.")

    # Print confirmation message
    if all_installed:
        print("All dependencies are installed.")
        print("Experimental code, engage your brain.")
    else:
        print("Some dependencies could not be installed.")

if __name__ == "__main__":
    main()

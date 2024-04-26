import glob
import os
import sys
import argparse
import subprocess
import shutil

# Function to locate the Colmap executable on the system PATH
def find_colmap():
    # Retrieve the system PATH environment variable
    system_path = os.getenv('PATH')
    
    # Split the PATH into individual directories
    directories = system_path.split(os.pathsep)

    # Iterate through each directory in the PATH to find 'colmap.exe'
    for directory in directories:
        colmap_path = os.path.join(directory, 'colmap.exe')
        
        # If 'colmap.exe' is found, return the full path
        if os.path.exists(colmap_path):
            return colmap_path

# Modify the path to point to a batch file if necessary
def modify_path_for_batch(path):
    # Adjust the path to point to a 'COLMAP.bat' instead of 'colmap.exe'
    base_path = path[:-len(r'\bin\colmap.exe')]
    batch_path = os.path.join(base_path, 'COLMAP.bat')
    return batch_path

# Get the path to the Python 'Scripts' directory where executables are located
def get_python_scripts_path():
    # Determine the directory of the current Python executable
    python_dir = os.path.dirname(sys.executable)
    
    # Append 'Scripts' to the directory path to get to script executables
    scripts_path = os.path.join(python_dir, 'Scripts')
    return scripts_path

# Set up the argument parser for command line arguments
def setup_arg_parser():
    parser = argparse.ArgumentParser(description="Automate image processing workflow.")
    parser.add_argument("--working_dir", type=str, required=True, help="Working directory where 'bundle.out' and 'imagelist.lst' should be located")
    parser.add_argument("--images_dir", type=str, required=True, help="Directory containing images")
    return parser

# Check if required files exist in the specified directory and return their full paths
def check_required_files(working_dir):
    # File extensions to search for
    file_extensions = ['.out', '.lst']
    found_files = {ext: None for ext in file_extensions}
    
    # Search for files with the required extensions
    for file in os.listdir(working_dir):
        _, ext = os.path.splitext(file)
        if ext in file_extensions:
            if found_files[ext] is not None:
                print(f"Error: Multiple '{ext}' files found in the directory '{working_dir}'.")
                sys.exit(1)
            found_files[ext] = os.path.join(working_dir, file)
    
    # Check if all required files are found
    if None in found_files.values():
        missing_types = ', '.join([ext for ext, path in found_files.items() if path is None])
        print(f"Error: No file with the following extensions found in the directory '{working_dir}': {missing_types}")
        sys.exit(1)
    
    return found_files['.out'], found_files['.lst']


# Convert the list of images from one format to another

def convert_imagelist(directory):
    # Find the only .lst file in the directory
    lst_files = glob.glob(os.path.join(directory, '*.lst'))
    if len(lst_files) != 1:
        raise Exception(f"Expected exactly one .lst file in directory {directory}, but found {len(lst_files)}")
    imagelist = lst_files[0]

    print(f"Processing imagelist: '{imagelist}'")
    with open(imagelist, 'r') as f:
        filenames = [os.path.split(line.strip())[1] for line in f]
    local_list_path = os.path.join(directory, os.path.splitext(os.path.basename(imagelist))[0] + '-local.lst')
    with open(local_list_path, 'w') as f_out:
        f_out.write("\n".join(filenames) + "\n")
    return local_list_path

# Install a specified Python package using pip
def install_package(package_name):
    print(f"Installing package: '{package_name}'")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"Success: The package '{package_name}' was installed.")
    except subprocess.CalledProcessError:
        print("Error: The package installation failed.")


def main():
    parser = setup_arg_parser()
    args = parser.parse_args()

    scripts_path = get_python_scripts_path()
    colmap_executable = find_colmap()
    colmap_bat = modify_path_for_batch(colmap_executable)

    # Get paths for the required files, updated to directly use the full file paths
    bundle_path, imagelist_path = check_required_files(args.working_dir)

    # Prepare directories for different stages of the dataset processing
    dataset_bundle_dir = "dataset-bundle"
    dataset_kapture_dir = "dataset-kapture"
    dataset_colmap_dir = "dataset-colmap"

    # Check if directories exist and remove them
    for dir_path in [dataset_kapture_dir, dataset_colmap_dir]:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
            print(f"Deleted existing directory: {dir_path}")

    os.makedirs(dataset_bundle_dir, exist_ok=True)
    os.makedirs(os.path.join(dataset_bundle_dir, "images"), exist_ok=True)
    os.makedirs(dataset_kapture_dir, exist_ok=True)
    os.makedirs(dataset_colmap_dir, exist_ok=True)
    # Stored converted text format to binary format here
    os.makedirs(f"{dataset_colmap_dir}/sparse/0", exist_ok=True)

    # Copy necessary files to their respective directories
    shutil.copy2(imagelist_path, os.path.join(dataset_bundle_dir, os.path.basename(imagelist_path)))
    shutil.copy2(bundle_path, os.path.join(dataset_bundle_dir, os.path.basename(bundle_path)))

    print(f"Copying images from '{args.images_dir}' to '{dataset_bundle_dir}/images'")
    images_dir = args.images_dir
    for file in os.listdir(images_dir):
        shutil.copy2(os.path.join(images_dir, file), os.path.join(dataset_bundle_dir, "images", file))

    local_imagelist = convert_imagelist(os.path.dirname(imagelist_path))

    install_package('kapture')

    # Convert from Bundler format to Kapture, followed by Colmap processes
    subprocess.run([
        'py', os.path.join(scripts_path, 'kapture_import_bundler.py'), '-v', 'debug', 
        '-i', bundle_path, '-l', local_imagelist, 
        '-im', os.path.join(dataset_bundle_dir, "images"), '--image_transfer', 'link_absolute', 
        '-o', dataset_kapture_dir, '--add-reconstruction'
    ], check=True)

    # Export Kapture data to Colmap format
    subprocess.run([
       'py', os.path.join(scripts_path, 'kapture_export_colmap.py'),  '-v', 'debug', '-f', 
        '-i', dataset_kapture_dir, '-db', f'{dataset_colmap_dir}/colmap.db', 
        '--reconstruction', f'{dataset_colmap_dir}/reconstruction-txt'
    ], check=True)


    # Convert from text format to binary format in Colmap
    subprocess.run([
        colmap_bat, 'model_converter', '--input_path', f'{dataset_colmap_dir}/reconstruction-txt', 
        '--output_path', f'{dataset_colmap_dir}/sparse/0', '--output_type', 'BIN'
    ], check=True)


    # Create a directory if it does not exist already called 'colmap-workspace'
    os.makedirs('colmap-workspace', exist_ok=True)

    # Movethe dataset-colmap, dataset-kapture, and dataset-bundle directories to the 'colmap-workspace' directory
    shutil.move(dataset_colmap_dir, 'colmap-workspace')
    shutil.move(dataset_kapture_dir, 'colmap-workspace')
    shutil.move(dataset_bundle_dir, 'colmap-workspace')

if __name__ == "__main__":
    main()

import streamlit as st
import os
from pathlib import Path
import shutil
import glob
import subprocess

class MainApp:
    
    def __init__(self):
        # Initialize session state variables if they don't exist
        if 'working_dir' not in st.session_state:
            st.session_state['working_dir'] = ''
        if 'images_dir' not in st.session_state:
            st.session_state['images_dir'] = ''
        if 'output_dir' not in st.session_state:
            st.session_state['output_dir'] = ''  # Set a default value for output_dir here
            
    def update_directories(self):
        if st.session_state['working_dir'] != '' and st.session_state['output_dir'] == '':
            # Set the default output directory only if no output directory has been set
            st.session_state['output_dir'] = Path.cwd() / "colmap-workspace"

    def create_stage_directories(self):
        if st.session_state['output_dir'] != '':
            output_dir = Path(st.session_state['output_dir'])
            output_dir.mkdir(parents=True, exist_ok=True)
            st.success("Output directory created successfully! Continuing to the next step.")
        
        # Using pathlib to create directories dataset-bundle, dataset-kapture, dataset-colmap inside working directory
        if  st.session_state['working_dir'] != '':
            output_dir = Path( st.session_state['output_dir'])
            dataset_bundle = output_dir / "dataset-bundle"
            dataset_bundle_images = output_dir / "dataset-bundle" / "images"
            dataset_kapture = output_dir / "dataset-kapture"
            dataset_colmap = output_dir / "dataset-colmap"
            dataset_colmap_sparse = output_dir / "dataset-colmap" / "sparse" / "0"
            
            dataset_bundle.mkdir(parents=True, exist_ok=True)
            dataset_kapture.mkdir(parents=True, exist_ok=True)
            
            dataset_colmap.mkdir(parents=True, exist_ok=True)
            dataset_colmap_sparse.mkdir(parents=True, exist_ok=True)
            
            st.session_state['dataset_bundle'] = dataset_bundle 
            st.session_state['dataset_bundle_images'] = dataset_bundle_images
            st.session_state['dataset_kapture'] = dataset_kapture
            
            st.session_state['dataset_colmap'] = dataset_colmap
            st.session_state['dataset_colmap_sparse'] = dataset_colmap_sparse
            
            st.success("Stage directories created successfully! Continuing to the next step.")
        else:
            st.error("Working directory path is not set. Please enter a valid path.")
            
    # Function to clear output directory
    def clear_output_dir(self):
        # check if the output directory exists in the system if so, delete contents
        if os.path.isdir(st.session_state['output_dir']):
            print(st.session_state['output_dir'])
            print("Output directory exists")
            output_dir = Path(st.session_state['output_dir'])
            for item in output_dir.iterdir():
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    os.remove(item)
            # Check if the directory is empty
            if not any(output_dir.iterdir()):
                st.success("Output directory cleared successfully!")
            else:
                st.error("Failed to clear the output directory!")
                st.error("Please refresh the page and start again.")
                st.stop()
    
    def check_required_files(self):
        """
        Check if the required files exist in the specified directory and return their full paths.
        """
        # File extensions to search for
        file_extensions = ['.out', '.lst']
        found_files = {ext: None for ext in file_extensions}
        
        # Search for files with the required extensions
        for file in Path(st.session_state['working_dir']).iterdir():
            if file.suffix in file_extensions:
                if found_files[file.suffix] is not None:
                    print(f"Error: Multiple '{file.suffix}' files found in the directory '{st.session_state['working_dir']}'.")
                    st.error("Multiple `.out` or `.lst` files found in the working directory")
                    st.stop()
                found_files[file.suffix] = file
        
        # Check if all required files are found
        if None in found_files.values():
            missing_types = ', '.join([ext for ext, path in found_files.items() if path is None])
            print(f"Error: No file with the following extensions found in the directory '{st.session_state['working_dir']}': {missing_types}")
            st.error("No `.out` or `.lst` file found in the working directory")
            st.stop()
        
        
        st.session_state['out_file_path'], st.session_state['lst_file_path'] = found_files['.out'], found_files['.lst']
    
    def find_colmap_and_batch(self):
        # Retrieve the system PATH environment variable
        system_path = os.getenv('PATH')
        
        # Split the PATH into individual directories
        directories = system_path.split(os.pathsep)

        # Initialize paths
        colmap_exe_path = None
        colmap_batch_path = None

        # Iterate through each directory in the PATH to find 'colmap.exe'
        for directory in directories:
            potential_path = os.path.join(directory, 'colmap.exe')
            
            # If 'colmap.exe' is found, set the paths
            if os.path.exists(potential_path):
                colmap_exe_path = potential_path
                base_path = potential_path[:-len(r'\bin\colmap.exe')]
                colmap_batch_path = os.path.join(base_path, 'COLMAP.bat')
                break
                
        st.session_state['colmap_exe_path'] = colmap_exe_path
        st.session_state['colmap_batch_path'] = colmap_batch_path
    
    def get_kapture_paths(self):
        st.session_state['kapture_import_path'] = Path.cwd() / "kapture" / 'kapture_import_bundler.py'
        st.session_state['kapture_export_path'] = Path.cwd() / "kapture" / 'kapture_export_colmap.py'
    
    def convert_imagelist(self):
        print("Converting imagelist...")
        # Find the only .lst file in the directory
        lst_files = glob.glob(os.path.join(st.session_state['working_dir'], '*.lst'))
        if len(lst_files) != 1:
            raise Exception(f"Expected exactly one .lst file in directory {st.session_state['working_dir']}, but found {len(lst_files)}")
        imagelist = lst_files[0]

        print(f"Processing imagelist: '{imagelist}'")
        with open(imagelist, 'r') as f:
            filenames = [os.path.split(line.strip())[1] for line in f]
        local_list_path = os.path.join(st.session_state['working_dir'], os.path.splitext(os.path.basename(imagelist))[0] + '-local.lst')
        with open(local_list_path, 'w') as f_out:
            f_out.write("\n".join(filenames) + "\n")
            
        st.session_state['local_list_path'] = local_list_path
        
    # function to delete all files int he working directory that end int `-local.lst`
    def delete_local_list_files(self):
        for file in glob.glob(os.path.join(st.session_state['working_dir'], '*-local*')):
            if os.path.isfile(file):
                os.remove(file)
                    
    
    def start_conversion(self):
        # if final-images-with-bin folder exists, delete it
        final_images_with_bin = st.session_state['output_dir'] / "final-images-with-bin"
        if os.path.isdir(final_images_with_bin):
            shutil.rmtree(final_images_with_bin)
            
        
        dataset_bundle_images = Path(st.session_state['dataset_bundle'], 'images')
        dataset_bundle_images.mkdir(parents=True, exist_ok=True)
        
        shutil.copy2(st.session_state['lst_file_path'], st.session_state['dataset_bundle'])
        shutil.copy2(st.session_state['out_file_path'], st.session_state['dataset_bundle'])
        
        # copy images from images directory to dataset-bundle/images
        print('Images Directory:', st.session_state['images_dir'])
        if os.path.isdir(st.session_state['images_dir']):
            for file in Path(st.session_state['images_dir']).iterdir():
                shutil.copy(file, Path(st.session_state['dataset_bundle_images']))
            # else:
            #     st.error("Images directory path is not set. Please enter a valid path.")
            #     st.stop()
                
        # Convert from Bundler format to Kapture, followed by Colmap processes
        step1 = subprocess.run([
            'python', st.session_state['kapture_import_path'], '-v', 'debug', 
            '-i', st.session_state['out_file_path'], '-l', st.session_state['local_list_path'],
            '-im', st.session_state['dataset_bundle_images'], '--image_transfer', 'link_absolute',
            '-o', st.session_state['dataset_kapture'], '--add-reconstruction'
        ], check=True)
        
        # if step1 succeeded, print success message
        if step1.returncode == 0:
            st.success("Bundler to Kapture conversion completed successfully! Continuing to the next step.")
         
         # Export Kapture data to Colmap format
        step2 = subprocess.run([
            'python', st.session_state['kapture_export_path'],  '-v', 'debug', '-f','-i', st.session_state['dataset_kapture'],
            '-db', f'{os.path.join(st.session_state['dataset_colmap'], "colmap.db")}',
            '--reconstruction', f'{os.path.join(st.session_state['dataset_colmap'], "reconstruction-txt")}'
            ], check=True)
        
        # if step2 succeeded, print success message
        if step2.returncode == 0:
            st.success("Kapture to Colmap conversion completed successfully! Continuing to the next step.")

        
        step3 = subprocess.run([
                st.session_state['colmap_batch_path'], 'model_converter', '--input_path', f'{os.path.join(st.session_state['dataset_colmap'], "reconstruction-txt")}',
                '--output_path', f'{os.path.join(st.session_state['dataset_colmap'], "sparse", "0")}', '--output_type', 'BIN'
            ], check=True)

        # if step3 succeeded, print success message
        if step3.returncode == 0:
            st.success("Colmap model conversion completed successfully! Continuing to the next step.")
        
        # In the output directory, create a folder called final-images-with-bin
        final_images_with_bin = st.session_state['output_dir'] / "final-images-with-bin"
        final_images_with_bin.mkdir(parents=True, exist_ok=True)
        
        # Move the images from dataset-bundle/images to final-images-with-bin
        for file in st.session_state['dataset_bundle_images'].iterdir():
            shutil.copy2(file, final_images_with_bin)
            
        # Copy all files in dataset-colmap/sparse/0 to final-images-with-bin
        path = st.session_state['dataset_colmap'] / 'sparse' / '0'
        for file in path.iterdir():
            shutil.copy2(file, final_images_with_bin)
            
        
        # Then delete the dataset-bundle, dataset-kapture, and dataset-colmap folders
        shutil.rmtree(st.session_state['dataset_bundle'])
        shutil.rmtree(st.session_state['dataset_kapture'])
        shutil.rmtree(st.session_state['dataset_colmap'])
        
        st.markdown("## Conversion process completed successfully!")
        st.markdown(f"You can simply drag and drop the `{st.session_state['output_dir']}/final-images-with-bin` folder to the PostShot application.")


def main():
    
    main_app = MainApp()
    
    st.title("Reality Capture to PostShot Workflow")
    
    # Input for working directory
    st.session_state['working_dir'] = st.text_input("Enter working directory path:")
    st.write("This is the path where the `.out` and `.lst` files are stored.")
    st.write(" - Please ensure there is only one `.out` and `.lst` file in this directory.")
    st.markdown("---")
    # Input for images directory
    st.session_state['images_dir'] = st.text_input("Enter images directory path:")
    st.write("This is the path where the images are stored from the export during the `Undistorted imageslist with images` step.")
    st.markdown("---")
    # Output directory
    st.session_state['output_dir'] = st.text_input("Enter output directory path:(Optional)", placeholder="")
    st.write("This is output path where the final images with bin files will be in a folder called `final-images-with-bin` inside the output directory.")
    st.write("If no output directory is specified, the output will be saved in the current working directory of the `StreamlitGUI.py` file, in the folder called `colmap-workspace`.")
    st.markdown("---")
    
    # Initialize a flag for directory validation
    if 'directories_valid' not in st.session_state:
        st.session_state['directories_valid'] = False
    
    # Validate the working directory
    if st.button('Press to Validate Working and Images Directories'):
        if os.path.isdir(st.session_state['working_dir']):
            st.success(f"Working directory is valid: {st.session_state['working_dir']}")
            # Validate the images directory
            if os.path.isdir(st.session_state['images_dir']):
                st.success(f"Images directory is valid: {st.session_state['images_dir']}")
                st.session_state['directories_valid'] = True
            else:
                st.error("Invalid images directory path, that path does not exist.")
        else:
            st.error("Invalid working directory path, that path does not exist.")
            
            
    if 'conversion_completed' in st.session_state:
        st.session_state['conversion_completed'] = False
        
    # Button to create stage directories
    if  st.session_state['directories_valid']:
        if st.button("Start Conversion Process"):
            st.write("Starting conversion process...")
            st.write("Please wait, this process may take a few minutes or more depending on the number of images.")
            main_app.clear_output_dir()
            main_app.delete_local_list_files()
            main_app.update_directories()
            main_app.get_kapture_paths()
            main_app.create_stage_directories()
            main_app.check_required_files()
    
            main_app.find_colmap_and_batch()
            main_app.convert_imagelist()
            main_app.start_conversion()
            
        
            
            st.stop()
        


if __name__ == "__main__":
    main()

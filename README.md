

# RealityCapture to Colmap to Postshot Script

> This script was made to simplify the process from this guide: https://gist.github.com/jo-chemla/258e6e40d3d6c2220b29518ff3c17c40 by [jo-chemla](https://gist.github.com/jo-chemla)

This repository contains a Python script designed to automate the process of converting images and data from RealityCapture to a format compatible with Postshot via Colmap.

## Prerequisites

- Ensure you have Python installed on your system, and the `pip` package manager is functional.
- Install Colmap on your system. You can download it from the [Colmap github](https://github.com/colmap/colmap).
- Ensure that `colmap.exe` and `colmap.bat` are exposed on your computer's PATH environment variable. This means that you should be able to run `colmap` from any directory in the command line.

**Example (depending on your installation path is):**
- E:\Program Files\Colmap\COLMAP-3.9.1-windows-cuda (location of colmap.bat)
- E:\Program Files\Colmap\COLMAP-3.9.1-windows-cuda\bin (location of colmap.exe)

These two paths should be added to your system's PATH as environment variables.


## Installation

Clone this repository to your local machine using:

```bash
git clone https://github.com/your-repository-url.git
```

Navigate to the cloned directory:

```bash
cd RealityCapture-to-Postshot
```

## Exporting Files from RealityCapture

### Export Step 1: the Bundler `.out` File

Choose a folder to store the exported file.

1. Set `Fit` option to `Inner Region`.
2. Set `Resolution` option to `Fit`.
3. Ensure `Export Images` is set to `No`.
   - **We will export the images separately in the next step when exporting the undistorted images with image list.**

![alt text](/media/bundler.png)

### Export Step 2: the Undistorted Images with Image List

Choose a folder to store the exported file.

1. Set `Fit` option to `Inner Region`.
2. Set `Resolution` option to `Fit`.
3. Under `Export image settings`, choose the desired image format (preferably `jpg` or `jpeg`).
4. Set `Naming Convention` to `original file name`.
5. Enable `Customize image path` and select the folder to store images.
6. (Optional) Adjust the `Downscale` option if required.

![alt text](/media/imagelist.png)

## Running the Script

### Configuration

The script requires the following directory arguments:

- `--images_dir`: The path to the folder containing the undistorted images. (The folder selected in the previous step for the undistorted images)
- `--working_dir`: The path to the folder containing the `.out` and `.lst` files. (The folder selected in the first step)

**Note:** The script expects `colmap.exe` to be exposed on your computer's PATH.

### Example Command

```bash
py RealityCaptureToColmap.py --working_dir "<full path to working directory from previous export step 1>" --images_dir "<full path to images folder from previous export step 2>" 
```

### Execution

Run the script from the command line. It will install the necessary `kapture` package into your Python environment and process the provided directories.

## Outputs

Upon successful execution, the script outputs a `colmap-workspace` folder in the working directory with subfolders for different dataset stages. The `dataset-colmap` folder contains the necessary files for Postshot import. Look for the `cameras.bin` in `dataset-colmap\sparse\0`.

## Importing to Postshot

Copy the `cameras.bin` file (from the `colmap-workspace\dataset-colmap\sparse\0` folder) and the images (exported from RealityCapture) into the **same folder**. Then simply drag and drop the folder into Postshot to start the import process.

You should see this pop-up window, showing `Camera Poses` set to `import`. (this means the that is imported the cameras.bin file successfully), you can now start training.

![alt text](/media/postshot.png)


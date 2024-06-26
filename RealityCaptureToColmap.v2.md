# RealityCapture to Colmap to Postshot Script

> This script was made to simplify the process from this guide: https://gist.github.com/jo-chemla/258e6e40d3d6c2220b29518ff3c17c40 by [jo-chemla](https://gist.github.com/jo-chemla)

This repository contains a Python script designed to automate the process of converting images and data from RealityCapture to a format compatible with Postshot via Colmap.

## Prerequisites

- Ensure you have Python installed on your system, and the `pip` package manager is functional.
- Install Colmap on your system. You can download it from the [Colmap github](https://github.com/colmap/colmap).
- Ensure that `colmap.exe` and `colmap.bat` are exposed on your computer's PATH environment variable. This means that you should be able to run `colmap` from any directory in the command line.

#### **Example paths for colmap exe and bat (<u>depending on your own installation path you need to define</u>):**

(location of colmap.bat)
- `E:\Program Files\Colmap\COLMAP-3.9.1-windows-cuda`     

(location of colmap.exe)
- `E:\Program Files\Colmap\COLMAP-3.9.1-windows-cuda\bin`   

These two paths should be added to your system's PATH as environment variables.

<img src="./media/path.png" width="500" >

## Installation

Clone this repository to your local machine using:

```bash
git clone https://github.com/Maxiviper117/RealityCapture-to-Postshot
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
   - **We will export the images separately in the next step when exporting the `Undistorted images with image list.` export option**

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
- `--output_dir`: (**OPTIONAL**) - The path to the folder where the script will output the Colmap workspace. (defaults to a folder named `colmap-workspace` in the working directory)

### Example Command

#### **NOTE: Must run the script from the command line as an administrator.**

```bash
py RealityCaptureToColmap.v2.py --working_dir "<full path to working directory from previous export step 1>" --images_dir "<full path to images folder from previous export step 2>" 
```

Option choose the output directory:

```bash
py RealityCaptureToColmap.v2.py --working_dir "<full path to working directory from previous export step 1>" --images_dir "<full path to images folder from previous export step 2>" --output_dir "<full path to output directory>"
```

### Execution

Run the script from the command line. It will install the necessary `kapture` package into your Python environment and process the provided directories.

## Outputs

Upon successful execution, the script outputs a `colmap-workspace` (or the specified output directory) folder in the working directory with subfolders for different dataset stages. The `dataset-colmap` folder contains the necessary files for Postshot import. Look for the `.bin` files in `dataset-colmap\sparse\0`.

![alt text](/media/camerabin.png)

## Importing to Postshot (Option 1)

Copy the all three `cameras.bin`, `images.bin` and `points3D.bin`  file (from the `<output_dir>\dataset-colmap\sparse\0` folder) and the images (exported from RealityCapture) into the **same folder**. (Either all three bin files in that same images folder or all images and bin files in a new folder)

Then simply drag and drop the folder into Postshot to start the import process.
<!-- ![alt text](dragdrop.png) -->
<img src="./media/dragdrop.png" width="600" >



You should see this pop-up window, showing `Camera Poses` set to `import`. (this means the that it imported the cameras.bin file successfully), you can now start training.

![alt text](/media/postshot.png)

## Failed to import camera poses error.

If you see this error, when you drag and drop the folder into Postshot, try close and open Postshot again, and drag and drop the folder again.

<!-- ![alt text](./media/error.png) -->
<img src="./media/error.png" width="800" >

## Importing to Postshot (Option 2)

Another way to import the data into Postshot is to first import the images separately, when the pop-up window appears, uncheck option `start training` then click import.
<!-- ![alt text](/media/starttrainting.png) -->
<img src="./media/starttrainting.png" width="500" >

Then select the image set, then at the bottom right corner, under `Actions` fold, click on `Import Camera Poses` and select the `cameras.bin` file.

<!-- ![alt text](/media/poses.png) -->
<img src="./media/poses.png" width="800" >





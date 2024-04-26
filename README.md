### Updated README for GitHub Repository

---

# RealityCapture to Postshot Conversion Tool

This repository contains a Python script designed to automate the process of converting images and data from RealityCapture to a format compatible with Postshot via Colmap.

## Prerequisites

Ensure you have Python installed on your system, and the `pip` package manager is functional. Additionally, ensure that `colmap.exe` is exposed on your computer's PATH environment variable.

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

### Export the Bundler `.out` File

1. Set `Fit` option to `Inner Region`.
2. Set `Resolution` option to `Fit`.
3. Ensure `Export Images` is set to `No`.

![alt text](/media/bundler.png)

### Export the Undistorted Images with Image List

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

- `--images_dir`: The path to the folder containing the undistorted images.
- `--working_dir`: The path to the folder containing the `.out` and `.lst` files.

**Note:** The script expects `colmap.exe` to be exposed on your computer's PATH.

### Example Command

```bash
py RealityCaptureToColmap.py --images_dir "E:\DEV\python\RealityCapture-to-Postshot\src\images" --working_dir "./src"
```

### Execution

Run the script from the command line. It will install the necessary `kapture` package into your Python environment and process the provided directories.

## Outputs

Upon successful execution, the script outputs a `colmap-workspace` folder in the working directory with subfolders for different dataset stages. The `dataset-colmap` folder contains the necessary files for Postshot import. Look for the `cameras.bin` in `dataset-colmap\sparse\0`.

## Importing to Postshot

Move the `cameras.bin` file (from the `colmap-workspace\dataset-colmap\sparse\0` folder) and the images (exported from RealityCapture) into the same folder. Then simply drag and drop the folder into Postshot to start the import process.

You should see this pop-up window, showing `Camera Poses` set to import. (this means the that is imported the cameras.bin file successfully), you can now start training.

![alt text](/media/postshot.png)


# Raidionics
[![license](https://img.shields.io/github/license/DAVFoundation/captain-n3m0.svg?style=flat-square)](https://github.com/DAVFoundation/captain-n3m0/blob/master/LICENSE)
[![GitHub Downloads](https://img.shields.io/github/downloads/dbouget/Raidionics/total?label=GitHub%20downloads&logo=github)](https://github.com/dbouget/Raidionics/releases)
![CI](https://github.com/dbouget/Raidionics/workflows/Build%20Windows/badge.svg?branch=master&event=push)
![CI](https://github.com/dbouget/Raidionics/workflows/Build%20Ubuntu/badge.svg?branch=master&event=push)
![CI](https://github.com/dbouget/Raidionics/workflows/Build%20macOS/badge.svg?branch=master&event=push)

## 1. Description
Software to automatically segment brain tumors from pre-operative MRI scans, compute their characteristics (e.g., volume, location), and generate a standardized report.

The software was introduced in the article "Brain tumor preoperative surgery imaging: models and software solutions for
segmentation and standardized reporting", which has been accepted for publication in [Frontiers in Neurology](https://www.frontiersin.org/journals/neurology).

## 2. Softwares and usage
An installer is provided for the three main Operating Systems: Windows (>= v10, 64-bit), macOS (>= Catalina), and Ubuntu Linux (>= 18.04). Software has been tested and found working on the newest Windows 11 and macOS Monterey operating systems.The software can be downloaded from [here](https://github.com/dbouget/Raidionics/releases) (see **Assets**). 

### 2.1 Download and installation
These steps are only needed to do once:
1) Download the installer to your Operating System.
2) Right click the downloaded file, click "open", and follow the instructions to install.
3) Search for the software "Raidionics" and double click to run.

### 2.2 Usage  
Two modes are proposed: (i) Single-use for processing one MRI scan at a time with the possibility to view and interact with the results, and (ii) Batch-mode for processing multiple MRI scans in a row, without any vizualisation.

For the single use case:
  1) Click 'Input MRI...' to select from your file explorer the MRI scan to process (unique file), preferably as nifti (*.nii, *.nii.gz).  
  1*) Alternatively, Click 'File > Import DICOM...' if you wish to process an MRI scan as a DICOM sequence.  
  2) Click 'Output destination' to choose a directory where to save the results.  
  3) (OPTIONAL) Click 'Input segmentation' to choose a tumor segmentation mask file, if nothing is provided the internal model with generate the segmentation automatically.  
  4) Select the tumor type from the drop-down menu, supported types are: (i) High-Grade Glioma (glioblastoma), (ii) Low-Grade Glioma, (iii) Meningioma, and (iv) Metastasis.
  5) Click 'Run segmentation' to generate the brain tumor mask, or 'Run standard reporting' to perform the full analysis. The human-readable version of the results will be displayed directly in the interface.  

### 2.3 Computed features  
The following features are automatically computed and reported to the user:
- **Multifocality**: whether the tumor is multifocal or not, the total number of foci, and the largest minimum distance between two foci.  
- **Volume**: total tumor volume in original patient space and MNI space (in ml).  
- **Laterality**: tumor percentage in each hemisphere, and assessment of midline crossing.  
- **Resectability**: expected residual volumes (in ml) and resection index (for high-grade gliomas only).  
- **Cortical structures**: percentage of the tumor volume overlapping each structure from the MNI atlas, the Harvard-Oxford atlas, and Schaefer atlas (version 7 and 17).  
- **Subcortical structures**: percentage of the tumor volume overlapping each structure from the BCB atlas. If no overlap, the minimum distance to the structure is provided (in mm).  

### 2.4 Generated results  
  The output folder is populated automatically with the following:  
    * The diagnosis results in human-readable text (report.txt) and Excel-ready format (report.csv).  
    * The automatic segmentation masks of the brain and the tumor in the original patient space (input_brain_mask.nii.gz and input_tumor_mask.nii.gz).  
    * The cortical structures mask in original patient space for the different atlases used.  
    * The input volume and tumor segmentation mask in MNI space in the sub-directory named \'registration\'.  
     
## 3. Source code usage

### 3.1 Installation
Use the requirements.txt file to create a virtual environment with the required libraries.
> virtualenv -p python3 venv  
> cd venv  
> source bin/activate  
> pip install -r ../requirements.txt  
> deactivate  

### 3.2 Usage
The command line input parameters are:
* -g [--use_gui]: Must be set to 0 to disable the gui, otherwise 1.
* -i [--input_filename]: Complete path to the MRI volume to process.
* (optional) -s [--input_tumor_segmentation_filename]: Complete path to the corresponding tumor mask, to avoid re-segmentation.
* -o [--output_folder]: Main destination directory. A unique timestamped folder will be created inside for each run.
* -d [--gpu_id]: Number of the GPU to use for the segmentation task. Set the value to -1 to run on CPU.
* -t [--task]: Process to perform, either segmentation or diagnosis (for generating the standardized report).
* -m [--model_segmentation]: Name of the trained model to use (from the list of automatically downloadable models).

To run segmentation directly from command line, without the use of the GUI, run the following:
> source venv/bin/activate  
> python main.py -g 0 -i /path/to/volume/T1.nii.gz -o /path/to/output/ -d 0 -t segmentation -m MRI_Meningioma 
> deactivate

### How to cite
Please, consider citing our paper, if you find the work useful:
```
@misc{https://doi.org/10.48550/arxiv.2204.14199,
title = {Preoperative brain tumor imaging: models and software for segmentation and standardized reporting},
author = {Bouget, D. and Pedersen, A. and Jakola, A. S. and Kavouridis, V. and Emblem, K. E. and Eijgelaar, R. S. and Kommers, I. and Ardon, H. and Barkhof, F. and Bello, L. and Berger, M. S. and Nibali, M. C. and Furtner, J. and Hervey-Jumper, S. and Idema, A. J. S. and Kiesel, B. and Kloet, A. and Mandonnet, E. and Müller, D. M. J. and Robe, P. A. and Rossi, M. and Sciortino, T. and Brink, W. Van den and Wagemakers, M. and Widhalm, G. and Witte, M. G. and Zwinderman, A. H. and Hamer, P. C. De Witt and Solheim, O. and Reinertsen, I.},
doi = {10.48550/ARXIV.2204.14199},
url = {https://arxiv.org/abs/2204.14199},
keywords = {Image and Video Processing (eess.IV), Computer Vision and Pattern Recognition (cs.CV), Machine Learning (cs.LG), FOS: Electrical engineering, electronic engineering, information engineering, FOS: Electrical engineering, electronic engineering, information engineering, FOS: Computer and information sciences, FOS: Computer and information sciences, I.4.6; J.3},
publisher = {arXiv},
year = {2022},
copyright = {Creative Commons Attribution 4.0 International}}
```

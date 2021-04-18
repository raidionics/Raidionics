# NeuroRADS

Simple project for building binary releases of Python code for Ubuntu/MacOSX/Windows using [PyInstaller](https://github.com/pyinstaller/pyinstaller).

## How to use?
Download binary release from the **tags** section. We currently support Ubuntu Linux (v18), MacOSX (>= high-sierra) and Windows (v10).

## How to build:
Using PyInstaller for building Python projects on various operating systems works well. However, [ANTs](https://github.com/ANTsX/ANTs) has limited support for Windows. Currently, the only stable way to use ANTs, is to use [ANTsPy](https://github.com/ANTsX/ANTsPy). Even still, on Windows, one have to install ANTsPy in a different way. Thus, read carefully through this tutorial before starting, to avoid having to start all over.

### Dependencies

1. Need to have installed Python on your machine (Python3.6 for Ubuntu/MacOSX, on Windows install Python3.7), and added to the environmental variables.
2. Also should have [**virtualenv**](https://pypi.org/project/virtualenv/) installed, in order to make virtual environments (pip install virtualenv).
3. CMake need to be installed on the machine, as ANTsPy depends on it for being built/installed through pip. This is the warning you might get otherwise:
```
RuntimeError: CMake must be installed to build the following extensions: ants
```

### Building the binary release

First of all, PyInstaller cannot [cross compile](https://realpython.com/pyinstaller-python/#limitations). Which simply means that an executable has to be built in a Windows operative system. The dependencies have to be met before building, and please use a fresh virtual environment to build, to minimize the size of the release as well as ensuring stability of the produced software.

These are the steps to build the software (for LINUX, it should be quite similar for different OS):

1. Create virtual environment, activate it, and install dependencies:
```
virtualenv -p python3 venv --clear
source venv/bin/activate
pip install -r requirements.txt
```

2. Install ANTs. Recommended way is to install ANTsPy, due to issues with Windows, and also simplifies packaging of software for deployment (note that different OS may have different OS, depending on what is available for the specific OS):
```
Ubuntu and MaxOSX: > pip install antspyx
Windows: > pip install https://github.com/SGotla/ANTsPy/releases/download/0.1.7Win64/antspy-0.1.7-cp37-cp37m-win_amd64.whl
```

2. Download model/config data, create the specified folder structure inside segmentation/ and place it there:
```
mkdir segmentation/resources/models/MRI_Brain/
mv path-to-some-model-data project-dir-path/segmentation/resources/models/MRI_Brain/
```

3. Install pyinstaller, if it is not already installed:
```
pip install pyinstaller==4.2
```

4. Build binary release, from the folder directory (note that Windows should have a Python3.7 virtual environment here):
```
Ubuntu > pyinstaller --noconform --clean --onefile --paths=./venv/lib/python3.6/site-packages/ants main_custom.spec
MacOSX > pyinstaller --noconfirm --clean --onefile --paths=./venv/lib/python3.6/site-packages/ants main_custom.spec
Windows > pyinstaller --noconfirm --clean --onefile --paths=./venv/lib/site-packages/ants main_custom.spec
```

The binary release will be place in dist/.

5. Run the release:
```
Ubuntu and MacOSX > ./dist/NeuroRADS
Windows > ./dist/NeuroRADS.exe
```

## TODOs (most important from top to bottom):

- [x] Use PyInstaller to produce release that encrypts the code and trained models into **one** file
- [x] Achieve multi-OS support for Ubuntu Linux, MacOSX and Windows
- [ ] Finish the GUI for release
- [ ] Re-build and produce binary releases for all relevant operating systems
- [ ] Publish release in open repository

## TIPS

But of course, depending on which OS you are building on, this experience might be less seemless.

On Windows the virtual environment can be activate by:
```
./venv/Scripts/activate.ps1
```

Create virtual environment using specific Python version (example from Win10 machine):
```
virtualenv --python=C:\Users\andrp\AppData\local\Programs\Python\python37\python.exe venv37 --clear
```

I was able to build ANTs on Win10, but I had issues with 32-bit/64-bit. I couldn't make that work. Thus, use ANTsPy instead, and for Windows use [SGotla's fix](https://github.com/SGotla/ANTsPy/releases). Future work should be to adapt what SGotla did to see if one could do the same for the most recent versions of ANTs.




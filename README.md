# NeuroRADS

Simple project for building binary releases of Python code for Ubuntu/MacOS/Windows using [PyInstaller](https://github.com/pyinstaller/pyinstaller).


## How to build:

### Dependencies

1. Need to have installed Python3.6 on your machine, and added to the environmental variables. Essentially Python3==Python3.6.
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
virtualenv -ppython3 venv --clear
source venv/bin/activate
pip install -r requirements.txt
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

4. Build binary release, from the folder directory:
```
pyinstaller --noconfirm --clean --onefile --paths=./venv/lib/python3.6/site-packages/ants main_custom.spec
```

The binary release will be place in dist/.

5. Run the release:
```
./dist/NeuroRADS
```

## TIPS

But of course, depending on which OS you are building on, this experience might be less seemless.

On Windows the virtual environment can be activate by:
```
./venv/Scripts/activate.ps1
```

The extension of the software varies depending on the OS. On Windows run:
```
./dist/NeuroRADS.app
```

and on MacOS:
```
./dist/NeuroRADS.app
```





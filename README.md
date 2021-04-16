# NeuroRADS

Simple project for building binary releases of Python code for Ubuntu/MacOS/Windows using [PyInstaller](https://github.com/pyinstaller/pyinstaller).


### How to use?

1. Create virtual environment, activate it, and install dependencies:
```
virtualenv -p python3 venv --clear
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

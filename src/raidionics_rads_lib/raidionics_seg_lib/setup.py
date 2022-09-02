import sys
from setuptools import find_packages, setup
import platform

with open("README.md", "r", errors='ignore') as f:
    long_description = f.read()

with open('requirements.txt', 'r', encoding='utf-8', errors='ignore') as ff:
    required = ff.read().splitlines()

if platform.system() == 'Windows':
    # required.append('tensorflow@https://github.com/andreped/tensorflow-windows-wheel/raw/master/1.13.1/py37/CPU/sse2/tensorflow-1.13.1-cp37-cp37m-win_amd64.whl')
    required.append('tensorflow==1.13.1')
else:
    required.append('tensorflow==1.13.1')


setup(
    name='raidionicsseg',
    packages=find_packages(
        include=[
            'raidionicsseg',
            'raidionicsseg.Utils',
            'raidionicsseg.PreProcessing',
            'raidionicsseg.Inference',
            'tests',
        ]
    ),
    entry_points={
        'console_scripts': [
            'raidionicsseg = raidionicsseg.__main__:main'
        ]
    },
    install_requires=required,
    python_requires=">=3.6",
    version='0.1.2',
    author='David Bouget (david.bouget@sintef.no)',
    license='BSD 2-Clause',
    description='Raidionics segmentation and classification back-end with TensorFlow',
    long_description=long_description,
    long_description_content_type="text/markdown",
)

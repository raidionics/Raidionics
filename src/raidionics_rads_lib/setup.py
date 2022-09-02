from setuptools import find_packages, setup
import platform

with open("README.md", "r", errors='ignore') as f:
    long_description = f.read()

with open('requirements.txt', 'r', encoding='utf-16', errors='ignore') as ff:
    required = ff.read().splitlines()

if platform.system() == 'Windows':
    required.append('antspy@https://github.com/SGotla/ANTsPy/releases/download/0.1.7Win64/antspy-0.1.7-cp37-cp37m-win_amd64.whl')
    required.append('pandas==1.1.5')
    required.append('scikit-learn==0.24.2')
    required.append('statsmodels==0.12.2')
elif platform.system() == 'Darwin':
    required.append('antspyx@https://github.com/ANTsX/ANTsPy/releases/download/v0.1.8/antspyx-0.1.8-cp37-cp37m-macosx_10_14_x86_64.whl')
    required.append('pandas==1.1.5')
    required.append('scikit-learn==0.24.2')
    required.append('statsmodels==0.12.2')
else:
    required.append('antspyx')

setup(
    name='raidionicsrads',
    packages=find_packages(
        include=[
            'raidionicsrads',
            'raidionicsrads.Utils',
            'raidionicsrads.Processing',
            'raidionicsrads.NeuroDiagnosis',
            'raidionicsrads.MediastinumDiagnosis',
            'raidionicsrads.Atlases',
            'tests',
        ]
    ),
    entry_points={
        'console_scripts': [
            'raidionicsrads = raidionicsrads.__main__:main'
        ]
    },
    install_requires=required,
    include_package_data=True,
    python_requires=">=3.6, <3.8",
    version='0.1.0',
    author='David Bouget (david.bouget@sintef.no)',
    license='BSD 2-Clause',
    description='Raidionics reporting and data system (RADS)',
    long_description=long_description,
    long_description_content_type="text/markdown",
)

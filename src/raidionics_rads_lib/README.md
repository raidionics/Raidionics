# Raidionics backend for computing tumor characteristics and standardized report (RADS)

[![License](https://img.shields.io/badge/License-BSD%202--Clause-orange.svg)](https://opensource.org/licenses/BSD-2-Clause)
[![Build Actions Status](https://github.com/dbouget/raidionics-rads-lib/workflows/Build/badge.svg)](https://github.com/dbouget/raidionics-rads-lib/actions)
[![Paper](https://zenodo.org/badge/DOI/10.3389/fneur.2022.932219.svg)](https://www.frontiersin.org/articles/10.3389/fneur.2022.932219/full)

The code corresponds to the Raidionics backend for generating standardized reports from MRI/CT volumes.  
The module can either be used as a Python library, as CLI, or as Docker container.

# Installation

```
pip install git+https://github.com/dbouget/raidionics-rads-lib.git
```

# Usage
## CLI
```
raidionicsrads CONFIG
```

CONFIG should point to a configuration file (*.ini), specifying all runtime parameters,
according to the pattern from [**blank_main_config.ini**](https://github.com/dbouget/raidionics-rads-lib/blob/master/blank_main_config.ini).

## Python module
```
from raidionicsrads import run_rads
run_rads(config_filename="/path/to/main_config.ini")
```

## Docker
```
docker pull dbouget/raidionics-rads:v1
docker run --entrypoint /bin/bash -v /home/ubuntu:/home/ubuntu -t -i --runtime=nvidia --network=host --ipc=host dbouget/raidionics-rads:v1
```

The `/home/ubuntu` before the column sign has to be changed to match your local machine.

# Models
The trained models are automatically downloaded when running Raidionics or Raidionics-Slicer.

# For developers
A manual installation of CUDA and of the following Python package is necessary to benefit from the GPU.

```
pip install tensorflow-gpu==1.14.0
```

The ANTs library can be manually installed (from source) and be used as a cpp backend rather than Python.
Visit https://github.com/ANTsX/ANTs.

# How to cite
If you are using Raidionics in your research, please use the following citation:
```
@article{10.3389/fneur.2022.932219,
title={Preoperative Brain Tumor Imaging: Models and Software for Segmentation and Standardized Reporting},
author={Bouget, David and Pedersen, André and Jakola, Asgeir S. and Kavouridis, Vasileios and Emblem, Kyrre E. and Eijgelaar, Roelant S. and Kommers, Ivar and Ardon, Hilko and Barkhof, Frederik and Bello, Lorenzo and Berger, Mitchel S. and Conti Nibali, Marco and Furtner, Julia and Hervey-Jumper, Shawn and Idema, Albert J. S. and Kiesel, Barbara and Kloet, Alfred and Mandonnet, Emmanuel and Müller, Domenique M. J. and Robe, Pierre A. and Rossi, Marco and Sciortino, Tommaso and Van den Brink, Wimar A. and Wagemakers, Michiel and Widhalm, Georg and Witte, Marnix G. and Zwinderman, Aeilko H. and De Witt Hamer, Philip C. and Solheim, Ole and Reinertsen, Ingerid},
journal={Frontiers in Neurology},
volume={13},
year={2022},
url={https://www.frontiersin.org/articles/10.3389/fneur.2022.932219},
doi={10.3389/fneur.2022.932219},
issn={1664-2295}}
```

## Note
After git cloning with submodules, should install the submodule to make it know as a Python package.
```
pip install raidionics_seg_lib
```

After a modification to the submodule in its original repo, the current project and virtualenv should be updated:
```
cd raidioncs_seg_lib
git clone origin master
cd ..
pip install raidionics_seg_lib
```

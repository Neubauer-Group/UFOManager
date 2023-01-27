[![DOI](https://zenodo.org/badge/516765685.svg)](https://zenodo.org/badge/latestdoi/516765685)

# About `UFO` models
`UFO` is the abbreviation of **U**niversal **F**eynRules **O**utput. UFO models are used to digitally store detailed information about the Lagrangian of a quantum field theory, such as names, [PDG IDs](https://doi.org/10.1007/BF02683426), and physical properties of elementary particles, relevant parameters (like coupling strengths), and vertices associated with Feynman Diagrams. They are developed as self-sustained Python libraries and can be used by Monte Carlo event generators such as [MadGraph](http://madgraph.phys.ucl.ac.be) to simulate physics processes in a collider experiment. UFO models are widely used in the context of the BSM theories. 

Further details about the content and format of UFO models can be found in the article: [UFO – The Universal FeynRules Output](https://doi.org/10.1016/j.cpc.2012.01.022). Also, you can find examples of different UFO models in this webpage: [https://feynrules.irmp.ucl.ac.be/wiki/ModelDatabaseMainPage](https://feynrules.irmp.ucl.ac.be/wiki/ModelDatabaseMainPage).

# About `FAIR` principles
`FAIR` stands for **F**indable, **A**ccessible, **I**nteroperable, and **R**eusable. FAIR principles were originally proposed in [this paper](https://doi.org/10.1038/sdata.2016.18) as domain-agnostic guidelines on preservation and management of scientific data. These principles have also been interpreted in the context of other digital objects like research software, machine learning (ML) models, notebooks etc. These guidelines focus on persistent preservation of such contents so that they are well-preserved, easily found, and reused, with additional emphasis on improving the ability of machines to automatically search and use digital contents and aims to help users better access and reuse those existing data. For more information of FAIR principles, you can visit [GO FAIR](https://www.go-fair.org/fair-principles).

Domain specific interpretation of FAIR principles in the context of different kinds of digital objetcs are being investigated by multiple groups. For instance, the [FAIR4HEP](https://fair4hep.github.io/) group focuses on identifying the best practices to make data and ML models FAIR in high energy physics. 

# About this repository
Like any other digital content, UFO models have software and platform dependencies, require version controlling, and can benefit from a unified way of preserving and distributing these resources. This FAIR-principle guided repository has been developed as a comprehensive tool to automate the persistent preservation and dispersion of UFO models and their corresponding metadata, creating a reliable and persistent bridgeway between the developers and users of such models. The primary content of this repository is the `UFOManager` package that consists of two python scripts: `UFOUpload.py` for uploading UFO models and `UFODownlaod.py` for downloading UFO modelss. Both scripts can be used as standalone `Python` scripts or the `UFOManager` package can be incorporated into user-developed custom facilitaor script.


# Setup
This package can be setup by simply downloading it from the git repository and installing the necessary dependencies. To download this package:
```bash
$ git clone git@github.com:Neubauer-Group/UFOManager.git
```
Since some of the older UFO models are only available in `Python 2`, we have made `UFOUpload.py` compatible with both versions of `Python`. However, we strongly recommend using the prescribed setup in `requirements_Python2.txt` and `requirements_Python3.txt` while using this package with the desired `Python` version. The desired setup can be obtained by setting up a [conda](https://docs.conda.io/en/latest/miniconda.html) environment. For `Python 2`, run-
```bash
$ conda create --name ufo2 python=2.7
```
and for `Python 3`, run-
```bash
$ conda create --name ufo3 python=3.8
```
After creating the desired environment, run the following command to setup the dependencies-
```
$ conda activate ufo<N>
$ pip install -r requirements_Python<N>.txt
```
Here `<N>` is the `Python` version. This will setup the necessary dependencies for the corresponding environment. 
**Note:** `UFODownload.py` is not supported with `Python 2`, so users willing to search and download models should setup the environment in `Python 3`.

## Before Using the Package
Every time before using the package, one should properly setup the environment and update the `PYTHONPATH` environment variable.
```
$ conda activate ufo<N>
$ cd <path-to-UFOManager>
$ export PYTHONPATH=$PYTHONPATH:$PWD
```

<!---
### Environment Build
It is recommended A Python virtual environment is recommended for executing `Uploadv2.py` or `Uploadv3.py` in command line interface. Necessary Python packages need to be installed. The Python2 support is enabled since many of the existing UFO models have been developed in Python2 and still used as is or with conversion locally performed by Python version conversion tools provided as plug-ins with Monte Carlo Generator Softwares like MadGraph.

**To run the script with Python3** (i.e. to use `Uploadv3.py`), one needs to build a Python3 virtual environment. You can do it with
```bash
$ python3 -m venv Your_virtual_envirenment_name
```
to create a Python3 virtual environment directly in your working environment;then, use
```bash
$ . Your_virtual_envirenment_name/bin/activate
```
to activate your envirenment.
After that, install neccessary packages,
```bash
(Your_virtual_envirenment_name)$ pip install requests PyGithub termcolor
```
**To run the script with Python2** (i.e. to use `Uploadv2.py`), one needs to build a Python2 virtual environment within a Python3 supported system. This needs installing the `virtualenv` package:
```bash
$ python3 -m pip install virtualenv
```
Then, construct the virtual environment and activate the environment in a similar way,
```bash
$ virtualenv --python=python2.7 Your_virtual_envirenment_name
$ . Your_virtual_envirenment_name/bin/activate
```
After that, install necessary packages in the same way,
```
(Your_virtual_envirenment_name)$ python -m pip install requests PyGithub termcolor
```
--->


# Using `UFOUpload`: Model Validation, Metadata Generation, and Preservation
Developers can use `UFOUpload.py` to validate the structure and content as well as publish their models with persistent **D**igital **O**bject **I**dentifiers (DOIs). When provided with the model files and some basic model inforamtion, the Upload function can examine the validation of model files,  generate metadata in the formal of a `json` file for the model, publish the model to [Zenodo](https://zenodo.org/), and make the metadata available via another repository [UFOMetadata](https://github.com/Neubauer-Group/UFOMetadata) for preservation.

## File Preparation
To use the Upload function you need to create a directory `Your_Model_Folder` that will contain the UFO model as a compressed folder with extensions (`.tar, .tar.gz, .tgz, .zip`) or as a directory itself. An additional json file called `metadata.json` is needed to provide basic information about the model.

For compressed folders, tarball and zip are accepted with UFO model python scripts inside the folder.
```
--Your_Model_Folder
 --metadata.json
 --Your_Model.zip/.tgz/.tar.gz
   --_init_.py
   --object_library.py
    ...
```
or
```
--Your_Model_Folder
 --metadata.json
 --Your_Model.zip/.tgz/.tar.gz
   --Your_Model Folder
    --_init_.py
    --object_library.py
    ...
```
For metadata.json, some basic information is required. You can see the requirements in [this example](https://github.com/Neubauer-Group/UFOManager/blob/main/metadata.json). For author information in `metadata.json`, affiliation and contact are optional, but at least one contact is needed. It also requires a reference to an associated publication (either an [arxiv](https:://arxiv.org) Id or a `DOI`) that contains the necessary physics details and validation.

Finally, developers need to prepare a `.txt` file containing **full** paths to their models, each path lies in a single line, for example, in the `.txt` file
```
path-to-model1
path-to-model2
...
```

## Usage
From the command line, one can run-
```bash
$  python -m UFOManager.UFOUpload <command>
```
where `<command>` represents one of the 5 choices-
```
'Validation check' 
'Generate metadata' 
'Upload model' 
'Update new version' 
'Upload metadata to GitHub'
``` 

The script runs in an interactive manner, requirung the user to provide the path to the `.txt` file containing paths to models:
```bash
$ Please enter the path to a text file with the list of all UFO models: <path-to-txt-file>
```
The same functionality can be achieved from an independent facilitator script and including the following lines:
```
from UFOManager import UFOUpload
UFOUpload.UFOUpload(<command>, <path-to-txt-file>)
```


### Validation check
At this point the script will first check your file preparation, like whether your folder contains only two files required, and whether your `metadata.json` contains necessary information. After that,your model's validation will be checked. Your model will be checked whether it can be imported as a complete python package, since event generators require model input as a complete python package. It will read through your necessary model dependent files, check the completeness of those files and generate basic model-related information, such as particles defined in your model, number of vertices defined in your model.

### Generate metadata
This request will go through the validation check of your model first and generate necessary model-related information. Then, some information is required from developers:
```
$ Please name your model: <model-name>
$ Please enter your model version: <model-version>
```
Note that the model will be given a default DOI of `0` in the enriched metadata unless the `Model doi` field is already present in the initial metadata. If you are using this functionality for a model for which a DOI already exists, you should provide that information in the initial metadata file.

The new enriched metadata `json` file will be created inside `Your_Model_Folder`. 
```
--Your_Model_Folder
 --metadata.json
 --Your_Model.zip/.tgz/.tar.gz
 --Your_Model.json
```
You can see an [example enriched metadata file](https://github.com/Neubauer-Group/UFOMetadata/blob/main/metadata.json) stored in the [UFOMetadata](https://github.com/Neubauer-Group/UFOMetadata) repository.

### Upload model    
At the beginning, your Zenodo personal access token and your GitHub personal access token will be required.
```
$ Please enter your Zenodo access token: <Zenodo_Access_Token>
$ Please enter you Github access token: <Github_Access_Token> 
```
For your Zenodo personal access token, `deposit:actions` and `desposit:write` should be allowed.

The script will go through the validation check of your model, generate the enriched metadata, and then use the [`Zenodo API`](https://developers.zenodo.org/) to publish your model to Zenodo and get a DOI for your model. 

<!---
During the upload, your need to name your model/give title of your upload. Other neccessary information, creators and description, will be directly from your metadata.json.
```bash
$ Please name your model: <model name
```
```
$ Please enter your model version: Your model version
```
--->

If everything goes well, you can see a new draft in your Zenodo account. A reserved Zenodo DOI will be created. The new metadata file will be created in `Your_Model_Folder`. After that, the [UFO Models Preservation repository](https://github.com/Neubauer-Group/UFOMetadata) used for metadata preservation will be forked in your Github account, the new metadata will be added. 

**Note**: If you forked [UFOMetadata](https://github.com/Neubauer-Group/UFOMetadata) before, make sure that your forked branch is up-to-date with orginal one.

Before finally publishing your model and uploading new enriched metadata to GitHub, you can make some changes to your Zenodo draft. And you can choose whether to continue
```
$ Do you want to publish your model and send your new enriched metadata file to GitHub repository UFOMetadata? Yes or No: Yes, or No
```
If you choose `Yes`, your model will be published to Zenodo, a pull request of your new enriched metadata will be created. A CI-enabled autocheck will run when pull request is made. This check may last for 5 minutes to make sure that model's DOI page is avaliable. If any problem happens, please contact Zijun Wang (zijun4@illinois.edu) or Avik Roy (avroy@illinois.edu).

If you choose `No`, you can publish your model by yourself. You can visit the associated Zenodo draft, edit it and publish. Afterwards, you can create the pull request to add your enriched metadata to [UFOMetadata](https://github.com/Neubauer-Group/UFOMetadata) by yourself, or send your enriched metadata file to Zijun Wang (zijun4@illinois.edu) or Avik Roy (avroy@illinois.edu).

### Update new version
To allow this functionality, your initial `metadata.json` needs to add a new key-value pair
```
"Existing Model Doi": "Zenodo-issued concept-DOI for your model"
```
The concept-DOI is a unique identifier issued by Zenodo to access all available versions of the model and always resolves to the latest version. 

Afterwards, Upload script will work in a way similar to what it would do with 'Upload model'. 

### Upload metadata to GitHub
If you previously uploaded your model to Zenodo and want to create an enriched metadata for your model, you need to add a key-value pair
```
"Model Doi": "Zenodo DOI of your model"
```
in metadata.json. Your GitHub personal access token will be required for this functionality. The script will go through the validation check of your model, the enriched metadata file will be created in `Your_Model_Folder`. After that, the [UFO Models Preservation repository](https://github.com/Neubauer-Group/UFOMetadata) used for metadata preservation will be forked in your Github account, the new metadata will be added, and pull request will be made.


### Dealing with errors
You will be given feedback when most errors happen. **If an error happens when you are uploading your model to Zenodo or uploading metadata to GitHub, it is recommended to delete the draft in Zenodo and the newly created enriched metadata in your forked branch before re-running the script**

# Using `UFODownload`: Search and Download UFO models
Users can use `UFODownload.py` to search for UFO models using the metadata preserved in [UFOMetadata repository](https://github.com/Neubauer-Group/UFOMetadata) and download them from Zenodo. It will require the user to run the commands with `Python 3`.

<!---
### Environment Build
The `Download.py` is developed only for python 3. A Python virtual environment is recommended for executing this script with command line interface. 

In the Python3 supported system, you can use
```bash
$ python3 -m venv Your_virtual_envirenment_name
```
to create a Python3 virtual environment directly in your working environment;then, use
```bash
$ . Your_virtual_envirenment_name/bin/activate
```
to activate your envirenment.

The `Download.py` utilizes [zenodo_get](https://github.com/dvolgyes/zenodo_get) from David Völgyes, detailed citation information is included within the python script. To install necessary prerequisites, run
```bash
pip install requests PyGithub zenodo_get termcolor tabulate
```
--->

## Usage
From the command line, one can run-
```bash
$  python -m UFOManager.UFODownload <command>
```
where `<command>` represents one of the 3 choices-
```
'Search for model' 
'Search and Download'
'Download model'
``` 
The same functionality can be achieved from an independent facilitator script and including the following lines:
```
from UFOManager import UFODownload
UFODownload.UFODownload(<command>)
```

### Search for model
Currently, the Download.py supports search on four types of information through UFO model metadata files: corresponding paper id of the model, Model's Zenodo DOI, pdg codes or names of particles in the model. You need to interactively make a choice-
```bash
$ Please choose your keyword type: Paper_id, Model Doi, pdg code, or name
```
Then, you can can start your search. For `Paper_id` and `Model Doi`, one input value is allowed. But you can input multiple particles' names/pdg codes, separated them with ','.
```bash
$ Please enter your needed pdg code: <code1,code2,...>
```
or
```bash
$ Please enter your needed particle name: <name1,name2,...>
```
**Note**: Your input particles should not be all elementary particles!!!

Then, you will get a feedback table containing metadata file name, model name, paper_id, and model DOI of UFO models fit your search. 

Also, you can restart the search by responding `Yes` to the following question:
```bash
$ Do you still want to search for models? Please type in Yes or No.
```

### Search and Download 
It will start with the usual steps of searching for models. Once your ssearch is complete, it will give you a list of metadata file names (with `.json` extensions). You can download UFO models you need, by typing in their corresponding metadata file full names and separated them with ','.  
```
$ You can choose the metadata you want to download: <meta1.json,meta2.json,...>
```
After that, you will be asked to create a folder, and all UFO models you need will be downloaded to that folder.
```bash
$ Please name your download folder: <Your_Download_Folder>
```
And the folder is under your current working path.
```
--Your current working path
 --Download.py
 --Your_Download_Folder
```

### Download model

Then, you can download UFO models you need, by typing in their corresponding metadata file full name (.json is required) and separated them with ','. You can find the full names from your search feedback. 

# References

This work was done as a part of the IRIS-HEP Fellowship project for Zijun Wang under the mentorship of Avik Roy, Mark S Neubauer, and Matthew Feickert. The presentation is available at [this link](https://indico.cern.ch/event/1195270/contributions/5043771/attachments/2508513/4311003/Zijun_Wang_IRIS-HEP_Presentation.pdf).

To cite this work, add to your bibliography-
```
Neubauer, M. S., Roy, A., & Wang, Z. (2022). Making Digital Objects FAIR in High Energy Physics: An Implementation for Universal FeynRules Output (UFO) Models. arXiv preprint arXiv:2209.09752.
```
or use the following bibtex entry-
```
@article{neubauer2022making,
  title={Making Digital Objects FAIR in High Energy Physics: An Implementation for Universal FeynRules Output (UFO) Models},
  author={Neubauer, Mark S and Roy, Avik and Wang, Zijun},
  journal={arXiv preprint arXiv:2209.09752},
  year={2022}
}
```

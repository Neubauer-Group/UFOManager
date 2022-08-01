
# About UFO models
UFO is the abbreviation of Universal FeynRule Output. UFO models are used to store detailed information of Beyond the Standard Model theory, such as information of particles, parameters, and vertices associated with Feynman Diagram and Feynman rules, and then can be used by Monte Carlo event generators such as [MadGraph](http://madgraph.phys.ucl.ac.be) to simulate collider physics in the context of the BSM theories. 

Unlike other models, which store BSM physics information in a collection of text files, requiring further parsing and interpretation before they can be used by every different event generator, UFO models store different information of the particle model, in a generator-independent way, into different PYTHON files. Such a storage method allows event generators working directly with UFO models without any modification or further interfacing. 

For detailed information and format of UFO models, you can read through the article [UFO – The Universal FeynRules Output](https://www.sciencedirect.com/science/article/abs/pii/S0010465512000379#!). Also, you can see exisiting UFO models in [wiki:NLOModels](https://feynrules.irmp.ucl.ac.be/wiki/NLOModels).

# About FAIR principles
FAIR stands for findable, accessible, interoperable, and reusable. FAIR principles provide guidelines to search, obtain, and use digital objects/data from internet database. The guidelines focus on improving the ability of machines to automatically search and use data and aims to help users better access and reuse those existing data.

For detailed information of FAIR principles, you can visit [GO FAIR](https://www.go-fair.org/fair-principles).

# About this repository
Like any other digital content, UFO models have software and platform dependencies, require version controlling, and can benefit from a unified way of preserving and distributing these resources. Therefore, we hope to develop FAIR criteria for preservation of UFO models. This repository works as a bridge between UFO model developers and users. In this repository, two python scripts, Upload.py and Downlaod.py, are developed for uploading and downloading UFO models.

# Upload
Developers can use Upload.py to publish their models. Provided by model files and necessary model inforamtion, the Upload.py will examine the validation of model files, publish the model to Zenodo, generate a metadata json file for the model, and push the metadata file to another repository [UFOMetadata](https://github.com/ThanosWang/UFOMetadata) for preservation.
## Preparation
You need to do a series of preparation work before being able to use the Upload.py
### Environment Build
The Upload.py is suitable in both Python2/3 environment. A Python virtual environment is recommended for executing the Upload.py in command line interface. And necessary Python packages are needed.

With Python3 as your python path, you can use
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
(Your_virtual_envirenment_name)$ pip install requests, PyGithub
```
With python 2.7 as you python path, you need to install the virtualenv first,
```bash
$ python -m pip install virtualenv
```
or with python 3 as your python path, use
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
(Your_virtual_envirenment_name)$ python -m pip install requests, PyGithub
```
### File Preparation
To use the Upload.py, you need to create Your_Model_Folder with a compressed folder storaging all your model files and a json file called metadata.json.

For compressed folder, tarball and zip are accepted with UFO model python scripts directly inside the folder.
```
--Your_Model_Folder
 --metadata.json
 --Your_Model.zip/.tgz/.tar.gz
   --_init_.py
   --object_library.py
    ...
```
For metadata.json, basic information is required. You can see the requirements in [example](https://github.com/ThanosWang/UFOModel_Upload_Download/blob/main/metadata.json)
And you need to make sure that Your_Model_Folder lies in subpath of your current working folder.
```
--Your current working directory
 --Your_virtual_envirenment_name
 --FolderA
  --FolderB
   ...
    --Your_Model_Folder
```
## Usage
After everything being set up, you can download Upload.py, put it in your current working directory, and start the python script through the command line
```bash
$ python2 or python3 Upload.py
```
### Validation Check
First, path of Your_Model_Folder, start from your current working directory, will be required
```bash
$ Please enter the path of your folder, starting from your current working directory: FolderA/FolderB/.../Your_Model_Folder
```
Then, your model's validation will be checked. Your model will be checked whether it can be imported as a complete python package, since event generators require model input as a complete python package. After that, the Upload.py will read through your necessary model dependent files, check the completeness of those files and generate basic model-related information, such as particles defined in your model, number of vertices defined in your model. Those information will be included in a new metadata file in later steps.
### Zenodo Upload
After the validation check, the Upload.py will use [Zenodo API](https://developers.zenodo.org/) to publish your model to Zenodo and get a DOI for your model. 

Your Zenodo personal access token will be required for uploading your model to Zenodo. The input uses getpass() to ensure the safety.
```bash
$ Please enter your Zenodo access token: Your Zenodo Personal Access Token
```
During the upload, your need to name your model/give title of your upload. Other neccessary information,creators and description, will be directly from your metadata.json.
```bash
$ Please name your model: Your model name
```
If everything goes well, you can see a new draft in your Zenodo account.

Then, you can choose whether to publish the draft. Entering Yes to publish it directly, or if you want to add more metadata information, entering No to skip the publish step.
```
Do you want to publish your model? Yes or No? Yes, or No
```
Note: You need to publish your model before going to next step. Since before being published, your reserved Zenodo DOI will not be registered by the DOI system. This will affect the upload of your metadata file to Github repository.
### Generate new metadata
#### Version issue
After publishing your model, your model version will be required.
```bash
Please enter your model version: Your model version
```
In Zenodo, create a new version of file in current upload will generate a new DOI for the file. Therefore, for new version of your existing model, you can just re-run the Upload.py to create a new Zenodo upload and get a new Zenodo DOI. Just the model version and your model compressed folder name need to be different from your existing model.

Then, a new metadata file will be created in Your_Model_Folder.  
```
--Your_Model_Folder
 --metadata.json
 --Your_Model_versionX.zip/.tgz/.tar.gz
 --Your_Model_versionX.json
```
You can see an example complete [metadata file](https://github.com/ThanosWang/UFOMetadata/blob/main/metadata.json) in the [UFO Models Preservation repository](https://github.com/ThanosWang/UFOMetadata).
### Github Upload
Before start this step, you can first check your new metadata file. If you want to make some changes, you can enter No to exit, create a pull request to the [UFO Models Preservation repository](https://github.com/ThanosWang/UFOMetadata) by yourself later.

Otherwise, a Github person access token is required, and the getpass() is used here for safety.
```
$ Please enter you Github access token: Your Github personal access token or No
```
After that, the [UFO Models Preservation repository](https://github.com/ThanosWang/UFOMetadata) used for metadata preservation will be forked in your Github account, the new metadata will be added, and pull request will be made.

A auto check will run when pull request is made. This check may last for 3 minutes to make sure that model's DOI page is avaliable. If any problem happens, please contact thanoswang@163.com.

# Download
Users can use Download.py to search for UFO models through their metadata preserved in [UFO Models Preservation repository](https://github.com/ThanosWang/UFOMetadata) and download them from Zenodo.
## Environment Build
The Download.py is developed only for python 3. A Python virtual environment is recommended for executing the Upload.py in command line interface. And necessary Python packages are needed.

With Python3 as your python path, you can use
```bash
$ python3 -m venv Your_virtual_envirenment_name
```
to create a Python3 virtual environment directly in your working environment;then, use
```bash
$ . Your_virtual_envirenment_name/bin/activate
```
to activate your envirenment.

The Download.py utilizes [zenodo_get](https://github.com/dvolgyes/zenodo_get) from David Völgyes, detailed citation information is included in the python script.
```bash
pip install requests, PyGithub, zenodo_get
```
## Usage
To use Download.py, just download it and put it anywhere you want and execute it.
```bash
$ python3 Download.py
```
Then, your Github personal access token will be require to access [UFO Models Preservation repository](https://github.com/ThanosWang/UFOModel_Metadata_Preservation). The input uses getpass() to ensure the safety.
### UFO Model Search
After that, you will be able to search for UFO models you need. Currently, the Download.py supports search on four types of information through UFO model metadata files: corresponding paper id of the model, Model's Zenodo DOI, pdg codes or names of particles in the model.
```bash
$ Please choose your keyword type: Paper_id, Model Doi, pdg code, or name
```
Then, you can can start your search. For Paper_id and Model Doi, one input value is allowed. But you can input multiple particles' names/pdg codes, separated them with ','.
```bash
$ Please enter your needed pdg code: code1, code2, ...
$ Please enter your needed particle name: name1, name2, ...
```
Then, you will get the feedback about which metadata files contains information you input. Also, you can restart the search.
```bash
$ Do you still want to search for models? Please type in Yes or No. Yes or No
```
### UFO Model Download
After you finishing all your search, you can download UFO models you need, by typing in their corresponding metadata file full name (.json is required) and separated them with ','. The full names will be shown with your search feedback. Or you can type No to exit.
```
$ You can choose the metadata you want to download, or type No to exsit: meta1.json, meta2.json, ...
```
Then, you will be asked to create a folder, and all UFO models you need will be downloaded to that folder.
```bash
$ Please name your download folder: Your_Download_Folder
```
And the folder is under your current working path.
```
--Your current working path
 --Download.py
 --Your_Download_Folder
```

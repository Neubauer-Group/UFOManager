
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
Developers can use Upload.py to publish their models. Provided by model files and necessary model inforamtion, the Upload.py can examine the validation of model files,  generate a metadata json file for the model, publish the model to Zenodo, and push the metadata file to another repository [UFOMetadata](https://github.com/ThanosWang/UFOMetadata) for preservation.

## Preparation
You need to do a series of preparation work before being able to use the Upload.py

### Environment Build
The Upload.py is suitable in both Python2/3 environment. A Python virtual environment is recommended for executing the Upload.py in command line interface. And necessary Python packages are needed.

In the Python3 supported system, you can use
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
To build a Python2 virtual environment with Python3 supported system
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
### File Preparation
To use the Upload.py, you need to create Your_Model_Folder with a compressed folder storaging all your model files and a json file called metadata.json.

For compressed folder, tarball and zip are accepted with UFO model python scripts inside the folder.
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
For metadata.json, basic information is required. You can see the requirements in [example](https://github.com/ThanosWang/UFOModel_Upload_Download/blob/main/metadata.json)

Note: For arthuor information in metadata.json, affiliation and contact are optional, but at least one contact is needed.

## Usage
After everything being set up, you can download Upload.py, put it in your current working directory and execute it. The Upload.py provides developers with 5 choices:
'Validation Check', 'Generate metadata', 'Upload model', 'Update new version', and 'Upload metadata to GitHub'. 

The Upload.py can deal with multiple models in single execution. Developers need to prepare a .txt file containing paths to their models, each path lies in a single line, for example, in the .txt file
```
path-to-model1
path-to-model2
...
```

Then, in each choices, path to the .txt file containing paths to models will be required
```bash
$ Please enter the path to a text file with the list of all UFO models: Path to .txt
```

### Validation Check
To check the validation of your model, use
```
$ python2/3 Upload.py 'Validation Check'
```
in command line.

Then, the Upload.py will first check your file preparation, like whether your folder contains only two files required, and whether your metadata.json contains necessary information. After that,your model's validation will be checked. Your model will be checked whether it can be imported as a complete python package, since event generators require model input as a complete python package. After that, the Upload.py will read through your necessary model dependent files, check the completeness of those files and generate basic model-related information, such as particles defined in your model, number of vertices defined in your model.

### Generate Metadata
To generate new metadata of your model, use
```
$ python2/3 Upload.py 'Generate metadata'
```
in command line.

Then, the Upload.py will go through the validation check of your model and output necessary model-related information. Then, some information is required from developers:
```
$ Please name your model: Your model name
$ Please enter your model version: Your model version
$ Please enter your Model Doi, enter 0 if not have one: Your Model Doi
```
After that, a new enriched metadata json file will be created in Your_Model_Folder. 
```
--Your_Model_Folder
 --metadata.json
 --Your_Model.zip/.tgz/.tar.gz
 --Your_Model.json
```
You can see an [example enriched metadata file](https://github.com/ThanosWang/UFOMetadata/blob/main/metadata.json) stored in [UFOMetadata](https://github.com/ThanosWang/UFOMetadata).

### Upload model    
To publish the model to Zenodo and push the metadata file to another repository [UFOMetadata](https://github.com/ThanosWang/UFOMetadata) for preservation, use
```
$ python2/3 Upload.py 'Upload model'
```
At the beginning, your Zenodo personal access token and your GitHub personal access token will be required. The input uses getpass() to ensure the safety.
```
$ Please enter your Zenodo access token: Your Zenodo personal access token
$ Please enter you Github access token: Your Github personal access token 
```
For your Zenodo personla access token, deposit:actions and desposit:write should be allowed.

Then, the Upload.py will go through the validation check of your model, output necessary model-related information.

After the validation check, the Upload.py will use [Zenodo API](https://developers.zenodo.org/) to publish your model to Zenodo and get a DOI for your model. 

During the upload, your need to name your model/give title of your upload. Other neccessary information,creators and description, will be directly from your metadata.json.
```bash
$ Please name your model: Your model name
```
```
$ Please enter your model version: Your model version
```
If everything goes well, you can see a new draft in your Zenodo account. A reserved Zenodo DOI will be created.

Then, a new metadata file will be created in Your_Model_Folder.  
```
--Your_Model_Folder
 --metadata.json
 --Your_Model_versionX.zip/.tgz/.tar.gz
 --Your_Model_versionX.json
```
You can see an [example enriched metadata file](https://github.com/ThanosWang/UFOMetadata/blob/main/metadata.json) stored in [UFOMetadata](https://github.com/ThanosWang/UFOMetadata).

After that, the [UFO Models Preservation repository](https://github.com/ThanosWang/UFOMetadata) used for metadata preservation will be forked in your Github account, the new metadata will be added.

Before finally publish your model and upload new enriched metadata to GitHub, you can make some changes to your Zenodo draft. 

Note: If you folked [UFOMetadata](https://github.com/ThanosWang/UFOMetadata) before, make sure that your forked branch is up-to-date with orginal one.

And you can choose whether to continue
```
$ Do you want to publish your model and send your new enriched metadata file to GitHub repository UFOMetadata? Yes or No: Yes, or No
```
If you choose Yes, your model will be published to Zenodo, a pull request of your new enriched metadata will be created. A auto check will run when pull request is made. This check may last for 5 minutes to make sure that model's DOI page is avaliable. If any problem happens, please contact thanoswang@163.com.

If you choose No, You can publish your model by yourself and create pull request by yourself. or send your enriched metadata file to thanoswang@163.com.

### Update new version
If you previously uploaded your model to Zenodo and want to update a new version of your model, use
```
$ python2/3 Upload.py 'Update new version'
```
And you need to add a new key-value pair
```
"Existing Model Doi": "Zenodo DOI from your model's latest version"
```
in metadata.json.

Then, the Upload.py will work in a similar way with 'Upload model'.

At the beginning, your Zenodo personal access token and your GitHub personal access token will be required. The input uses getpass() to ensure the safety.
```
$ Please enter your Zenodo access token: Your Zenodo personal access token
$ Please enter you Github access token: Your Github personal access token 
```
For your Zenodo personla access token, deposit:actions and desposit:write should be allowed.

Then, the Upload.py will go through the validation check of your model, output necessary model-related information.

After the validation check, the Upload.py will use [Zenodo API](https://developers.zenodo.org/) to publish your model to Zenodo and get a DOI for your model. 

During the upload, your need to name your model/give title of your upload. Other neccessary information,creators and description, will be directly from your metadata.json.
```bash
$ Please name your model: Your model name
```
```
$ Please enter your model version: Your model version
```
If everything goes well, you can see a new draft in your Zenodo account. A reserved Zenodo DOI will be created.

Then, a new metadata file will be created in Your_Model_Folder.  
```
--Your_Model_Folder
 --metadata.json
 --Your_Model_versionX.zip/.tgz/.tar.gz
 --Your_Model_versionX.json
```
You can see an [example enriched metadata file](https://github.com/ThanosWang/UFOMetadata/blob/main/metadata.json) stored in [UFOMetadata](https://github.com/ThanosWang/UFOMetadata).

After that, the [UFO Models Preservation repository](https://github.com/ThanosWang/UFOMetadata) used for metadata preservation will be forked in your Github account, the new metadata will be added.

Before finally publish your model and upload new enriched metadata to GitHub, you can make some changes to your Zenodo draft. 

Note: If you folked [UFOMetadata](https://github.com/ThanosWang/UFOMetadata) before, make sure that your forked branch is up-to-date with orginal one.

And you can choose whether to continue
```
$ Do you want to publish your model and send your new enriched metadata file to GitHub repository UFOMetadata? Yes or No: Yes, or No
```
If you choose Yes, your model will be published to Zenodo, a pull request of your new enriched metadata will be created. A auto check will run when pull request is made. This check may last for 5 minutes to make sure that model's DOI page is avaliable. If any problem happens, please contact thanoswang@163.com.

If you choose No, You can publish your model by yourself and create pull request by yourself. or send your enriched metadata file to thanoswang@163.com.

### Upload metadata to GitHub
If you previously uploaded your model to Zenodo and want to create an enriched metadata for your model and upload metadata to GitHub, use 
```
$ python2/3 Upload.py 'Upload metadata to GitHub'
```
And you need to add a key-value pair
```
"Model Doi": "Zenodo DOI of your model"
```
in metadata.json.

Then, your GitHub personal access token will be required. The input uses getpass() to ensure the safety.
```
$ Please enter you Github access token: Your Github personal access token 
```
Then, the Upload.py will go through the validation check of your model, output necessary model-related information.

After that, the Upload.py will generate a new enriched metadata file, and following information will be asked
```bash
$ Please name your model: Your model name
```

```
$ Please enter your model version: Your model version
```

Then, a new metadata file will be created in Your_Model_Folder.  
```
--Your_Model_Folder
 --metadata.json
 --Your_Model_versionX.zip/.tgz/.tar.gz
 --Your_Model_versionX.json
```
You can see an [example enriched metadata file](https://github.com/ThanosWang/UFOMetadata/blob/main/metadata.json) stored in [UFOMetadata](https://github.com/ThanosWang/UFOMetadata).

After that, the [UFO Models Preservation repository](https://github.com/ThanosWang/UFOMetadata) used for metadata preservation will be forked in your Github account, the new metadata will be added, and pull request will be made.

# Download
Users can use Download.py to search for UFO models through their metadata preserved in [UFO Models Preservation repository](https://github.com/ThanosWang/UFOMetadata) and download them from Zenodo.
## Environment Build
The Download.py is developed only for python 3. A Python virtual environment is recommended for executing the Upload.py in command line interface. And necessary Python packages are needed.

In the Python3 supported system, you can use
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
To use Download.py, just download it and put it anywhere you want and execute it. The Download.py allows 3 choices for users: simply search for models, simply download models, or do both. In each step, your github personal access token is needed, and getpass() is used as input to ensure safety.
### UFO Model Search
To simply search for UFO models, use
```
$ python Download.py 'Search for model'
```
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
To simply download UFO models, use
```
$ python Download.py 'Download model'
```
Then, you can download UFO models you need, by typing in their corresponding metadata file full name (.json is required) and separated them with ','. The full names will be shown with your search feedback. 
```
$ You can choose the metadata you want to download: meta1.json, meta2.json, ...
```
After that, you will be asked to create a folder, and all UFO models you need will be downloaded to that folder.
```bash
$ Please name your download folder: Your_Download_Folder
```
And the folder is under your current working path.
```
--Your current working path
 --Download.py
 --Your_Download_Folder
```
### Search and Download 
To both search for and download UFO models, just use
```
$ python Download.py 'Search and Download'
```
And follow steps in UFO Model Search and UFO Model Download. 

# UFOManager

This repository contains two python scripts for uploading/downloading UFO models. 

# Upload
The Upload.py can be executed in both Python2/3. You can use Upload.py to check validation of your UFO model, upload your UFO model to Zenodo, and get a metadata json file of your UFO model.
## Preparation
In python3, use
```bash
$ pip install requests, PyGithub
```
In python2, use
```
$ python -m pip install requests, PyGithub
```
## Usage
To use the Upload part, you need to create Your_Model_Folder with a compressed folder storaging all your model files and a json file called metadata.json.

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

After everything being set up, you can start the python script in the terminal
```bash
$ python2 or python3 Upload.py
```
Then, path of Your_Model_Folder, start from your current working directory, will be required
```
--Your current working directory
 --A
  --B
   ...
    --Your_Model_Folder
```

```bash
$ Please enter the path of your folder, starting from your current working directory:: A/B/.../Your_Model_Folder
```
Then, your model will be checked whether it can be imported as a complete python package. Your model independent files will also be checked.

After that, your Zenodo personal access token will be required for uploading your model to Zenodo. The input uses getpass() to ensure the safety.
```bash
$ Please enter your Zenodo access token: Your Zenodo Personal Access Token
```
During the upload, your need to name your model/give title of your upload. Other neccessary information will be directly from your metadata.json.
```bash
$ Please name your model: Your model name or title
```
If everything goes well, you can see a new upload draft in your Zenodo account.

Then, you can choose whether to publish the draft. Entering Yes to publish it directly, or if you want to add more information, entering No to skip the publish step.
```
Do you want to publish your model? Yes or No? Yes, or No
```
After that, a new metadata json file for your model will be created. To ensure the version control, your model version will be required.
```bash
Please enter your model version: Your model version
```
Then, you can check the new metadata json file in Your_Model_Folder
```
--Your_Model_Folder
 --metadata.json
 --Your_Model.zip/.tgz/.tar.gz
 --Your_Model.json
```
Before upload your new metadata to Github, you can first check the new metadata.
Then, a Github person access token is required, the getpass() is also used here for safety. Or You can enter No to exit, upload by yourself later.
```bash
$ Please enter you Github access token: Your Github personal access token or No
```
After that, the [UFO Models Preservation repository](https://github.com/ThanosWang/UFOModel_Metadata_Preservation) used for metadata preservation will be forked in your Github account, the new metadata will be added, and pull request will be made.

# Download
The Download.py is developed only for python 3.You can use Download.py to search for UFO models and download them from Zenodo.
## Preparation
The Download.py utilizes [zenodo_get](https://github.com/dvolgyes/zenodo_get) from David Völgyes, detailed citation information is included in the python script.
```bash
pip install requests, PyGithub, zenodo_get
```
## Usage
To use Download.py, just put it anywhere you want and execute it.
```bash
$ python3 Download.py
```
Then, your Github personal access token will be require to access [UFO Models Preservation repository](https://github.com/ThanosWang/UFOModel_Metadata_Preservation). The input uses getpass() to ensure the safety.

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
--Path
 --Download.py
 --Your_Download_Folder
```

# UFOModel_Upload_Download

This repository contains two python scripts for uploading/downloading UFO models. 

# Upload
You can use Upload.py to check validation of your UFO model, upload your UFO model to Zenodo, and get a metadata json file of your UFO model.
## Preparation
```bash
$ pip install requests, PyGithub
```
## Usage
The Upload.py can be executed in both Python2/3. To use Upload.py, you need to put it in the same path with Your_Model_Folder.
```
--Some_path
 --Upload.py
 --Your_Model_Folder
```
And inside Your_Model_Folder, a compressed folder and a json file called metadata.json are required.

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
You can start the python script in the terminal
```bash
$ python2 or python3 Upload.py
```
And your folder name will be required
```bash
$ Please enter your whole folder contain both your compressed model file and metadata.json: Your_Model_Folder
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
If everything goes well, you can see a new upload published in your Zenodo account.

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
Then, a Github person access token is required, the getpass() is also used here for safety. Or You can enter 'No' to exit, upload by yourself later.
```bash
$ Please enter you Github access token: Your Github personal access token or No
```
After that, the [UFO Models Preservation repository](https://github.com/ThanosWang/UFOModel_Metadata_Preservation) used for metadata preservation will be forked in your Github account, the new metadata will be added, and pull request will be made.

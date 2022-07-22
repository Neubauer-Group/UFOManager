# UFOModel_Upload_Download

This repository contains two python scripts for uploading/downloading UFO models. 

# Upload
You can use Upload.py to check validation of your UFO model, upload your UFO model to Zenodo, and get a metadata json file of your UFO model.
## Preparation
```bash
$ pip install requests, PyGithub
```
## Usage
To use Upload.py, you need to put it in the same path with Your_Model_Folder.
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

from github import Github
import os
import requests
import sys
import shutil
import json
import zenodo_get
from getpass import getpass

# This python script utilizes zenodo_get package from David Völgyes 
# David Völgyes. (2020, February 20). Zenodo_get: a downloader for Zenodo records (Version 1.3.4).
# Zenodo. https://doi.org/10.5281/zenodo.1261812

# Bibtex format:
'''@misc{david_volgyes_2020_10.5281/zenodo.1261812,
  author  = {David Völgyes},
  title   = {Zenodo_get: a downloader for Zenodo records.},
  month   = {2},
  year    = {2020},
  doi     = {10.5281/zenodo.1261812},
  url     = {https://doi.org/10.5281/zenodo.1261812}
}'''




# Connect to Github Repository
Github_Access_Token = getpass('Please enter you Github access token:')

g = Github(Github_Access_Token)

repo = g.get_repo("ThanosWang/UFOModel_Metadata_Preservation")

Allmetadata = repo.get_contents('Metadata')

api_path = os.getcwd()

# A Global Variable
Flag = 0

def preparation():
    # Create a temporary folder for metadata
    try:
        os.mkdir('MetadatafilesTemporaryFolder')
    except FileExistsError:
        os.chdir('MetadatafilesTemporaryFolder')
        return

    os.chdir('MetadatafilesTemporaryFolder')

    # Download all metadata files from GitHub Repository
    for i in Allmetadata:
        name = i.name
        url = 'https://raw.githubusercontent.com/ThanosWang/UFOModel_Metadata_Preservation/main/Metadata/'
        url += name
        metadata = requests.get(url)
        open(name,'wb').write(metadata.content)

    # Make sure this function won't execute again
    global Flag
    Flag = 1

   
# Start the Interface
print('You can search for model with Paper_id, Model Doi, pdg code or name (of certain particles).')

# Now allows multiple times search
while True:
    search_type = input('Please choose your keyword type:')

    # Search for models with corresponding paper id
    if search_type == 'Paper_id':
        paper_id = input('Please enter your needed paper_id:')
        if Flag == 0:
            preparation()
        for file in os.listdir('.'):
            with open(file,encoding='utf-8') as metadata:
                metadatafile = json.load(metadata)
            paper_ids = [metadatafile['Paper_id'][i] for i in metadatafile['Paper_id']]
            if paper_id in paper_ids:
                print('The metadata file %s has the paper_id %s you are looking for.' %(file,paper_id))
    
    # Search for models with corresponding model Doi from Zenodo
    if search_type == 'Model Doi':
        Model_Doi = input('Please enter your needed Model doi:')
        if Flag == 0:
            preparation()
        for file in os.listdir('.'):
            with open(file,encoding='utf-8') as metadata:
                metadatafile = json.load(metadata)
            if Model_Doi == metadatafile['Model Doi']:
                print('The metadata file %s has Model Doi %s you are looking for.' %(file,metadatafile['Model Doi']))
    
    # Search for models with particles' pdg codes
    if search_type == 'pdg code':
        pdg_code = input('Please enter your needed pdg code:').split(',')
        pdg_code_list = [int(i) for i in pdg_code]
        if Flag == 0:
            preparation()
        for file in os.listdir('.'):
            with open(file,encoding='utf-8') as metadata:
                metadatafile = json.load(metadata)
            All_particles_pdg_code = [metadatafile['All Particles'][i] for i in metadatafile['All Particles']]
            pdg_dict = {}
            pdg_code_compare_result = all(i in All_particles_pdg_code for i in pdg_code_list)
            if pdg_code_compare_result:
                for i in metadatafile['All Particles']:
                    if metadatafile['All Particles'][i] in pdg_code_list:
                        pdg_dict[i] = metadatafile['All Particles'][i]
                print('The metadata file %s has particles %s you are looking for.' %(file,str(pdg_dict)))
    
    # Search for models with particles' names
    if search_type == 'name':
        particle_name_list = input('Please enter your needed particle name:').split(',')
        if Flag == 0:
            preparation()
        pdg_code_corresponding_list = []
        for file in os.listdir('.'):
            with open(file,encoding='utf-8') as metadata:
                metadatafile = json.load(metadata)
            All_particles_name_list = [i for i in metadatafile['All Particles']]
            particle_compare_result = all(i in All_particles_name_list for i in particle_name_list)
            if particle_compare_result:
                pdg_code_corresponding_list = [metadatafile['All Particles'][i] for i in particle_name_list]
                break
        if pdg_code_corresponding_list != []:
            for file in os.listdir('.'):
                with open(file,encoding='utf-8') as metadata:
                    metadatafile = json.load(metadata)
                All_particles_pdg_code = [metadatafile['All Particles'][i] for i in metadatafile['All Particles']]
                pdg_dict_from_particles = {}
                pdg_code_compare_result_from_particles = all(i in All_particles_pdg_code for i in pdg_code_corresponding_list)
                if pdg_code_compare_result_from_particles:
                    for i in metadatafile['All Particles']:
                        if metadatafile['All Particles'][i] in pdg_code_corresponding_list:
                            pdg_dict_from_particles[i] = metadatafile['All Particles'][i]
                    print('The metadata file %s has particles %s you are looking for.' %(file,str(pdg_dict_from_particles)))

    # Stop the loop and exit search part     
    if input('Do you still want to search for models? Please type in Yes or No.') == 'No':
        break

# Start download part
download_command = input('You can choose the metadata you want to download, or type No to exit:')

if download_command == 'No':
    # Delete temporary folder for metadata files
    os.chdir(api_path)
    shutil.rmtree('MetadatafilesTemporaryFolder')
    sys.exit()
else:
    # Get moodels' doi
    download_list = download_command.split(',')
    download_doi = []
    for file in download_list:
        with open(file) as metadata:
            metadatafile = json.load(metadata)
        download_doi.append(metadatafile['Model Doi'])

# Delete temporary folder for metadata files
os.chdir(api_path)
shutil.rmtree('MetadatafilesTemporaryFolder')

foldername = input('Please name your download folder:')
os.mkdir(foldername)
os.chdir(foldername)

# Download model files from zenodo using zenodo_get created by David Völgyes
for i in download_doi:
    single_download_doi = []
    single_download_doi.append(i)
    zenodo_get.zenodo_get(single_download_doi)

print('You have successfully downloaded your needed models in %s under the same path with this python script.' %(foldername))
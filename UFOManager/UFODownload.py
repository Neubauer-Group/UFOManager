import sys
from termcolor import colored
if sys.version_info.major == 2:
    raise Exception(colored('UFODownload.py only works for Python 3','red'))
from github import Github
import os
import requests
import shutil
import json
import zenodo_get
from getpass import getpass
import argparse
from tabulate import tabulate
from termcolor import colored
from particle import PDGID
# This python script utilizes zenodo_get package from David Volgyes
# David Volgyes. (2020, February 20). Zenodo_get: a downloader for Zenodo records (Version 1.3.4).
# Zenodo. https://doi.org/10.5281/zenodo.1261812

# Bibtex format:
'''@misc{david_volgyes_2020_10.5281/zenodo.1261812,
author  = {David V\"{o}lgyes},
title   = {Zenodo_get: a downloader for Zenodo records.},
month   = {2},
year    = {2020},
doi     = {10.5281/zenodo.1261812},
url     = {https://doi.org/10.5281/zenodo.1261812}
}'''


def AccessGitRepo(Github_Access_Token):
    # Connect to Github Repository

    g = Github(Github_Access_Token)
    repo = g.get_repo("Neubauer-Group/UFOMetadata")
    Allmetadata = repo.get_contents('Metadata')

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
        url = 'https://raw.githubusercontent.com/Neubauer-Group/UFOMetadata/main/Metadata/'
        url += name
        metadata = requests.get(url)
        open(name,'wb').write(metadata.content)

def Display(jsonlist):
    display_data = []    
    for file in jsonlist:
        with open(file,encoding='utf-8') as metadata:
            metadatafile = json.load(metadata)
        if 'arXiv' in metadatafile['Paper_id']:
            information = [file,metadatafile['Model name'],metadatafile['Paper_id']['arXiv'],metadatafile['Model Doi']] #metadatafile['Description']]
        else:
            if 'doi.org' in metadatafile['Paper_id']['doi']:
                information = [file,metadatafile['Model name'],metadatafile['Paper_id']['doi'][16:],metadatafile['Model Doi']] #,metadatafile['Description']]
            else:
                information = [file,metadatafile['Model name'],metadatafile['Paper_id']['doi'],metadatafile['Model Doi']] #,metadatafile['Description']]
        display_data.append(information)
    
    print(tabulate(display_data, headers=["Metadata file","Model Name","Paper ID","Model DOI"]))
        

def Search(Github_Access_Token):
    global api_path
    valid_search_keys = ['Paper_id', 'Model Doi', 'pdg code', 'name']
    # Start the Interface
    print('You can search for model with {}, {}, {}, {} (of certain particles).'.format(colored('Paper_id', 'magenta'),
                                                                                                                colored('Model Doi', 'magenta'),
                                                                                                                colored('pdg code', 'magenta'),
                                                                                                                colored('name', 'magenta'))
    )
    all_json_file = set()
    
    # Now allows multiple times search
    while True:
        search_type = input('Please choose your keyword type: ')
        if search_type not in valid_search_keys:
            print(colored('Invalid Keyword!', 'red'))
        
        # Search for models with corresponding paper id
        if search_type == 'Paper_id':
            paper_id = input('Please enter your needed paper_id: ')
            
            target_list = []
            for file in os.listdir('.'):
                with open(file,encoding='utf-8') as metadata:
                    metadatafile = json.load(metadata)
                paper_ids = [metadatafile['Paper_id'][i] for i in metadatafile['Paper_id']]
                if paper_id in paper_ids:
                    target_list.append(file)
            
            if len(target_list) == 0:
                print('There is no model associated with the paper_id ' + colored(paper_id,'red') + ' you are looking for.')
            else:
                print('Based on your search, we find models below:')
                Display(jsonlist=target_list)
                all_json_file = all_json_file.union(target_list)
        
        # Search for models with corresponding model Doi from Zenodo
        if search_type == 'Model Doi':
            Model_Doi = input('Please enter your needed Model doi: ')

            model_name = ''
            target_list = []
            current_working_doi = ''
            for file in os.listdir('.'):
                with open(file,encoding='utf-8') as metadata:
                    metadatafile = json.load(metadata)
                if Model_Doi == metadatafile['Model Doi']:
                    model_name = file
                    break
                if 'Existing Model Doi' in metadatafile and metadatafile['Existing Model Doi'] == Model_Doi:
                    model_name = file
                    break
            if len(model_name) != 0:
                target_list.append(model_name)
                with open(model_name,encoding='utf-8') as metadata:
                    _metadatafile = json.load(metadata)
                if 'Existing Model Doi' in _metadatafile:
                    current_working_doi = _metadatafile['Existing Model Doi']
                    for file in os.listdir('.'):
                        if file in target_list:
                            continue
                        with open(file,encoding='utf-8') as metadata:
                            metadatafile = json.load(metadata)
                        if 'Existing Model Doi' in metadatafile:
                            if metadatafile['Existing Model Doi'] == current_working_doi:
                                target_list.append(file)
                            continue
                        this_doi = metadatafile['Model Doi']
                        r = requests.get("https://doi.org/" + this_doi)
                        for line in r.iter_lines():
                            line = str(line)
                            if 'Cite all versions' not in line:
                                continue
                            conceptdoi = line.split("https://doi.org")[1].split('</a>')[0].split('">')[1]
                            break
                        if current_working_doi == conceptdoi:
                            target_list.append(file)
                print('Based on your search, we find models below:')                                                        
                Display(jsonlist=target_list)
                all_json_file = all_json_file.union(target_list)
            else:
                print('There is no model associated with the Model Doi ' + colored(Model_Doi,'red') + ' you are looking for.') 
            

        
        # Search for models with particles' pdg codes
        if search_type == 'pdg code':
            pdg_code = [f.strip() for f in input('Please enter your needed pdg code: ').split(',')]
            pdg_code_list = [int(i) for i in pdg_code]
            target_list = []
            elementary_particles_list = []
            for i in pdg_code_list:
                if PDGID(i).is_sm_quark == True or PDGID(i).is_sm_gauge_boson_or_higgs == True or PDGID(i).is_sm_lepton == True:
                    elementary_particles_list.append(i)
            elementary_particle_compare = all(i in elementary_particles_list for i in pdg_code_list)
            Feedback = 'All particles you are looking for are elementary particles which are contained by all models. Please try again with BSM particles.'
            if elementary_particle_compare:
                print(colored(Feedback,'red'))
            else:
                for file in os.listdir('.'):
                    with open(file,encoding='utf-8') as metadata:
                        metadatafile = json.load(metadata)
                    All_particles_pdg_code = [metadatafile['All Particles'][i] for i in metadatafile['All Particles']]
                    pdg_dict = {}
                    pdg_code_compare_result = all(i in All_particles_pdg_code for i in pdg_code_list)
                    if pdg_code_compare_result:
                        target_list.append(file)
                    
                if len(target_list) == 0:
                    print('There is no model containing all particle(s) with pdg code' + colored(pdg_code,'red') + ' you are looking for.')
                else:
                    print('Based on your search, we find models below:')
                    Display(jsonlist=target_list)
                    all_json_file = all_json_file.union(target_list)
                    
        
        # Search for models with particles' names
        if search_type == 'name':
            particle_name_list = [f.strip() for f in input('Please enter your needed particle name: ').split(',')]
            pdg_code_corresponding_list = []
            target_list = []

            for file in os.listdir('.'):
                with open(file,encoding='utf-8') as metadata:
                    metadatafile = json.load(metadata)
                All_particles_name_list = [i for i in metadatafile['All Particles']]
                particle_compare_result = all(i in All_particles_name_list for i in particle_name_list)
                if particle_compare_result:
                    pdg_code_corresponding_list = [metadatafile['All Particles'][i] for i in particle_name_list]
                    break
            if pdg_code_corresponding_list != []:
                elementary_particles_list = []
                for i in pdg_code_corresponding_list:
                    if PDGID(i).is_sm_quark == True or PDGID(i).is_sm_gauge_boson_or_higgs == True or PDGID(i).is_sm_lepton == True:
                        elementary_particles_list.append(i)
                elementary_particle_compare = all(i in elementary_particles_list for i in pdg_code_corresponding_list)
                Feedback = 'All particles you are looking for are elementary particles which are contained by all models. Please try again with BSM particles.'
                if elementary_particle_compare:
                    print(colored(Feedback,'red'))
                else:
                    for file in os.listdir('.'):
                        with open(file,encoding='utf-8') as metadata:
                            metadatafile = json.load(metadata)
                        All_particles_pdg_code = [metadatafile['All Particles'][i] for i in metadatafile['All Particles']]
                        pdg_dict_from_particles = {}
                        pdg_code_compare_result_from_particles = all(i in All_particles_pdg_code for i in pdg_code_corresponding_list)
                        if pdg_code_compare_result_from_particles:
                            target_list.append(file)
            else:
                print('There is no model containing all particle(s) ' + colored(particle_name_list,'red') + ' you are looking for.')

            if len(target_list) != 0:
                print('Based on your search, we find models below:')
                Display(jsonlist=target_list)
                all_json_file = all_json_file.union(target_list)
                                

        # Stop the loop and exit search part     
        if input('Do you still want to search for models? Please type in {} or {}: '.format(colored('Yes', 'green'), colored('No','red'))) == 'No':
            break
        
    return list(all_json_file)



def Downloader(Github_Access_Token, filelist=None):
    global api_path
    print('Here is the UFOModel metadata file list.')
    if not filelist:
        print("\n".join(list(os.listdir('.'))))
    else:
        print("\n".join(filelist))

    # Start download part
    download_command = input('Enter a comma separated list of metadata filenames from the list above to download corresponding files: ')

    # Get models' doi
    download_list = [f.strip() for f in download_command.split(',')]
    download_doi = []
    for file in download_list:
        with open(file,encoding='utf-8') as metadata:
            metadatafile = json.load(metadata)
        download_doi.append(metadatafile['Model Doi'])

    os.chdir(api_path)

    foldername = input('Please name your download folder: ')
    
    try:
        os.mkdir(foldername)
        os.chdir(foldername)
    except FileExistsError:
        os.chdir(foldername)

    # Download model files from zenodo using zenodo_get created by David Volgyes
    for i in download_doi:
        single_download_doi = []
        single_download_doi.append(i)
        zenodo_get.zenodo_get(single_download_doi)

    print('You have successfully downloaded your needed models in %s under the same path with this python script.' %(foldername))

def Search_Download(Github_Access_Token):
    jsonlist = Search(Github_Access_Token)
    Downloader(Github_Access_Token, jsonlist)

def Delete():
    global api_path
    os.chdir(api_path)
    shutil.rmtree('MetadatafilesTemporaryFolder')

def UFODownload(command):
    global api_path
    api_path = os.getcwd()
    Github_Access_Token = getpass('Please enter you Github access token:')
    AccessGitRepo(Github_Access_Token=Github_Access_Token)

    if command == 'Search for model':
        Search(Github_Access_Token=Github_Access_Token)
        Delete()
    elif command == 'Download model':
        Downloader(Github_Access_Token=Github_Access_Token)
        Delete()
    elif command == 'Search and Download':
        Search_Download(Github_Access_Token=Github_Access_Token)
        Delete()
    else:
        print('Wrong command! Please choose from ["Search for model", "Download model", "Search and Download"].')
        Delete()

if __name__ == '__main__':
    FUNCTION_MAP = {'Search for model' : Search,
                'Download model' : Downloader,
                'Search and Download': Search_Download}

    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=FUNCTION_MAP.keys())
    args = parser.parse_args()
    RunFunction = FUNCTION_MAP[args.command]

    Github_Access_Token = getpass('Please enter you Github access token:')
    api_path = os.getcwd()
    AccessGitRepo(Github_Access_Token=Github_Access_Token)
    RunFunction(Github_Access_Token=Github_Access_Token)
    Delete()

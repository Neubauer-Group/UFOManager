import os
import zipfile
import tarfile
import shutil
import sys
import json
import importlib
import requests
from github import Github
from getpass import getpass
import argparse
from termcolor import colored, cprint
import re

if sys.version_info.major == 3:
    raw_input = input

regex = r'[^@]+@[^@]+\.[^@]+'

def validator(model_path):

    '''    Check for necessary files and their formats   '''
    # List of all files in the folder
    original_file = os.listdir(model_path)

    #  Check if the folder contains and only contains required files
    assert len(original_file) == 2, \
        'File Count check: ' + colored('FAILED! More than two files inside the given directory'.format(model_path), 'red')
    print('File count check: ' + colored('PASSED!', 'green'))

    assert 'metadata.json' in original_file, \
        'Check if initial "metadata.json" exists: ' + colored('FAILED!', 'red')
    try:
        metadata = open('metadata.json')
        file = json.load(metadata)
    except:
        raise Exception(colored('Check if initial "metadata.json" is correctly formatted: ') + colored('FAILED!', 'red'))
    print('Check if initial "metadata.json" exists and correctly formatted: ' + colored('PASSED!', 'green'))


    '''    Check the content of metadata.json    '''
    
    # Check uploaded metadata.json for author names and contacts
    
    try:
        assert file['Author']
    except:
        raise Exception(colored('"Author" field does not exist in metadata', 'red'))
    all_contact = []
    for i in file['Author']:
        try:
            assert i['name'].strip()
        except:
            raise Exception(colored('At least one author name does not exist in metadata', 'red'))
        if 'contact' in i:
            assert re.match(regex, i['contact'].strip()), \
                Exception(colored('At least one author contact is not a valid email address', 'red'))
            all_contact.append(i['contact'])
    assert all_contact != [], colored('No contact information for authors exists ', 'red')
    print('Check author information and contact information in initial metadata:' + colored(' PASSED!', 'green'))

    # Check uploaded metadata.json for a paper id
    
    try:
        assert file['Paper_id']
    except:
        raise Exception(colored('"Paper_id" field does not exist in metadata', 'red'))
    if 'doi' in file['Paper_id']:
        url = 'https://doi.org/' + file['Paper_id']['doi']
        doi_webpage = requests.get(url)
        assert doi_webpage.status_code < 400, colored('DOI does not resolve to a valid paper', 'red')
    if 'arXiv' in file['Paper_id']:
        url = 'https://arxiv.org/abs/' + file['Paper_id']['arXiv']
        arXiv_webpage = requests.get(url)
        assert arXiv_webpage.status_code < 400, colored('arxiv id does not resolve to a valid paper', 'red')
    print('Check paper information in initial metadata:' + colored(' PASSED!', 'green'))


    # Check uploaded metadata.json for model description
    
    try:
        assert file['Description']
    except:
        raise Exception(colored('"Description" field does not exist in metadata', 'red'))

    '''    Unpack the model inside a directory called "ModelFolder"     '''
    
    for i in original_file:
        if i.endswith('.json'):
            pass
        else:
            assert i.endswith('.zip') or i.endswith('.tgz') or i.endswith('.tar.gz'), \
                colored('Compressed UFO model not found', 'red')
            # Uncompress the model file to a temprory folder to get ready for validation test
            if i.endswith('.zip'):
                with zipfile.ZipFile(i, 'r') as zip:
                    zip.extractall('ModelFolder')
            else:
                tarfile.open(i).extractall('ModelFolder')

                
    '''    Check if the compressed folder contains a single model and
           reorganize its content inside a directory called "ModelFolder"    '''
    
    ModelFolder_Files = os.listdir('ModelFolder')
    if '__init__.py' not in ModelFolder_Files:
        if len(ModelFolder_Files) != 1:
            raise Exception(colored('Uncompressed content has too many files/folders', 'red'))
        if '__init__.py' not in os.listdir('ModelFolder/' + ModelFolder_Files[0]):
            raise Exception(colored('"__init__.py" not available within model, not a Python Package!', 'red'))
        for _file in os.listdir('ModelFolder/' + ModelFolder_Files[0]):
            if _file == "__pycache__" or _file.endswith(".pyc") or _file.endswith("~"):
                shutil.rmtree('ModelFolder/' + ModelFolder_Files[0] + '/__pycache__')
                continue
            shutil.copy('ModelFolder/' + ModelFolder_Files[0] + '/' +  _file, 'ModelFolder/' +  _file)
        shutil.rmtree('ModelFolder/' + ModelFolder_Files[0])


    '''    Check if the model can be loaded as a python package    '''
    
    if True:     
        sys.path.append(model_path)
        modelpath = model_path + '/ModelFolder'
        sys.path.insert(0,modelpath)
        if sys.version_info.major == 3:
            try:
                UFOModel = importlib.import_module('ModelFolder')
            except SyntaxError:
                os.chdir(model_path)
                shutil.rmtree('ModelFolder')
                raise Exception(colored('The model may be not compatible with Python3 or have invalid code syntaxes. Please check and try with Python2 instead',
                                        'red'))
            except ModuleNotFoundError:
                os.chdir(model_path)
                shutil.rmtree('ModelFolder')
                raise Exception(colored('The model may be missing some files, please check again', 'red'))
            except AttributeError:
                os.chdir(model_path)
                shutil.rmtree('ModelFolder')
                raise Exception(colored('Undefined variables in your imported modules, please check again', 'red'))
            except NameError:
                os.chdir(model_path)
                shutil.rmtree('ModelFolder')
                raise Exception(colored('Some modules/variables not imported/defined, please check again', 'red'))
            except TypeError:
                os.chdir(model_path)
                shutil.rmtree('ModelFolder')
                raise Exception(colored('At least one of the variables is missing required positional argument, please check again.','red'))
        else:
            try:
                UFOModel = importlib.import_module('ModelFolder')
            except SyntaxError:
                os.chdir(model_path)
                shutil.rmtree('ModelFolder')
                raise Exception('Your model may have invalid syntaxes, please check again')
            except ImportError:
                os.chdir(model_path)
                shutil.rmtree('ModelFolder')
                raise Exception(colored('The model may be missing some files, please check again', 'red'))
            except AttributeError:
                os.chdir(model_path)
                shutil.rmtree('ModelFolder')
                raise Exception(colored('Undefined variables in your imported modules, please check again', 'red'))
            except NameError:
                os.chdir(model_path)
                shutil.rmtree('ModelFolder')
                raise Exception(colored('Some modules/variables not imported/defined, please check again', 'red'))
            except TypeError:
                os.chdir(model_path)
                shutil.rmtree('ModelFolder')
                raise Exception(colored('At least one of the variables is missing required positional argument, please check again.','red'))

        os.chdir('ModelFolder')

    print("Check for module imported as a python package: " + colored("PASSED!", "green"))


    '''    Check the existence of model-independent files    '''
    
    ModelFiles = os.listdir('.')
    Neccessary_MI_Files = ['__init__.py', 'object_library.py', 'function_library.py', 'write_param_card.py']
    Missing_MI_Files = [i for i in Neccessary_MI_Files if i not in ModelFiles]
    if Missing_MI_Files != []:
        print(colored('Your model lacks these files below'))
        print(colored(', '.join(Missing_MI_Files), 'brown'))
        raise Exception(colored('Sorry, your model misses some necessary model-independent files.', 'red'))
    else:
        print("Check if model contains necessary model-independent files: " + colored("PASSED!", 'green'))

    '''    Check the existence of model-dependent files    '''
    
    Neccessary_MD_Files = ['parameters.py','particles.py','coupling_orders.py','couplings.py','lorentz.py','vertices.py']
    Missing_MD_Files = [i for i in Neccessary_MD_Files if i not in ModelFiles]
    if Missing_MD_Files != []:
        print(colored('Your model lacks these files below'))
        print(colored(', '.join(Missing_MD_Files), 'brown'))
        raise Exception(colored('Sorry, your model misses some necessary model-dependent files.', 'red'))
    else:
        print("Check if model contains necessary model-dependent files: " + colored("PASSED!", 'green'))

    '''    Check individual files within the model    '''
    
    model_folder_path = os.getcwd()
    sys.path.insert(0,model_folder_path)

    # Check on model-independent files
    try:
        import object_library
    except:
        raise Exception(colored('The file "object_library.py" could not be imported. Please check again', 'red'))

    # Check parameters.py and if it contains some parameters
    try:
        import parameters
    except ImportError:
        os.chdir(model_path)
        shutil.rmtree('ModelFolder')
        raise Exception(colored('The file "parameters.py" could not be imported. Please check again', 'red'))
    
 
    params = []
    number_of_params = 0
    for i in [item for item in dir(parameters) if not item.startswith("__")]:    
        item = getattr(parameters,i)
        if type(item) == (object_library.Parameter):
            params.append(item.name)
            number_of_params += 1

    if len(params) == 0:
        raise Exception(colored('There should be some parameters defined in "parameters.py"', 'red'))
    else:
        print('Check if model contains well behaved "parameters.py": ' + colored("PASSED!", 'green'))
        print('The model contains %i parameters.' %(number_of_params))

    del sys.modules['parameters']
    
    # Check particles.py and if contains particles
    try:
        import particles
    except ImportError:
        os.chdir(model_path)
        shutil.rmtree('ModelFolder')
        raise Exception(colored('The file "particles.py" could not be imported. Please check again', 'red'))

    particle_dict = {}
    new_particle_dict = {}
    pdg_code_list = []
    number_of_particles = 0
    spin = [1, 2, 3, 5]
    elementary_particles = [1, -1, 2, -2, 3, -3, 4, -4, 5, -5, 6, -6, 11, 12, 13, 14, 15, 16, -11, -12, -13, -14, -15, -16, 9, 21, 22, 23, 24, -24, 25, 35, 36, 37, -37]
    for i in [item for item in dir(particles) if not item.startswith("__")]:
        item = getattr(particles,i)
        if type(item) == (object_library.Particle):
            number_of_particles += 1
            particle_dict[item.name] = item.pdg_code
            pdg_code_list.append(item.pdg_code)
            if item.spin in spin and item.pdg_code not in elementary_particles:
                new_particle_dict[item.name] = item.pdg_code

    if len(particle_dict) == 0:
        raise Exception(colored('There should be particles defined in "particles.py"', 'red'))

    if len(set(pdg_code_list)) != len(pdg_code_list):
        raise Exception(colored('Some of your particles have same pdg code, please check again!', 'red'))
    
    print('Check if model contains well behaved "particles.py": ' + colored("PASSED!", 'green'))
    print('The model contains %i fundamental particles' %(number_of_particles))
    print('The model contains %i new elementary particles and corresponding pdg codes are:'%(len(list(new_particle_dict.keys()))))
    for key in new_particle_dict.keys():
        print(key, new_particle_dict[key])

    del sys.modules['particles']

    # Check vertices.py and if it contains vertices
    try:
        import vertices
    except ImportError:
        os.chdir(model_path)
        shutil.rmtree('ModelFolder')
        raise Exception(colored('The file "vertices.py" could not be imported. Please check again', 'red'))

    vertex = []
    number_of_vertices = 0
    for i in [item for item in dir(vertices) if not item.startswith("__")]:
        item = getattr(vertices,i)
        if type(item) == (object_library.Vertex):
            vertex.append(item.name)
            number_of_vertices += 1

    if len(vertex) == 0:
        raise Exception(colored('There should be vertices defined in "vertices.py"', 'red'))
    else:
        print('Check if model contains well behaved "vertices.py": ' + colored("PASSED!", 'green'))
        print('The model contains %i vertices' %(number_of_vertices))
        
    del sys.modules['vertices']

    # Check coupling_orders.py and if it contains coupling orders
    try:
        import coupling_orders
    except ImportError:
        os.chdir(model_path)
        shutil.rmtree('ModelFolder')
        raise Exception(colored('The file "coupling_orders.py" could not be imported. Please check again', 'red'))

    coupling_order = []
    number_of_coupling_orders = 0
    for i in [item for item in dir(coupling_orders) if not item.startswith("__")]:
        item = getattr(coupling_orders,i)
        if type(item) == (object_library.CouplingOrder):
            coupling_order.append(item.name)
            number_of_coupling_orders += 1

    if len(coupling_order) == 0:
        raise Exception(colored('There should be coupling orders defined in "coupling_orders.py"','red'))
    else:
        print('Check if model contains well behaved "coupling_orders.py": ' + colored("PASSED!", 'green'))
        print('The model contains %i coupling_orders' %(number_of_coupling_orders))

    del sys.modules['coupling_orders']


    # Check couplings.py and if it contains couplings
    try:
        import couplings
    except ImportError:
        os.chdir(model_path)
        shutil.rmtree('ModelFolder')
        raise Exception(colored('The file "couplings.py" could not be imported. Please check again', 'red'))

    coupling_tensor = []
    number_of_coupling_tensors = 0
    for i in [item for item in dir(couplings) if not item.startswith("__")]:
        item = getattr(couplings,i)
        if type(item) == (object_library.Coupling):
            coupling_tensor.append(item.name)
            number_of_coupling_tensors += 1

    if len(coupling_tensor) == 0:
        raise Exception('There should be coupling tensors defined in "couplings.py"')
    else:
        print('Check if model contains well behaved "couplings.py": ' + colored("PASSED!", 'green'))
        print('The model contains %i couplings' %(number_of_coupling_tensors))

    del sys.modules['couplings']


    # Check lorentz.py and see if it contains lorentz tensors
    try:
        import lorentz
    except ImportError:
        os.chdir(model_path)
        shutil.rmtree('ModelFolder')
        raise Exception(colored('The file "lorentz.py" could not be imported. Please check again', 'red'))

    lorentz_tensor = []
    number_of_lorentz_tensors = 0
    for i in [item for item in dir(lorentz) if not item.startswith("__")]:    
        item = getattr(lorentz,i)
        if type(item) == (object_library.Lorentz):
            lorentz_tensor.append(item.name)
            number_of_lorentz_tensors += 1

    if len(lorentz_tensor) == 0:
        raise Exception(colored('There should be lorentz tensors defined in "lorentz.py"', 'red'))
    else:
        print('Check if model contains well behaved "lorentz.py": ' + colored("PASSED!", 'green'))
        print('The model contains %i lorentz tensors' %(number_of_lorentz_tensors))

    del sys.modules['lorentz']


    # Check if propagators.py contains propagators
    try:
        import propagators
        props = []
        number_of_propagators = 0
        for i in [item for item in dir(propagators) if not item.startswith("__")]:
            item = getattr(propagators,i)
            if type(item) == (object_library.Propagator):
                props.append(item.name)
                number_of_propagators += 1

        if len(props) == 0:
            raise Exception('There should be propagators defined in "propagators.py"')
        else:
            print('Check if model contains well behaved "propagators.py": ' + colored("PASSED!", 'green'))
            print('The model contains %i propagators' %(number_of_propagators))
        del sys.modules['propagators']  
    except ImportError:
        number_of_propagators = 0
        pass

    # Check if decays.py contains decays
    try:
        import decays
        decay = []
        number_of_decays = 0
        for i in [item for item in dir(decays) if not item.startswith("__")]:
            item = getattr(decays,i)
            if type(item) == (object_library.Decay):
                decay.append(item.name)
                number_of_decays += 1

        if len(decay) == 0:
            raise Exception('There should be decays defined in "decays.py"')
        else:
            print('Check if model contains well behaved "decayss.py": ' + colored("PASSED!", 'green'))
            print('The model contains %i propagators' %(number_of_decays))
        del sys.modules['decays']
    except ImportError:
        number_of_decays = 0
        pass

    # Finish the validation checking
    sys.path.remove(model_folder_path)
    os.chdir(model_path)
    shutil.rmtree('ModelFolder')

    return file, original_file, number_of_params, particle_dict, new_particle_dict, number_of_vertices, number_of_coupling_orders, number_of_coupling_tensors, number_of_lorentz_tensors, number_of_propagators, number_of_decays



def metadatamaker(model_path, create_file = True):
    # Check Validation and get necessary outputs
    file, original_file, number_of_params, particle_dict, new_particle_dict, number_of_vertices, number_of_coupling_orders, number_of_coupling_tensors, number_of_lorentz_tensors, number_of_propagators, number_of_decays = validator(model_path)
    filename = [i for i in original_file if i != 'metadata.json'][0]
    modelname = raw_input('Please name your model:')
    modelversion = raw_input('Please enter your model version:')
    Doi = "0"
    if create_file:
        Doi = raw_input('Please enter your Model Doi, enter 0 if not have one:')
    newcontent = {'Model name' : modelname,
                'Model Doi' : Doi,
                'Model Version' : modelversion,
                'Model Python Version' : sys.version_info.major,
                'All Particles' : particle_dict,
                'New elementary particles' : new_particle_dict,
                'Number of parameters' : number_of_params,
                'Number of vertices' : number_of_vertices,
                'Number of coupling orders' : number_of_coupling_orders,
                'Number of coupling tensors' : number_of_coupling_tensors,
                'Number of lorentz tensors' : number_of_lorentz_tensors,
                'Number of propagators' : number_of_propagators,
                'Number of decays' : number_of_decays
                }

    file.update(newcontent)
    meta_name = filename.split('.')[0]
    if not meta_name:
        raise Exception("Invalid filename: '{}', please cheack".format(filename))
    metadata_name =  meta_name + '.json'
    if create_file:
        with open(metadata_name,'w') as metadata:
            json.dump(file,metadata,indent=2)
        # Check new metadata
        print('Now you can see your the metadata file %s for your new model in the same directory.' %(metadata_name))

    return file, filename, modelname, metadata_name
        

def uploader(model_path):
    
    '''    Generate the metadata for the model   '''
    file, filename, modelname, metadata_name = metadatamaker(model_path, create_file=False)

    '''    Check if  Zenodo token works    '''
    Zenodo_Access_Token = getpass('Please enter your Zenodo access token:')
    params = {'access_token': Zenodo_Access_Token}
    r = requests.get("https://zenodo.org/api/deposit/depositions", params=params)
    if r.status_code > 400:
        raise Exception(colored("URL connection with Zenodo Failed!", "red") + " Status Code: " + colored("{}".format(r.status_code), "red"))
    print("Validating Zenodo access token: " + colored("PASSED!", "green"))
    

    '''    Check if Github token works    '''
    Github_Access_Token = getpass('Please enter you Github access token:')
    try:
        g = Github(Github_Access_Token)
        github_user = g.get_user()
        # Get the public repo
        repo = g.get_repo('ThanosWang/UFOMetadata')
    except:
        raise Exception(colored("Github access token cannot be validated", "red"))

    print("Validating Github access token: " + colored("PASSED!", "green"))

    
    '''    Check if user's metadata repo is in sync with upstream    '''
    # Create a fork in user's github
    myfork = github_user.create_fork(repo)

    # Check if the fork is up to date with main
    if repo.get_branch('main').commit.sha != myfork.get_branch('main').commit.sha:
        print(colored("Your fork of the UFOMetadata repo is out of sync from the upstream!", "red"))
        print(colored("Please retry after syncing your local fork with upstream", "yellow"))
        raise Exception

    
    # Create an empty upload
    headers = {"Content-Type": "application/json"}
    params = {'access_token': Zenodo_Access_Token}
    r = requests.post("https://zenodo.org/api/deposit/depositions", 
                    params= params,
                    json= {},
                    headers= headers)
    if r.status_code > 400:
        print(colored("Creating deposition entry with Zenodo Failed!", "red"))
        print("Status Code: {}".format(r.status_code))
        raise Exception
    # Work with Zenodo API
    
    bucker_url = r.json()["links"]["bucket"]
    Doi = r.json()["metadata"]["prereserve_doi"]["doi"]
    deposition_id = r.json()["id"]

     # Upload new files
    #filename = [i for i in original_file if i != 'metadata.json'][0]
    path = model_path + '/%s' %(filename)

    with open(path, 'rb') as fp:
        r = requests.put("%s/%s" %(bucker_url, filename),
                         data = fp,
                         params = params)
        if r.status_code > 400:
            print(colored("Putting content to Zenodo Failed!", "red"))
            print("Status Code: {}".format(r.status_code))
            raise Exception
    


    Author_Full_Information = [i for i in file['Author']]
    Author_Information = []
    for i in Author_Full_Information:
        if 'affiliation' in i:
            Author_Information.append({"name": i['name'],
                                    "affiliation": i['affiliation']})
        else:
            Author_Information.append({"name": i['name']})

    data = { 'metadata' : {
            'title': modelname,
            'upload_type': 'dataset',
            'description': file['Description'],
            'creators': Author_Information          
        }
    }

    # Add required metadata to draft
    r = requests.put('https://zenodo.org/api/deposit/depositions/%s' %(deposition_id),
                     params=params, #{'access_token': Zenodo_Access_Token}, 
                    data=json.dumps(data),
                    headers=headers)
    if r.status_code > 400:
        print(colored("Creating deposition entry with Zenodo Failed!", "red"))
        print("Status Code: {}".format(r.status_code))
        raise Exception
    file["Model Doi"] = Doi

    with open(metadata_name,'w') as metadata:
        json.dump(file,metadata,indent=2)


    '''    Upload to Github Repository    '''


    # Create new metadata file in the forked repo
    f= open(metadata_name).read()

    GitHub_filename = 'Metadata/' + metadata_name

    myfork.create_file(GitHub_filename, 'Upload metadata for model: {}'.format(metadata_name.replace('.json', '')), f, branch='main')

    # Pull Request from forked branch to original
    username = g.get_user().login

    body = 'Upload metadata for new model(s)'

    # Final Check before all upload

    if r.status_code == 200:
        print('Now you can go to Zenodo to see your draft, make some changes, and be ready to publish your model.')
        publish_command = raw_input('Do you want to publish your model and send your new enriched metadata file to GitHub repository UFOMetadata? Yes or No:')
        if publish_command == 'Yes':
            r = requests.post('https://zenodo.org/api/deposit/depositions/%s/actions/publish' %(deposition_id),
                              params=params) #{'access_token': Zenodo_Access_Token} )
            if r.status_code > 400:
                print(colored("Publishing model with Zenodo Failed!", "red"))
                print("Status Code: {}".format(r.status_code))
                raise Exception
            #print(r.json())
            #print(r.status_code)
            print('Your model has been successfully uploaded to Zenodo with DOI: %s' %(Doi))
            print('You can  access your model in Zenodo at: {}'.format(r.json()['links']['record_html']))
            pr = repo.create_pull(title="Upload metadata for a new model", body=body, head='{}:{}'.format(username,'main'), base='{}'.format('main'))
            print('''
            You have successfully upload your model to Zenodo and create a pull request of your new enriched metadate file to GitHub repository UFOMetadata. 
            If this is your first time pull request to UFOMetadata, your pull request need to be admitted before being checked by GitHub workflow.
            If your pull request failed or workflow doesn't start, please contact thanoswang@163.com.
            ''')
        else:
            print("You can publish your model by yourself. Then, please send your enriched metadata file to thanoswang@163.com. I will help upload your metadata to GitHub Repository.")
    else:
        print('Your Zenodo upload Draft may have some problems. You can check your Draft on Zenodo and publish it by yourself. Then, please send your enriched metadata file to thanoswang@163.com. I will help upload your metadata to GitHub Repository.')          


FUNCTION_MAP = {'Validation Check' : validator,
                'Generate metadata' : metadatamaker,
                'Upload model': uploader}

parser = argparse.ArgumentParser()
parser.add_argument('command', choices=FUNCTION_MAP.keys())

args = parser.parse_args()

RunFunction = FUNCTION_MAP[args.command]

if __name__ == '__main__':
    Path = raw_input('Please enter the path of your folder, starting from your current working directory:')
    # Get into the folder
    os.chdir(Path)
    # Path of the folder's content
    model_path = os.getcwd()
    RunFunction(model_path=model_path)

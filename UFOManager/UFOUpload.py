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
import datetime
from particle import PDGID

if sys.version_info.major == 3:
    raw_input = input

regex = r'[^@]+@[^@]+\.[^@]+'

def validator(model_path):

    print("\nChecking Model: " + colored(model_path, "magenta") + "\n")
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
            if not re.match(regex, i['contact'].strip()):
                print(colored('At least one author contact is not a valid email address, please check!', 'yellow'))
            all_contact.append(i['contact'])
    assert all_contact != [], colored('No contact information for authors exists ', 'red')
    print('Check author information and contact information in initial metadata:' + colored(' PASSED!', 'green'))

    # Check uploaded metadata.json for a paper id
    
    try:
        assert file['Paper_id']
    except:
        raise Exception(colored('"Paper_id" field does not exist in metadata', 'red'))
    assert 'doi' in file['Paper_id'] or 'arXiv' in file['Paper_id'], \
        Exception(colored('"Paper_id" field does not contain doi or arXiv ID', 'red'))
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

    # Check uploaded metadata.json for Model Homepage if exists

    if 'Model Homepage' in file:
        try:
            assert requests.get(file['Model Homepage']).status_code < 400
        except:
            raise Exception(colored('"Model Homepage" link is invalid in metadata', 'red'))
    
    '''    Unpack the model inside a directory called "ModelFolder"     '''
    
    for _file in original_file:
        if _file.endswith('.json'):
            pass
        elif _file.endswith('.zip'):
            with zipfile.ZipFile(_file, 'r') as zip:
                zip.extractall('ModelFolder')
        elif _file.endswith('.tar') or _file.endswith('.tgz') or _file.endswith('.tar.gz'):
            tarfile.open(_file).extractall('ModelFolder')
        elif os.path.isdir(_file):
            cf = tarfile.open( _file + ".tgz", "w:gz")
            for _f in os.listdir(_file):
                cf.add(_file + '/' + _f)
            cf.close()
            shutil.move(_file, 'ModelFolder')
            original_file.remove(_file)
            original_file.append(_file + ".tgz")
        else:
            raise Exception(colored("Valid Format for UFO directory not found", "red"))

                
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
                shutil.rmtree('ModelFolder/' + ModelFolder_Files[0] + '/' + _file)
                continue
            shutil.copy('ModelFolder/' + ModelFolder_Files[0] + '/' +  _file, 'ModelFolder/' +  _file)
        shutil.rmtree('ModelFolder/' + ModelFolder_Files[0])


    '''    Check if the model can be loaded as a python package    '''
    
    sys.path.append(model_path)
    modelloc = model_path + '/ModelFolder'
    sys.path.insert(0,modelloc)

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
    
    # Check particles.py and all particles
    try:
        import particles
    except ImportError:
        os.chdir(model_path)
        shutil.rmtree('ModelFolder')
        raise Exception(colored('The file "particles.py" could not be imported. Please check again', 'red'))

    particle_dict = {}
    SM_elementary_particle_dict = {}
    BSM_elementary_particle_with_registered_PDGID_dict = {}
    Particle_with_PDG_like_ID_dict = {}
    pdg_code_list = []
    for i in [item for item in dir(particles) if not item.startswith("__")]:
        item = getattr(particles,i)
        if type(item) == (object_library.Particle):
            if item.GhostNumber == 0:
                particle_dict[item.name] = item.pdg_code
                pdg_code_list.append(item.pdg_code)

                if PDGID(item.pdg_code).is_valid == True:
                    if PDGID(item.pdg_code).three_charge != int(round(item.charge*3)):
                        Particle_with_PDG_like_ID_dict[item.name] = {'id': item.pdg_code,
                                                                     'spin': item.spin,
                                                                     'charge': item.charge}
                    if PDGID(item.pdg_code).j_spin != item.spin:
                        if item.spin == 1 and PDGID(item.pdg_code).j_spin == None:
                            pass
                        else:
                            Particle_with_PDG_like_ID_dict[item.name] = {'id': item.pdg_code,
                                                                         'spin': item.spin,
                                                                         'charge': item.charge}

                    #if PDGID(item.pdg_code).is_quark or PDGID(item.pdg_code).is_lepton or PDGID(item.pdg_code).is_gauge_boson_or_higgs:
                    if item.spin in [1,2,3]:   
                        if PDGID(item.pdg_code).is_sm_quark or PDGID(item.pdg_code).is_sm_lepton or PDGID(item.pdg_code).is_sm_gauge_boson_or_higgs:
                            SM_elementary_particle_dict[item.name] = item.pdg_code
                        elif item.name not in Particle_with_PDG_like_ID_dict.keys():
                            BSM_elementary_particle_with_registered_PDGID_dict[item.name] = item.pdg_code
                else:
                    Particle_with_PDG_like_ID_dict[item.name] = {'id': item.pdg_code,
                                                                 'spin': item.spin,
                                                                 'charge': item.charge}                    

    if len(particle_dict) == 0:
        os.chdir(model_path)
        shutil.rmtree('ModelFolder')
        raise Exception(colored('There should be real particles defined in "particles.py"', 'red'))

    if len(set(pdg_code_list)) != len(pdg_code_list):
        os.chdir(model_path)
        shutil.rmtree('ModelFolder')
        raise Exception(colored('Some of your particles have same pdg code, please check again!', 'red'))

    print('Check if model contains well behaved "particles.py": ' + colored("PASSED!", 'green'))

    print('The model contains %i fundamental particles' %(len(SM_elementary_particle_dict)))

    print('The model contains %i Standard Model elementary particles with registered pdg codes:'%(len(list(SM_elementary_particle_dict.keys()))))
    for key in SM_elementary_particle_dict.keys():
        print(key, SM_elementary_particle_dict[key])
    
    print('The model contains %i Beyond the Standard Model elementary particles with registered pdg codes:'%(len(list(BSM_elementary_particle_with_registered_PDGID_dict.keys()))))
    for key in BSM_elementary_particle_with_registered_PDGID_dict.keys():
        print(key, BSM_elementary_particle_with_registered_PDGID_dict[key])

    print('The model contains %i particles with pdg-like codes:'%(len(list(Particle_with_PDG_like_ID_dict.keys()))))
    for key in Particle_with_PDG_like_ID_dict.keys():
        print(key, Particle_with_PDG_like_ID_dict[key])

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
        os.chdir(model_path)
        shutil.rmtree('ModelFolder')
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
        os.chdir(model_path)
        shutil.rmtree('ModelFolder')
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
        os.chdir(model_path)
        shutil.rmtree('ModelFolder')
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
        os.chdir(model_path)
        shutil.rmtree('ModelFolder')
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
            os.chdir(model_path)
            shutil.rmtree('ModelFolder')
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
            os.chdir(model_path)
            shutil.rmtree('ModelFolder')
            raise Exception('There should be decays defined in "decays.py"')
        else:
            print('Check if model contains well behaved "decays.py": ' + colored("PASSED!", 'green'))
            print('The model contains %i decays' %(number_of_decays))
        del sys.modules['decays']
    except ImportError:
        number_of_decays = 0
        pass

    # Check if the model supports NLO calculations
    try:
        import CT_couplings
        CT_coupling = []
        for i in [item for item in dir(CT_couplings) if not item.startswith("__")]:
            item = getattr(CT_couplings,i)
            if type(item) == (object_library.Coupling):
                CT_coupling.append(item.name)
        if len(CT_coupling) == 0:
            Check_CTCouplings = False
            print('Check if model contains well behaved "CT_couplings.py": ' + colored("FAILED!", 'red'))
        else:
            print('Check if model contains well behaved "CT_couplings.py": ' + colored("PASSED!", 'green'))
            Check_CTCouplings = True
        del sys.modules['CT_couplings']
    except ImportError:
        print('Check if model contains well behaved "CT_couplings.py": ' + colored("FAILED!", 'red'))
        Check_CTCouplings = False

    try:
        import CT_parameters
        CT_parameter = []
        for i in [item for item in dir(CT_parameters) if not item.startswith("__")]:
            item = getattr(CT_parameters,i)
            if type(item) == (object_library.CTParameter):
                CT_parameter.append(item.name)
        if len(CT_parameter) == 0:
            Check_CTParameters = False
            print('Check if model contains well behaved "CT_parameters.py": ' + colored("FAILED!", 'red'))
        else:
            print('Check if model contains well behaved "CT_parameters.py": ' + colored("PASSED!", 'green'))
            Check_CTParameters = True
    except ImportError:
        print('Check if model contains well behaved "CT_parameters.py": ' + colored("FAILED!", 'red'))
        Check_CTParameters = False

    try:
        import CT_vertices
        CT_vertice = []
        for i in [item for item in dir(CT_vertices) if not item.startswith("__")]:
            item = getattr(CT_vertices,i)
            if type(item) == (object_library.CTVertex):
                CT_vertice.append(item.name)
        if len(CT_vertice) == 0:
            Check_CTVertices = False
            print('Check if model contains well behaved "CT_vertices.py": ' + colored("FAILED!", 'red'))
        else:
            print('Check if model contains well behaved "CT_vertices.py": ' + colored("PASSED!", 'green'))
            Check_CTVertices = True
    except ImportError:
        print('Check if model contains well behaved "CT_vertices.py": ' + colored("FAILED!", 'red'))
        Check_CTVertices = True
    
    if Check_CTCouplings == True and Check_CTParameters == True and Check_CTVertices == True:
        print(colored('The model allows NLO calculations.','green'))
        NLO_value = True
    else:
        print(colored('The model does not allow NLO calculations.','red'))
        NLO_value = False
    
    # Finish the validation checking
    os.chdir(model_path)
    shutil.rmtree('ModelFolder')
    sys.path.remove(model_path)
    sys.path.remove(modelloc)
    for f in [f for f in sys.modules.keys() if 'ModelFolder' in f]:
        del sys.modules[f]
    for f in ['particles', 'parameters', 'vertices', 'coupling_orders', 'couplings', 'lorentz', 'propagators', 'decays']:
        if f in sys.modules.keys():
            del sys.modules[f]        

    return file, original_file, number_of_params, particle_dict, SM_elementary_particle_dict, Particle_with_PDG_like_ID_dict, BSM_elementary_particle_with_registered_PDGID_dict, number_of_vertices, number_of_coupling_orders, number_of_coupling_tensors, number_of_lorentz_tensors, number_of_propagators, number_of_decays, NLO_value


def validator_all(all_models):
    base_path = os.getcwd()
    for _path in all_models:
        os.chdir(_path)
        _ = validator(model_path = os.getcwd())
        os.chdir(base_path)


def metadatamaker(model_path, create_file = True):
    # Check Validation and get necessary outputs
    file, original_file, number_of_params, particle_dict, SM_elementary_particle_dict, Particle_with_PDG_like_ID_dict, BSM_elementary_particle_with_registered_PDGID_dict, number_of_vertices, number_of_coupling_orders, number_of_coupling_tensors, number_of_lorentz_tensors, number_of_propagators, number_of_decays, NLO_value = validator(model_path)
    filename = [i for i in original_file if i != 'metadata.json'][0]
    print('\nWorking on model: ' + colored(model_path, "magenta") + "\n")
    modelname = raw_input('Please name your model:')
    modelversion = raw_input('Please enter your model version:')
    Doi = "0"
    if 'Model Homepage' in file:
        Homepage = file['Model Homepage']
    else:
        if create_file:
            Homepage = raw_input('Please enter your model homepage:')
        else:
            Homepage = ''
    # if create_file or "Model Doi" not in file.keys():
    #    Doi = raw_input('Please enter your Model Doi, enter 0 if not have one:')
    if  "Model Doi" in file.keys():
        Doi = file["Model Doi"]
    newcontent = {'Model name' : modelname,
                'Model Homepage' : Homepage,
                'Model Doi' : Doi,
                'Model Version' : modelversion,
                'Model Python Version' : sys.version_info.major,
                'Allows NLO calculations': NLO_value,
                'All Particles' : particle_dict,
                'SM particles' : SM_elementary_particle_dict,
                'BSM particles with standard PDG codes': BSM_elementary_particle_with_registered_PDGID_dict,
                'Particles with PDG-like IDs': Particle_with_PDG_like_ID_dict,
                'Number of parameters' : number_of_params,
                'Number of vertices' : number_of_vertices,
                'Number of coupling orders' : number_of_coupling_orders,
                'Number of coupling tensors' : number_of_coupling_tensors,
                'Number of lorentz tensors' : number_of_lorentz_tensors,
                'Number of propagators' : number_of_propagators,
                'Number of decays' : number_of_decays
                }

    file.update(newcontent)
    meta_name = filename.split('.')[0].strip()
    if not meta_name:
        raise Exception("Invalid filename: '{}', please check".format(filename))
    metadata_name =  meta_name + '.json'
    if create_file:
        with open(metadata_name,'w') as metadata:
            json.dump(file,metadata,indent=2)
        # Check new metadata
        print('Now you can see your the metadata file %s for your new model in the same directory.' %(colored(metadata_name, "magenta")))

    return file, filename, modelname, metadata_name


def metadatamaker_all(all_models):
    base_path = os.getcwd()
    for _path in all_models:
        print("\nChecking Model: " + colored(_path, "magenta") + "\n")
        os.chdir(_path)
        _ = metadatamaker(model_path = os.getcwd())
        os.chdir(base_path)

def is_parent(child, parent):
    if not child.parents:
        return False
    if child.sha == parent.sha:
        return True
    return is_parent(child.parents[0], parent)

        
def uploader(model_path, myrepo, myfork, params):
    
    '''    Generate the metadata for the model   '''
    file, filename, modelname, metadata_name = metadatamaker(model_path, create_file=False)

    '''Check metadata file name'''
    Allmetadata = myrepo.get_contents('Metadata')
    Allmetadataname = [i.name for i in Allmetadata]
    while True:
        if metadata_name in Allmetadataname:
            url = 'https://raw.githubusercontent.com/ThanosWang/UFOMetadata/main/Metadata/'
            url += metadata_name
            metadata = requests.get(url)
            open(metadata_name,'wb').write(metadata.content)
            with open(metadata_name,encoding='utf-8') as metadata:
                file = json.load(metadata)
            DOI = file['Model Doi']
            print('Your metadata file name has been used. Please check the model with DOI: ' + colored(DOI, 'red') + ' in Zenodo.')
            os.remove(metadata_name)
            continuecommand = raw_input('Do you want to continue your upload?' + \
                                    colored(' Yes', 'green') + ' or' + colored(' No', 'red') + ':')
            if continuecommand == 'Yes':
                while True:
                    metadata_name = raw_input('Please rename your metadata file:').replace(' ','_')
                    try:
                        assert metadata_name.endswith('.json')
                        break
                    except:
                        print('Your metadata file name should end with ' + colored('.json', 'red') + '.')
            else:
                sys.exit()
        else:
            break

    '''    Check if  Zenodo token works    '''    
    # Create an empty upload
    headers = {"Content-Type": "application/json"}
    r = requests.post("https://sandbox.zenodo.org/api/deposit/depositions", 
                      params= params,
                      json= {},
                      headers= headers)
    if r.status_code > 400:
        print(colored("Creating deposition entry with Zenodo Failed!", "red"))
        print("Status Code: {}".format(r.status_code))
        raise Exception
    
    # Work with Zenodo API
    
    bucket_url = r.json()["links"]["bucket"]
    Doi = r.json()["metadata"]["prereserve_doi"]["doi"]
    deposition_id = r.json()["id"]

    # Upload new files
    path = model_path + '/%s' %(filename)
    with open(path, 'rb') as fp:
        r = requests.put("%s/%s" %(bucket_url, filename),
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
    r = requests.put('https://sandbox.zenodo.org/api/deposit/depositions/%s' %(deposition_id),
                     params=params,
                     data=json.dumps(data),
                     headers=headers)
    if r.status_code > 400:
        print(colored("Creating deposition entry with Zenodo Failed!", "red"))
        print("Status Code: {}".format(r.status_code))
        raise Exception
    file["Model Doi"] = Doi

    # Use Zenodo page as Homepage if there's no homepage provided
    if len(file['Model Homepage']) == 0:
        file['Model Homepage'] = 'https://doi.org/' + Doi

    with open(metadata_name,'w') as metadata:
        json.dump(file,metadata,indent=2)


    '''    Upload to Github Repository    '''


    # Create new metadata file in the forked repo
    f= open(metadata_name).read()
    GitHub_filename = 'Metadata/' + metadata_name
    myfork.create_file(GitHub_filename, 'Upload metadata for model: {}'.format(metadata_name.replace('.json', '')), f, branch='main')

    if r.status_code == 200:
        print('Now you can go to Zenodo to see your draft at Doi: %s, make some changes, and be ready to publish your model.'%colored(Doi, 'magenta'))
        publish_command = raw_input('Do you want to publish your model and send your new enriched metadata file to GitHub repository UFOMetadata? ' + \
                                    colored(' Yes', 'green') + ' or' + colored(' No', 'red') + ':')
        if publish_command == 'Yes':
            r = requests.post('https://sandbox.zenodo.org/api/deposit/depositions/%s/actions/publish' %(deposition_id),
                              params=params)
            if r.status_code != 202:
                print(colored("Publishing model with Zenodo Failed!", "red"))
                print(r.json())
                raise Exception
            print('Your model has been successfully uploaded to Zenodo with DOI: %s' %(Doi))
            print('You can access your model in Zenodo at: {}'.format(r.json()['links']['record_html']))
            print('\n\n')
        else:
            print("You can publish your model by yourself. Then, please send your enriched metadata file to %s. I will help upload your metadata to GitHub Repository."%colored("thanoswang@163.com/zijun4@illinois.edu", "blue"))
    else:
        print("Your Zenodo upload Draft may have some problems. You can check your Draft on Zenodo and publish it by yourself. Then, please send your enriched metadata file to %s. I will help upload your metadata to GitHub Repository."%colored("thanoswang@163.com/zijun4@illinois.edu", "blue"))


def uploader_all(all_models):
    
    '''    Check if  Zenodo token works    '''
    Zenodo_Access_Token = getpass('Please enter your Zenodo access token:')
    params = {'access_token': Zenodo_Access_Token}
    r = requests.get("https://sandbox.zenodo.org/api/deposit/depositions", params=params)
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
    if not is_parent(myfork.get_branch('main').commit,  repo.get_branch('main').commit): 
        print(colored("Your fork of the UFOMetadata repo is out of sync from the upstream!", "red"))
        print(colored("Please retry after syncing your local fork with upstream", "yellow"))
        raise Exception

    # Now put all models in zenodo and put their metadata in the local fork of metadata repo
    base_path = os.getcwd()
    for _path in all_models:
        print("\nChecking Model: " + colored(_path, "magenta") + "\n")
        os.chdir(_path)
        uploader(model_path = os.getcwd(), myrepo= repo, myfork = myfork, params = params)
        os.chdir(base_path)

    # Pull Request from forked branch to original
    username = g.get_user().login
    body = 'Upload metadata for new model(s)'
    pr = repo.create_pull(title="Upload metadata for a new model", body=body, head='{}:{}'.format(username,'main'), base='{}'.format('main'))
    print('''
    You have successfully upload your model(s) to Zenodo and created a pull request of your new enriched metadate files to GitHub repository''' + colored(' UFOMetadata', 'magenta') + '''. 
    Your pull request to UFOMetadata will be checked by GitHub's CI workflow.
    If your pull request failed or workflow doesn't start, please contact ''' +  colored('thanoswang@163.com/zijun4@illinois.edu' ,'blue')
    )


def newversion(model_path, myrepo, myfork, params, depositions):

    '''    Check for necessary files and their formats    '''
    original_file = os.listdir(model_path)

    assert 'metadata.json' in original_file, \
        'Check if initial "metadata.json" exists: ' + colored('FAILED!', 'red')
    try:
        metadata = open('metadata.json')
        file = json.load(metadata)
    except:
        raise Exception(colored('Check if initial "metadata.json" is correctly formatted: ') + colored('FAILED!', 'red'))
    print('Check if initial "metadata.json" exists and correctly formatted: ' + colored('PASSED!', 'green'))

    '''    Check existing model DOI    '''
    try:
        assert file['Existing Model Doi']
    except:
        raise Exception(colored('"Existing Model Doi" field does not exist in metadata', 'red'))

    try:
        assert 'zenodo' in file['Existing Model Doi']
    except:
        raise Exception(colored('We suggest you to upload your model to Zenodo', 'red'))

    url = 'https://doi.org/' + file['Existing Model Doi']
    existing_model_webpage = requests.get(url)

    try:
        assert existing_model_webpage.status_code < 400
    except:
        raise Exception(colored('We cannot find your model page with your provided existing model doi.', 'red'))


    '''    Generate the metadata for the model   '''
    file, filename, modelname, metadata_name = metadatamaker(model_path, create_file=False)
    
    '''Check metadata file name'''
    Allmetadata = myrepo.get_contents('Metadata')
    Allmetadataname = [i.name for i in Allmetadata]
    while True:
        if metadata_name in Allmetadataname:
            url = 'https://raw.githubusercontent.com/ThanosWang/UFOMetadata/main/Metadata/'
            url += metadata_name
            metadata = requests.get(url)
            open(metadata_name,'wb').write(metadata.content)
            with open(metadata_name,encoding='utf-8') as metadata:
                file = json.load(metadata)
            DOI = file['Model Doi']
            print('Your metadata file name has been used. Please check the model with DOI: ' + colored(DOI, 'red') + ' in Zenodo.')
            os.remove(metadata_name)
            continuecommand = raw_input('Do you want to continue your upload?' + \
                                    colored(' Yes', 'green') + ' or' + colored(' No', 'red') + ':')
            if continuecommand == 'Yes':
                while True:
                    metadata_name = raw_input('Please rename your metadata file:').replace(' ','_')
                    try:
                        assert metadata_name.endswith('.json')
                        break
                    except:
                        print('Your metadata file name should end with ' + colored('.json', 'red') + '.')
            else:
                sys.exit()
        else:
            break

    '''    Find corresponding old version from the concept DOI    '''
    filenames = []
    found_entry = False
    entry = None
    for _entry in depositions:
        if _entry['conceptdoi'].strip().split('.')[-1] == file['Existing Model Doi'].strip().split('.')[-1]:
            found_entry = True
            entry = _entry

    assert found_entry, colored('The zenodo entry corresponding to DOI: {} not found'.format(file['Existing Model Doi']), 'red')

    old_deposition_id = entry['links']['latest'].strip().split('/')[-1]
    _r = requests.get("https://sandbox.zenodo.org/api/records/{}".format(old_deposition_id), params=params)
    for _file in _r.json()['files']:
        link = _file['links']['self'].strip()
        fname = link.split('/')[-1]
        filenames.append(fname)

    print('Your previous upload contains the file(s): %s. Do you want to delete them?' %(colored(','.join(filenames), 'magenta')))

    deletelist = [f.strip() for f in raw_input('Please enter file names you want to delete in your new version, separated names with comma, or Enter ' + colored("No", "red") + ": ").split(',')]


    # Work with new version draft
    '''    Request a  new version    '''
    r = requests.post("https://sandbox.zenodo.org/api/deposit/depositions/%s/actions/newversion"%(old_deposition_id),params=params)
    if r.status_code > 400:
        print(colored("Creating deposition entry with Zenodo Failed!", "red"))
        print("Status Code: {}".format(r.status_code))
        raise Exception

    # Get new deposition id
    new_deposition_id = r.json()['links']['latest_draft'].split('/')[-1]
    
    if deletelist[0] != 'No':
        r = requests.get("https://sandbox.zenodo.org/api/deposit/depositions/%s/files"%(new_deposition_id), params=params)
        if r.status_code > 400:
            print(colored("Could not fetch file details from latest version!", "red"))
            print("Status Code: {}".format(r.status_code))
            raise Exception
        for _file in r.json():
            if _file['filename'] in deletelist:
                _link = _file['links']['self']
                r = requests.delete(_link, params=params)

    headers = {"Content-Type": "application/json"}
    
    r = requests.get('https://sandbox.zenodo.org/api/deposit/depositions/%s' %(new_deposition_id),
                     json={},
                     params=params,
                     headers=headers )

    if r.status_code > 400:
        print(colored("Creating deposition entry with Zenodo Failed!", "red"))
        print("Status Code: {}".format(r.status_code))
        raise Exception

    bucket_url = r.json()["links"]["bucket"]
    Doi = r.json()["metadata"]["prereserve_doi"]["doi"]
    
    # Upload new model files
    path = model_path + '/%s' %(filename)
    with open(path, 'rb') as fp:
        r = requests.put("%s/%s" %(bucket_url, filename),
                         data = fp,
                         params = params)
        if r.status_code > 400:
            print(colored("Putting content to Zenodo Failed!", "red"))
            print("Status Code: {}".format(r.status_code))
            raise Exception

    # Create Zenodo upload metadata
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
            'creators': Author_Information,
            'version': file['Model Version'],
            'publication_date': datetime.datetime.today().strftime('%Y-%m-%d')         
        }
    }

    r = requests.put('https://sandbox.zenodo.org/api/deposit/depositions/%s' %(new_deposition_id),
                     params=params,
                     data=json.dumps(data),
                     headers=headers)
    
    if r.status_code > 400:
        print(colored("Creating deposition entry with Zenodo Failed!", "red"))
        print("Status Code: {}".format(r.status_code))
        raise Exception

    file["Model Doi"] = Doi

    # Use Zenodo page as Homepage if there's no homepage provided
    if len(file['Model Homepage']) == 0:
        file['Model Homepage'] = 'https://doi.org/' + Doi

    '''    Create enriched metadata file    '''
    newmetadataname = metadata_name.split('.')[0] + '.V' + file['Model Version'] + '.json' 

    with open(newmetadataname,'w') as metadata:
        json.dump(file,metadata,indent=2)

    
    '''    Upload to Github Repository    '''

    f= open(newmetadataname).read()
    GitHub_filename = 'Metadata/' + newmetadataname
    myfork.create_file(GitHub_filename, 'Upload metadata for model: {}'.format(metadata_name.replace('.json', '')), f, branch='main')

    if r.status_code == 200:
        print('Now you can go to Zenodo to see your draft at Doi: %s, make some changes, and be ready to publish your model.'%colored(Doi, 'magenta'))
        publish_command = raw_input('Do you want to publish your model and send your new enriched metadata file to GitHub repository UFOMetadata? ' + \
                                    colored(' Yes', 'green') + ' or' + colored(' No', 'red') + ':')
        if publish_command == 'Yes':
            r = requests.post('https://sandbox.zenodo.org/api/deposit/depositions/%s/actions/publish' %(new_deposition_id),
                              params=params)
            if r.status_code != 202:
                print(colored("Publishing model with Zenodo Failed!", "red"))
                print(r.json())
                raise Exception
            print('Your model has been successfully uploaded to Zenodo with DOI: %s' %(Doi))
            print('You can access your model in Zenodo at: {}'.format(r.json()["links"]["record_html"]))
            print('\n\n')
        else:
            print("You can publish your model by yourself. Then, please send your enriched metadata file to %s. I will help upload your metadata to GitHub Repository."%colored("thanoswang@163.com", "blue"))
    else:
        print("Your Zenodo upload Draft may have some problems. You can check your Draft on Zenodo and publish it by yourself. Then, please send your enriched metadata file to %s. I will help upload your metadata to GitHub Repository."%colored("thanoswang@163.com", "blue"))

def newversion_all(all_models):

    '''    Check if  Zenodo token works    '''
    Zenodo_Access_Token = getpass('Please enter your Zenodo access token:')
    params = {'access_token': Zenodo_Access_Token}
    r = requests.get("https://sandbox.zenodo.org/api/deposit/depositions", params=params)
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
    if not is_parent(myfork.get_branch('main').commit,  repo.get_branch('main').commit): 
        print(colored("Your fork of the UFOMetadata repo is out of sync from the upstream!", "red"))
        print(colored("Please retry after syncing your local fork with upstream", "yellow"))
        raise Exception

    # Now put all models in zenodo and put their metadata in the local fork of metadata repo
    base_path = os.getcwd()
    for _path in all_models:
        print("\nChecking Model: " + colored(_path, "magenta") + "\n")
        os.chdir(_path)
        newversion(model_path = os.getcwd(), myrepo= repo, myfork = myfork, params = params, depositions = r.json())
        os.chdir(base_path)

    # Pull Request from forked branch to original
    username = g.get_user().login
    body = 'Upload metadata for new model(s)'
    pr = repo.create_pull(title="Upload metadata for a model's new version", body=body, head='{}:{}'.format(username,'main'), base='{}'.format('main'))
    print('''
    You have successfully uploaded your model(s) to Zenodo and created a pull request of your new enriched metadate files to GitHub repository''' + colored(' UFOMetadata', 'magenta') + '''. 
    Your pull request to UFOMetadata will be checked by GitHub's CI workflow.
    If your pull request failed or workflow doesn't start, please contact ''' +  colored('thanoswang@163.com/zijun4@illinois.edu' ,'blue')
    )



def githubupload(model_path, myrepo, myfork):
    '''    Check for necessary files and their formats    '''
    original_file = os.listdir(model_path)

    assert 'metadata.json' in original_file, \
        'Check if initial "metadata.json" exists: ' + colored('FAILED!', 'red')
    try:
        metadata = open('metadata.json')
        file = json.load(metadata)
    except:
        raise Exception(colored('Check if initial "metadata.json" is correctly formatted: ') + colored('FAILED!', 'red'))
    print('Check if initial "metadata.json" exists and correctly formatted: ' + colored('PASSED!', 'green'))

    '''    Check existing model DOI    '''
    try:
        assert file['Model Doi']
    except:
        raise Exception(colored('"Model Doi" field does not exist in metadata', 'red'))
    
    try:
        assert 'zenodo' in file['Model Doi']
    except:
        raise Exception(colored('We suggest you to upload your model to Zenodo', 'red'))


    url = 'https://doi.org/' + file['Model Doi']
    existing_model_webpage = requests.get(url)
    try:
        assert existing_model_webpage.status_code < 400
    except:
        raise Exception(colored('We cannot find your model page with your provided existing model doi.', 'red'))

    
    '''    Generate the metadata for the model   '''
    file, filename, modelname, metadata_name = metadatamaker(model_path, create_file=False)

    # Use Zenodo page as Homepage if there's no homepage provided
    if len(file['Model Homepage']) == 0:
        file['Model Homepage'] = 'https://doi.org/' + file['Model Doi']

    with open(metadata_name,'w') as metadata:
        json.dump(file,metadata,indent=2)

    '''Check metadata file name'''
    Allmetadata = myrepo.get_contents('Metadata')
    Allmetadataname = [i.name for i in Allmetadata]
    while True:
        if metadata_name in Allmetadataname:
            url = 'https://raw.githubusercontent.com/ThanosWang/UFOMetadata/main/Metadata/'
            url += metadata_name
            metadata = requests.get(url)
            open(metadata_name,'wb').write(metadata.content)
            with open(metadata_name,encoding='utf-8') as metadata:
                file = json.load(metadata)
            DOI = file['Model Doi']
            print('Your metadata file name has been used. Please check the model with DOI: ' + colored(DOI, 'red') + ' in Zenodo.')
            os.remove(metadata_name)
            continuecommand = raw_input('Do you want to continue your upload?' + \
                                    colored(' Yes', 'green') + ' or' + colored(' No', 'red') + ':')
            if continuecommand == 'Yes':
                while True:
                    metadata_name = raw_input('Please rename your metadata file:').replace(' ','_')
                    try:
                        assert metadata_name.endswith('.json')
                        break
                    except:
                        print('Your metadata file name should end with ' + colored('.json', 'red') + '.')
            else:
                sys.exit()
        else:
            break

    '''    Upload to Github Repository    '''


    # Create new metadata file in the forked repo
    f= open(metadata_name).read()
    GitHub_filename = 'Metadata/' + metadata_name
    myfork.create_file(GitHub_filename, 'Upload metadata for model: {}'.format(metadata_name.replace('.json', '')), f, branch='main')


def githubupload_all(all_models):

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
    if not is_parent(myfork.get_branch('main').commit,  repo.get_branch('main').commit): 
        print(colored("Your fork of the UFOMetadata repo is out of sync from the upstream!", "red"))
        print(colored("Please retry after syncing your local fork with upstream", "yellow"))
        raise Exception

    # Now put all models in zenodo and put their metadata in the local fork of metadata repo
    base_path = os.getcwd()
    for _path in all_models:
        print("\nChecking Model: " + colored(_path, "magenta") + "\n")
        os.chdir(_path)
        githubupload(model_path = os.getcwd(), myrepo= repo, myfork = myfork)
        os.chdir(base_path)

    # Pull Request from forked branch to original
    username = g.get_user().login
    body = 'Upload metadata for new model(s)'
    pr = repo.create_pull(title="Upload metadata for a new model", body=body, head='{}:{}'.format(username,'main'), base='{}'.format('main'))
    print('''
    You have successfully upload your model(s) to Zenodo and created a pull request of your new enriched metadate files to GitHub repository''' + colored(' UFOMetadata', 'magenta') + '''. 
    Your pull request to UFOMetadata will be checked by GitHub's CI workflow.
    If your pull request failed or workflow doesn't start, please contact ''' +  colored('thanoswang@163.com/zijun4@illinois.edu' ,'blue')
    )

def UFOUpload(command,modelpath):
    with open(modelpath) as f:
        all_models = [line.strip() for line in f.readlines() if not line.strip().startswith('#')]
    if command == 'Validation check':
        validator_all(all_models=all_models)
    elif command == 'Generate metadata':
        metadatamaker_all(all_models=all_models)
    elif command == 'Upload model':
        uploader_all(all_models=all_models)
    elif command == 'Update new version':
        newversion_all(all_models=all_models)
    elif command == 'Upload metadata to GitHub':
        githubupload_all(all_models=all_models)
    else:
        print('Wrong command! Please choose from ["Validation check", "Generate metadata", "Upload model", "Updata new version", "Upload metadata to GitHub"].')

if __name__ == '__main__':
    FUNCTION_MAP = {'Validation check' : validator_all,
                    'Generate metadata' : metadatamaker_all,
                    'Upload model': uploader_all,
                    'Update new version' : newversion_all,
                    'Upload metadata to GitHub': githubupload_all}

    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=FUNCTION_MAP.keys())
    args = parser.parse_args()
    RunFunction = FUNCTION_MAP[args.command]

    TXT = raw_input('Please enter the path to a text file with the list of all UFO models:')
    with open(TXT) as f:
        all_models = [line.strip() for line in f.readlines() if not line.strip().startswith('#')]
    RunFunction(all_models = all_models)

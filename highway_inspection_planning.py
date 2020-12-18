import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from tabulate import tabulate
import random
import warnings
import os
import copy
import pickle

warnings.filterwarnings("ignore")
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 4)

def import_data(foldername):
    """Function to import all data from the BRON database and convert it from CSV format to Pandas DataFrames.
       To make sure only accidents on highways are included, the filter for HECTOMETER is not empty is performed on accidents.
       Additionaly the filter WEGNUMMER is not empty is performed to filter roadsegments that are part of highways.
       
       The reference files are stored as small conversion Pandas Dataframes and bundled into the ref_files dictionary"""
    txt = ".txt"
    accident_data_foldername = r"Accident data (Ongevallengegevens)"
    network_data_foldername = r"Network data (Netwerkgegevens)"
    ref_files_accidents_foldername = r"Reference files Accidents"
    ref_files_network_foldername = r"Reference files Network"

    accidents_source = pd.read_csv(open(Path(foldername, accident_data_foldername, 'ongevallen.txt'), 'r'), encoding='utf-8').set_index('VKL_NUMMER')
    #Filter only those accidents that happend on the highway
    accidents_source = accidents_source[accidents_source['HECTOMETER'].notna()]
    parties_source = pd.read_csv(Path(foldername, accident_data_foldername, 'partijen.txt')).set_index('PTJ_ID')

    hectointervallen =  pd.read_csv(open(Path(foldername, network_data_foldername, 'hectointervallen.txt'), 'r'), encoding='utf-8')
    hectopunten =  pd.read_csv(open(Path(foldername, network_data_foldername, 'hectopunten.txt'), 'r'), encoding='utf-8')
    junctiehectometrering =  pd.read_csv(open(Path(foldername, network_data_foldername, 'junctiehectometrering.txt'), 'r'), encoding='utf-8')
    juncties =  pd.read_csv(open(Path(foldername, network_data_foldername, 'juncties.txt'), 'r'), encoding='utf-8')
    puntlocaties =  pd.read_csv(open(Path(foldername, network_data_foldername, 'puntlocaties.txt'), 'r'), encoding='utf-8')
    wegvakken =  pd.read_csv(open(Path(foldername, network_data_foldername, 'wegvakken.txt'), 'r'), encoding='utf-8')
    #Filter only those roadsegments which are on the highway
    wegvakken = wegvakken[wegvakken['WEGNUMMER'].notna()]

    ref_file_accidents_names = os.listdir(Path(foldername, ref_files_accidents_foldername))
    ref_file_network_names = os.listdir(Path(foldername, ref_files_network_foldername))

    ref_file_accidents_names.remove('Definitie.txt')
    ref_file_network_names.remove('Definitie.txt')

    ref_files = {}
    for ref_file_name in ref_file_accidents_names:
        ref_file_name = ref_file_name.replace(txt, "")
        ref_files[ref_file_name] = pd.read_csv(open(Path(foldername, ref_files_accidents_foldername, ref_file_name+txt), 'r'), index_col=0)

    for ref_file_name in ref_file_network_names:
        ref_file_name = ref_file_name.replace(txt, "")
        ref_files[ref_file_name] = pd.read_csv(open(Path(foldername, ref_files_network_foldername, ref_file_name+txt), 'r'), index_col=0)
    
    ref_files['intended_movements'] = create_intended_movements_ref_file()
    
    return accidents_source, parties_source, wegvakken, ref_files

def create_intended_movements_ref_file():
    df_intended_movements = pd.DataFrame(
    [[1, 'Oversteken'],
    [2, 'Vooruit'],
    [3, 'Links rijstrook wisselen'],
    [4, 'Stilstand'],
    [5, 'Rechts rijstrook wisselen'],
    [6, 'Linksaf'],
    [7, 'Links omkeren'],
    [8, 'Achteruit'],
    [9, 'Rechts omkeren'],
    [10, 'Rechtsaf'],
    [11, 'Parkeerstand']], columns=['VOORGBEW', 'VOORGBEW_OMS'])
    df_intended_movements = df_intended_movements.set_index('VOORGBEW')
    return df_intended_movements

def save_data(filename, data):
    with open(filename, 'wb') as f:
        pickle.dump(data, f)

def open_data(filename):
    with open(filename, 'rb') as f:
        data = pickle.load(f)
    return data

def load_fields_descriptions(descriptions_filename):
    descriptions_accidents = pd.read_excel(descriptions_filename, sheet_name='accidents')
    descriptions_accidents['Naam'] = descriptions_accidents['Naam'].apply(str.upper)
    descriptions_accidents = descriptions_accidents[['Naam','Definitie NL']]
    descriptions_accidents = descriptions_accidents.set_index('Naam')
    dict_descriptions_accidents = descriptions_accidents['Definitie NL'].to_dict()

    descriptions_roadsegments = pd.read_excel(descriptions_filename, sheet_name='roadsegments')
    descriptions_roadsegments['Naam'] = descriptions_roadsegments['Naam'].apply(str.upper)
    descriptions_roadsegments = descriptions_roadsegments[['Naam','Definitie NL']]
    descriptions_roadsegments = descriptions_roadsegments.set_index('Naam')
    dict_descriptions_roadsegments = descriptions_roadsegments['Definitie NL'].to_dict()

    descriptions_parties = pd.read_excel(descriptions_filename, sheet_name='parties')
    descriptions_parties['Naam'] = descriptions_parties['Naam'].apply(str.upper)
    descriptions_parties = descriptions_parties[['Naam','Definitie NL']]
    descriptions_parties = descriptions_parties.set_index('Naam')
    dict_descriptions_parties = descriptions_parties['Definitie NL'].to_dict()
    
    return dict_descriptions_accidents, dict_descriptions_roadsegments, dict_descriptions_parties

def barplot_parties(parties, ref_files, ylabel, groupby='OTE_ID', ref_file=False, description_var=False):
    import matplotlib.pyplot as plt
    objecttypes_count = parties.groupby(groupby)['VKL_NUMMER'].count()
    objecttypes_count = objecttypes_count.sort_values(ascending=True)
    if ref_file:
        plt.barh(ref_files[ref_file].loc[list(objecttypes_count.index)][description_var].iloc[-15:], objecttypes_count.iloc[-15:], color='gray')
    else:
        plt.barh(objecttypes_count.index, objecttypes_count, color='gray')
    plt.ylabel(ylabel, fontsize=16)
    plt.show()

def barplot_accidents(accidents, ref_files, ylabel, groupby='JAAR_VKL', ref_file=False, description_var=False):
    import matplotlib.pyplot as plt
    objecttypes_count = accidents.groupby(groupby)['WVK_ID'].count()
    objecttypes_count = objecttypes_count.sort_values(ascending=True)
    if ref_file:
        plt.barh(ref_files[ref_file].loc[list(objecttypes_count.index)][description_var].iloc[-15:], objecttypes_count.iloc[-15:], color='gray')
    else:
        plt.barh(objecttypes_count.index, objecttypes_count, color='gray')
    plt.ylabel(ylabel, fontsize=16)
    plt.show()






def retrieve_accident_by_ID(data, accident_ID):
    accidents, parties, roadsegments, ref_files = data
    accident_dict = accidents[accidents.index.astype(str)==str(accident_ID)].T.to_dict()[accident_ID]
    return Accident(accident_dict, accident_ID, data)

def retrieve_road_segment_by_ID(data, roadsegment_ID):
    accidents, parties, roadsegments, ref_files = data    
    roadsegment_dict = find_road_segment(data, roadsegment_ID)
    return Roadsegment(roadsegment_dict, roadsegment_ID, data)
    
def find_road_segment(data, roadsegment_ID):
    accidents, parties, roadsegments, ref_files = data
    wegvak = roadsegments[roadsegments['WVK_ID']==roadsegment_ID] 
    if wegvak.shape[0] > 0:
        return wegvak.iloc[0].to_dict()
    else:
        return {}
    
def find_accidents_on_roadsegment(data, roadsegment_ID):
    accidents, parties, roadsegments, ref_files = data    
    roadsegment = find_road_segment(data, roadsegment_ID)
    accidents_on_roadsegment = accidents[accidents['WVK_ID']==roadsegment_ID].T.to_dict()
    accidents_on_roadsegment_objects = []
    for i, val in enumerate(accidents_on_roadsegment.items()):
        if i < extract_first_n_accidents:
            accident_ID, accident_dict = val
            accidents_on_roadsegment_objects.append(Accident(accident_dict, accident_ID, data, roadsegment=roadsegment))
    return accidents_on_roadsegment_objects

def find_parties(data, accident_ID):
    accidents, parties, roadsegments, ref_files = data    
    parties_involved = parties[parties['VKL_NUMMER'].astype(str)==str(accident_ID)].T.to_dict()
    
    for party_id, party_dict in parties_involved.items():
        parties_involved[party_id]['OTE_OMS'] = determine_value(party_dict['OTE_ID'], ref_files['objecttypes'])
        parties_involved[party_id]['BWG_OMS_1'] = determine_value(party_dict['BWG_ID_1'], ref_files['bewegingen'])
        parties_involved[party_id]['BWG_OMS_2'] = determine_value(party_dict['BWG_ID_2'], ref_files['bewegingen'])
        
    return parties_involved

def determine_value(ID, reference_file):
    try:
        ID = int(ID)
        return reference_file.loc[ID][0]
    except:
        return "NaN"

BOLD = '\033[1m'
END = '\033[0m'

print_all_elements = False
# important_data_elements_accidents = ['REGNUMMER', 'NIVEAUKOP', 'MAXSNELHD', 'WVG_ID', 'WVK_ID']
# important_data_elements_roadsegments = ['WVK_ID', 'WEGBEHSRT', 'WEGNUMMER', 'RIJRICHTNG']
# important_data_elements_parties = ['PTJ_ID', 'OTE_ID', 'OTE_OMS', 'OTE_AN', 'SCHADE', 'UITGPOS1', 'UITGPOS2', 'UITGPOS_AN', 
#                                    'VOORGBEW', 'BWG_ID_1', 'BWG_ID_2', 'BWG_AN']

extract_first_n_accidents = 20

class Accident():
    def __init__(self, dictionary, ID, data, roadsegment=False):
        accidents, parties, roadsegments, ref_files = data
        self.accident = dictionary
        self.accident['WVG_OMS'] = determine_value(self.accident['WVG_ID'], ref_files['wegverhardingen'])
        self.ID = ID
        if roadsegment:
            self.roadsegment = roadsegment
        else:
            self.roadsegment = find_road_segment(data, int(dictionary['WVK_ID']))
        try:
            int_registrationnumber = int(dictionary['REGNUMMER'])
            self.registrationnumber = str(int_registrationnumber)
        except:
            self.registrationnumber = str(dictionary['REGNUMMER'])
        self.parties = find_parties(data, self.ID)
        self.n_parties = len(self.parties)
        self.assesment_task_assess_damage_level()

    def print_accident_details(self, fields_descriptions, fields_to_print):
        dict_descriptions_accidents, dict_descriptions_roadsegments, dict_descriptions_parties = fields_descriptions
        fields_to_print_accidents, fields_to_print_parties, fields_to_print_roadsegments = fields_to_print
        print('------------------------------------------------')
        print(BOLD+f'Accident data {self.ID}'+END)
        for k, v in self.accident.items():
            if print_all_elements or k in fields_to_print_accidents:
                print('   ' + BOLD+f'{k} '+END+f'{dict_descriptions_accidents[k]}: '+BOLD+f'{v}'+END+'\n')
        print('------------------------------------------------')

    def print_parties_details(self, fields_descriptions, fields_to_print):
        dict_descriptions_accidents, dict_descriptions_roadsegments, dict_descriptions_parties = fields_descriptions
        fields_to_print_accidents, fields_to_print_parties, fields_to_print_roadsegments = fields_to_print
        print(BOLD+f'Parties data ({self.n_parties} parties)'+END)
        for i, val in enumerate(self.parties.items()):
            party_id, party_dict = val
            print('    ' +BOLD+f'Party {i+1}: '+END+BOLD+f'{party_id}'+END)
            for k, v in sorted(party_dict.items()):
                if print_all_elements or k in fields_to_print_parties:
                    print('       ' + BOLD+f'{k} '+END+f'{dict_descriptions_parties[k]}: '+BOLD+f'{v}'+END+'\n')
        
        print('------------------------------------------------')
        
    def print_roadsegment_details(self, fields_descriptions, fields_to_print):
        dict_descriptions_accidents, dict_descriptions_roadsegments, dict_descriptions_parties = fields_descriptions
        fields_to_print_accidents, fields_to_print_parties, fields_to_print_roadsegments = fields_to_print
        print(BOLD+'Road segment data'+END)
        for k, v in self.roadsegment.items():
            if print_all_elements or k in fields_to_print_roadsegments:
                print('   ' + BOLD+f'{k} '+END+f'{dict_descriptions_roadsegments[k]}: '+BOLD+f'{v}'+END+'\n')
        print('------------------------------------------------')


    def abstract_involves_element_from_road(self):
        elements_from_road = ['Boom', 'Lichtmast', 'Overig vast object', 'Overig wegmeubilair']
        for party_id, party_dict in self.parties.items():
            if party_dict['OTE_OMS'] in elements_from_road:
                self.involves_element_from_road = True
                return
        self.involves_element_from_road = False
        
    def abstract_involves_heavy_object(self):
        self.involves_heavy_object = False
        heavy_objects = ['Vrachtauto', 'Trekker', 'Trekker met oplegger', 'Landbouwvoertuig']
        for party_id, party_dict in self.parties.items():
            if party_dict['OTE_OMS'] in heavy_objects:
                self.involves_heavy_object = True
                return
        self.involves_heavy_object = False

    def abstract_determine_scale_accident(self):
        if self.n_parties < 3:
            self.scale_accident = 'small'        
        elif self.n_parties == 3 or self.n_parties == 4:
            self.scale_accident = 'medium'   
        else:
            self.scale_accident = 'large'   
            
    def abstract_involves_damaging_movement(self):
        damaging_movements = ['Kantelen', 'Over de kop', 'Uitrollen']
        self.involves_damaging_movement = False
        for party_id, party_dict in self.parties.items():
            if party_dict['BWG_OMS_1'] in damaging_movements or party_dict['BWG_OMS_2'] in damaging_movements:
                self.involves_damaging_movement = True
                return
        self.involves_damaging_movement = False
    
    def abstract_determine_happend_on_highway(self):
        if self.accident['HECTOMETER'] != 'nan':
            self.happend_on_highway = True
        else:
            self.happend_on_highway = False
    
    def abstract(self, print_log=True):
        self.abstract_determine_happend_on_highway()
        self.abstract_involves_element_from_road()
        self.abstract_involves_heavy_object()
        self.abstract_determine_scale_accident()
        self.involves_heavy_object_and_road_element = (self.involves_heavy_object and self.involves_element_from_road) 
        self.abstract_involves_damaging_movement()

    def print_abstractions(self):
        print('The following abstractions were made:')
        if self.happend_on_highway:
            print(f'  -  Accident happend on the highway')
        else:
            print(f'  -  Accident did not happen on the highway')

        if self.involves_element_from_road:
            print(f'  -  Accident involves an element from the road')
        else:
            print(f'  -  Accident does not involve an element from the road')

        if self.involves_heavy_object:
            print(f'  -  Accident involves a heavy object')
        else:
            print(f'  -  Accident does not involve any heavy objects')

        print(f'  -  Accident is a {self.scale_accident} size scaled accident')
    
    def specify_norms(self):
        self.norms = ['involves_damaging_movement', 'involves_element_from_road', 'involves_heavy_object', 'involves_heavy_object_and_road_element']
        self.n_norms = len(self.norms)
        
    def select_norm(self):
        norm = self.norms.pop(random.randint(0,len(self.norms)-1))
        if len(self.norms) == 0:
            self.norms_to_evaluate = False
            self.assesment_complete = True 
        return norm
    
    def evaluate_norm(self, norm):
        if norm == 'involves_element_from_road':
            return self.involves_element_from_road
        elif norm == 'involves_heavy_object':
            return self.involves_heavy_object
        elif norm == 'involves_heavy_object_and_road_element':
            return self.involves_heavy_object_and_road_element
        elif norm == 'involves_damaging_movement':
            return self.involves_damaging_movement
                   
    def match_norm_value(self, norm, norm_value):
        if norm == 'involves_element_from_road':
            if norm_value==True:
                self.expected_damage_level = 'medium'
        elif norm == 'involves_heavy_object':
            if norm_value==True:
                self.expected_damage_level = 'medium'
        elif norm == 'involves_heavy_object_and_road_element':
            if norm_value==True:
                self.expected_damage_level = 'high'
                self.assesment_complete = True
        elif norm == 'involves_damaging_movement':
            if norm_value==True:
                self.expected_damage_level = 'high'
                self.assesment_complete = True

    def assesment_task_assess_damage_level(self, print_log=False):
        if print_log:
            print('------------------------------------------------')
            print(BOLD+'Start assesment task to: determine expected damage level'+END)
        self.abstract()    
        if print_log:
            self.print_abstractions()
        self.specify_norms()
        if print_log:
            print('Specified norms:')
            for norm in self.norms:
                print(f'   - {norm}')
        self.expected_damage_level = 'undecided'
        self.norms_to_evaluate=True
        self.assesment_complete=False
        if print_log:
            print('Start norms evaluation')
        norm_i = 1
        while self.norms_to_evaluate and not self.assesment_complete:
            norm = self.select_norm()
            if print_log:
                print(f' -  Selected norm {norm_i} {norm} to evaluate')
            norm_value = self.evaluate_norm(norm)
            if print_log:
                print(f'    -  Obtained norm value {norm_value}')
            self.match_norm_value(norm, norm_value)
            if print_log:
                print(f'    -  Matched norm value to make decision: {self.expected_damage_level}')
            norm_i+=1
        if print_log:
            print(BOLD+f'Result of assesment task: Expected damage level is {self.expected_damage_level}'+END)
            print('------------------------------------------------')

class Roadsegment():
    def __init__(self, roadsegment_dict, roadsegment_ID, data):
        self.roadsegment = roadsegment_dict
        self.ID = roadsegment_ID
        
        self.accidents = find_accidents_on_roadsegment(data, self.ID)
        self.n_accidents = len(self.accidents)
    
        self.print_all_elements = False
    
    def print_roadsegment_details(self, fields_descriptions, fields_to_print):
        dict_descriptions_accidents, dict_descriptions_roadsegments, dict_descriptions_parties = fields_descriptions
        fields_to_print_accidents, fields_to_print_parties, fields_to_print_roadsegments = fields_to_print
        print(BOLD+'Road segment data'+END)
        for k, v in self.roadsegment.items():
            if self.print_all_elements or k in fields_to_print_roadsegments:
                print('   ' + BOLD+f'{k} '+END+f'{dict_descriptions_roadsegments[k]}: '+BOLD+f'{v}'+END+'\n')
        print('------------------------------------------------')
        
    def print_accidents_on_roadsegment_details(self, fields_descriptions, fields_to_print):
        dict_descriptions_accidents, dict_descriptions_roadsegments, dict_descriptions_parties = fields_descriptions
        fields_to_print_accidents, fields_to_print_parties, fields_to_print_roadsegments = fields_to_print
        print(BOLD+f'Accidents data ({self.n_accidents} accidents)'+END)
        accidents_print = []
        for accident in self.accidents:
            accidents_print.append([accident.ID, accident.expected_damage_level, accident.n_parties, accident.scale_accident, accident.involves_damaging_movement, accident.involves_element_from_road, accident.involves_heavy_object])
        df_accidents_print = pd.DataFrame(accidents_print)
        df_accidents_print.columns = ['ID', r'Expected damage level', r'N parties', 'Scale', r'Damaging movement', r'Element from road', r'Heavy objects']
        print(tabulate(df_accidents_print, headers='keys'))
        print('------------------------------------------------')

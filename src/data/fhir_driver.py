import argparse
import json
import re
import sys
from datetime import datetime
import xml.etree.ElementTree as ET

sys.path.append('../..')

import src.data.logical_forms_to_fhir_queries as lffq
import src.data.mapped_codes as mc

# Current mapped codes file, keeps updating for newly encountered CUIs
path_to_mapped_file = '../../data/mapped_cui_codes.txt'
# Manually annotated code mappings
path_to_mapped_file_manual = '../../data/mapped_cui_codes-manual.txt'
# Code mappings from additional concept annotations done for the questions present in both the datasets (ICU and FHIR)
path_to_mapped_file_meta = '../../data/mapped_cui_codes-meta.txt'


parser = argparse.ArgumentParser(description='fhir driver options')
parser.add_argument("-lf_xml_str", "--logical_form_xml_str", type=str, required=True, help="logical form in xml format")
parser.add_argument("-output_file", "--output_file", type=str, required=True, help="file path to write the output")
parser.add_argument("-api_key", "--umls_api_key", type=str, required=True, dest="api_key",
                    help="enter api key from your UTS Profile")
parser.add_argument("-pat_id", "--patient_id", type=str, required=True, dest="pat_id", help="enter patient ID")
parser.add_argument("-c_time", "--current_time", type=datetime.fromisoformat, default=None, dest="current_time",
                    help="enter the current time in ISO format to consider while fetching an answer; "
                         "leave blank to use the time now")
parser.add_argument("-v", "--version", dest="version", type=str, default="current", help="enter version example-2015AA")

args = parser.parse_args()

xml_str = args.logical_form_xml_str
xml_str = xml_str.strip()
out_file = args.output_file
api_key = args.api_key
pat_id = args.pat_id
current_time = args.current_time
version = args.version

print('Logical form xml:')
print('--------------------------------------------------')
print(xml_str)
print('--------------------------------------------------')

with open(path_to_mapped_file) as infile:
    current_mapped_cui_information = json.load(infile)

cui_added = False
cuis_in_logical_form_xml = re.findall('\\b\\d+\\b', xml_str)
if len(cuis_in_logical_form_xml) > 0:
    for cui in cuis_in_logical_form_xml:
        if len(cui) > 6 and cui not in current_mapped_cui_information:
            print('Fetching information for cui: {}'.format(cui))
            dict_codes = mc.get_umls_code_mappings(cui, api_key, version)
            current_mapped_cui_information[cui] = dict_codes
            cui_added = True

with open(path_to_mapped_file_manual) as infile:
    manual_mapped_cui_information = json.load(infile)

for cui, manual_details in manual_mapped_cui_information.items():
    try:
        current_details = current_mapped_cui_information[cui]
        for vocab, manual_codes_str in manual_details.items():
            try:
                current_codes_set = set(current_details[vocab].split(','))
                manual_codes_set = set(manual_codes_str.split(','))
                if current_codes_set == manual_codes_set:
                    continue
                current_codes_set = current_codes_set.union(manual_codes_set)
                current_codes_str = ','.join(current_codes_set)
                current_details[vocab] = current_codes_str
                cui_added = True
            except KeyError:
                current_details[vocab] = manual_codes_str
    except KeyError:
        current_mapped_cui_information[cui] = manual_details
        cui_added = True

with open(path_to_mapped_file_meta) as infile:
    meta_mapped_cui_information = json.load(infile)

for new_cui, existing_cuis in meta_mapped_cui_information.items():
    if new_cui not in current_mapped_cui_information:
        print('Fetching information for cui: {}'.format(new_cui))
        dict_codes = mc.get_umls_code_mappings(new_cui, api_key, version)
        current_mapped_cui_information[new_cui] = dict_codes
        cui_added = True
    new_cui_details = current_mapped_cui_information.get(new_cui, {})
    for exist_cui in existing_cuis:
        if exist_cui not in current_mapped_cui_information:
            print('Fetching information for cui: {}'.format(exist_cui))
            dict_codes = mc.get_umls_code_mappings(exist_cui, api_key, version)
            current_mapped_cui_information[exist_cui] = dict_codes
            cui_added = True
        exist_cui_details = current_mapped_cui_information.get(exist_cui, {})
        umls_mappings_str = new_cui_details.get('UMLS', '')
        umls_mappings_set = set(x for x in umls_mappings_str.split(',') if x != '')
        if exist_cui not in umls_mappings_set:
            umls_mappings_set.add(exist_cui)
            new_cui_details['UMLS'] = ','.join(umls_mappings_set)
            cui_added = True
        for vocab, codes_str in exist_cui_details.items():
            if vocab == 'semantic_type':
                continue
            if vocab not in new_cui_details:
                new_cui_details[vocab] = codes_str
                cui_added = True
            else:
                new_cui_codes_str = new_cui_details[vocab]
                new_cui_codes_set = set(new_cui_codes_str.split(','))
                exist_cui_codes_set = set(codes_str.split(','))
                if not exist_cui_codes_set.issubset(new_cui_codes_set):
                    new_cui_codes_set = new_cui_codes_set.union(exist_cui_codes_set)
                    new_cui_details[vocab] = ','.join(new_cui_codes_set)
                    cui_added = True
    current_mapped_cui_information[new_cui] = new_cui_details


if cui_added:
    print('CUI added to mapped_cui_codes.txt file')
    current_mapped_cui_info_str = json.dumps(current_mapped_cui_information, indent=2)
    with open(path_to_mapped_file, 'w') as outfile:
        outfile.write(current_mapped_cui_info_str)

root_node = ET.fromstring(xml_str)

resp = lffq.get_answer_for_logical_form(root_node, path_to_mapped_file, pat_id, current_time)
print(json.dumps(resp, sort_keys=True, indent=4))

print('Writing to output file: ' + out_file)
json.dump(resp, open(out_file, 'w'), sort_keys=True, indent=4)

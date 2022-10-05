from src.data.Authentication import Authentication
import argparse
import json
import requests
import xml.etree.ElementTree as ET
import re
from collections import defaultdict

uri = 'https://uts-ws.nlm.nih.gov'


def get_umls_code_mappings(cui, apikey, version='current'):
    # Authentication
    AuthClient = Authentication(apikey)
    tgt = AuthClient.gettgt()

    # Calling the UMLS server for Retrieving UMLS Concept Information
    concept_info_endpoint = '{}/rest/content/{}/CUI/C{}'.format(uri, str(version), cui)
    query_to_get_name = {'ticket': AuthClient.getst(tgt)}
    r = requests.get(concept_info_endpoint, params=query_to_get_name)
    print('Response from UMLS Concept Information: {}'.format(r))
    r.encoding = 'utf-8'
    items = json.loads(r.text)
    result = items['result']
    name = result['name']
    semantic_type = result['semanticTypes'][0]['name']

    # Calling the UMLS server for Retrieving UMLS Atoms
    concept_atoms_endpoint = concept_info_endpoint + '/atoms'
    query_to_get_codes = {
        'ticket': AuthClient.getst(tgt),
        'includeObsolete': True,
        'includeSuppressible': True
    }
    r = requests.get(concept_atoms_endpoint, params=query_to_get_codes)
    print('Response from UMLS Atoms: {}'.format(r))
    code_dict = defaultdict(set)
    if r.status_code == 200:
        r.encoding = 'utf-8'
        items = json.loads(r.text)
        result_list = items['result']
        result_list = [x for x in result_list if 'rootSource' in x]
        for code_item in result_list:
            code_source = str(code_item['rootSource'])
            code_dict[code_source].add(str(code_item['code']).rsplit('/', 1)[1])
    elif r.status_code == 404:
        # In case of an error, leaving the code dictionary empty
        print('UMLS Atoms API response status code is 404')
    else:
        print(r.text)
        raise RuntimeError('Call to UMLS Atoms failed with status code {}'.format(r.status_code))

    code_dict = {k: ','.join(v) for k, v in code_dict.items()}
    code_dict['semantic_type'] = semantic_type

    return code_dict


def main():
    parser = argparse.ArgumentParser(description='process user given parameters')
    parser.add_argument('-xml', '--xml file', required=True, dest='input', help='path to annotated xml file')
    parser.add_argument('-k', '--apikey', required=True, dest='apikey', help='enter api key from your UTS Profile')
    parser.add_argument('-v', '--version', required=False, dest='version', default='current',
                        help='enter version example-2015AA')
    parser.add_argument('-output', '--outputfile', required=True, dest='outputfile',
                        help='enter a name for your output file')
    args = parser.parse_args()
    path_to_input = args.input
    apikey = args.apikey
    version = args.version
    outputfile = args.outputfile

    of = open(outputfile, 'w')

    tree = ET.parse(path_to_input)
    root = tree.getroot()
    items = root.findall('Item')
    cui_to_other_codes_mapping_dict = {}
    for item in items:
        print('Id: ' + item.get('id'))
        questions = item.findall('Question')
        for question in questions:
            logical_form = question.find('LogicalForm')
            logical_form_text = logical_form.text
            cuis_in_logical_form = re.findall('\\b\\d+\\b', logical_form_text)
            if len(cuis_in_logical_form) > 0:
                for cui in cuis_in_logical_form:
                    if len(cui) > 6:
                        if cui not in cui_to_other_codes_mapping_dict:
                            dict_codes = get_umls_code_mappings(cui, apikey, version)
                            cui_to_other_codes_mapping_dict[cui] = dict_codes

    of.write(json.dumps(cui_to_other_codes_mapping_dict))
    of.close()


if __name__ == '__main__':
    main()

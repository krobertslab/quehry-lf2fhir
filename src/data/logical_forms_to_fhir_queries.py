import json
import xml.etree.ElementTree as ET
import src.data.time_utils as time_utils
import src.data.fhir_client as fhir_client
import src.data.manipulation_utils as mnp_utils
import src.data.settings as settings
import argparse
import re
import calendar

month_list = [x.lower() for x in list(calendar.month_name) + list(calendar.month_abbr) if x != '']
month_name_to_number = {month.lower(): index for index, month in enumerate(calendar.month_name) if month}
month_abbr_to_number = {month.lower(): index for index, month in enumerate(calendar.month_abbr) if month}
month_to_number = {**month_name_to_number, **month_abbr_to_number}


def construct_semtype_resource_mapping(set_semantic_types):
    dict_object_types = {}
    for st in set_semantic_types:
        if 'Function' in st or 'Abnormality' in st or st == 'Qualitative Concept':
            dict_object_types[st] = 'Condition/Observation/AllergyIntolerance/Procedure'
        elif 'Disease' in st or 'Syndrome' in st or 'Symptom' in st or 'Injury' in st or 'Virus' in st:
            dict_object_types[st] = 'Condition/AllergyIntolerance/CarePlan'
        elif 'Finding' in st or 'Dysfunction' in st:
            dict_object_types[st] = 'Observation/Condition/AllergyIntolerance/Procedure/Encounter'
        elif 'Body Location' in st or 'Body Part' in st or st == 'Laboratory or Test Result':
            dict_object_types[st] = 'Observation'
        elif 'Substance' in st or st == 'Inorganic Chemical' or st == 'Organic Chemical':
            dict_object_types[st] = 'MedicationAdministration/MedicationStatement/Observation'
        elif st == 'Amino Acid, Peptide, or Protein':
            dict_object_types[st] = 'MedicationAdministration/MedicationStatement/MedicationOrder/Observation/Procedure'
        elif 'Professional' in st:
            dict_object_types[st] = 'Encounter'
        elif st == 'Drug Delivery Device':
            dict_object_types[st] = 'MedicationOrder'
        elif 'Device' in st or st == 'Manufactured Object':
            dict_object_types[st] = 'Procedure'
        elif 'Procedure' in st:
            dict_object_types[st] = 'MedicationAdministration/MedicationStatement/Procedure/CarePlan/Encounter'
        elif 'Material' in st or st == 'Antibiotic' or st == 'Food':
            dict_object_types[st] = 'MedicationAdministration/MedicationStatement'
        elif 'Activity' in st:
            dict_object_types[st] = 'Procedure/Observation/Condition/AllergyIntolerance/CarePlan/Encounter'
        elif 'Attribute' in st or st == 'Organism':
            dict_object_types[st] = 'Observation/Procedure/DiagnosticReport'
        elif st == 'Temporal Concept':
            dict_object_types[st] = 'Observation'
        elif st == 'Immunologic Factor':
            dict_object_types[st] = 'Immunization'
        elif st == 'Clinical Drug':
            dict_object_types[st] = 'MedicationOrder/Immunization'
        elif st == 'Intellectual Product':
            dict_object_types[st] = 'CarePlan/Observation'
        else:
            # If the semantic type is none of the above, fetch everything
            dict_object_types[st] = \
                'Observation/Condition/Procedure/MedicationAdministration/MedicationStatement/MedicationOrder/' \
                'Immunization/CarePlan/AllergyIntolerance/DiagnosticReport/Encounter'

    # Add a default mapping for null values
    dict_object_types[None] = ''

    return dict_object_types


def get_corresponding_resource_cui_time(has_logical_func, mapped_cui_information, dict_object_types):
    # Extracting only the arguments delimited by commas in the 'has_' function
    arguments_part = has_logical_func.split('(')[1].split(')')[0]
    arguments = arguments_part.split(',')
    if len(arguments) == 4:
        cui = arguments[1].strip()
        time = arguments[2].strip()
        level = arguments[3].strip()
    elif len(arguments) == 2:
        print("Not implemented functions which take 2 inputs")
        return None, None, None, None
    else:
        if arguments[1].strip() == 'admission' or arguments[1].strip() == 'discharge' or arguments[1].strip() == \
                'readmission':
            task_to_check = arguments[1].strip()
            fhir_res = 'Encounter'
            time = arguments[2].strip()
            level = 'NA'
            return fhir_res, task_to_check, time, level
        else:
            cui = arguments[1].strip()
            time = arguments[2].strip()
            level = 'NA'

    if cui == "*":
        print("Not implemented for CUI = *")
        return None, None, None, None

    if cui not in mapped_cui_information:
        print('cui "{}" not present in mapped_cui_information'.format(cui))
        concept_type = None
    else:
        concept_type = mapped_cui_information[cui]['semantic_type']
    fhir_res = dict_object_types[concept_type]
    return fhir_res, cui, time, level


def switch_build_root_func():
    switcher = {
        'delta': mnp_utils.get_answer_delta_func,
        'latest': mnp_utils.get_answer_latest_func,
        'earliest': mnp_utils.get_answer_earliest_func,
        'count': mnp_utils.get_answer_count_func,
        'location': mnp_utils.get_answer_loc_func,
        'dose': mnp_utils.get_answer_dose_func,
        'duration': mnp_utils.get_answer_duration_func,
        'time': mnp_utils.get_answer_time_func,
        'max': mnp_utils.get_answer_max_or_min_func,
        'min': mnp_utils.get_answer_max_or_min_func,
        'is_positive': mnp_utils.get_answer_is_positive_or_negative_func,
        'is_negative': mnp_utils.get_answer_is_positive_or_negative_func,
        'positive': mnp_utils.get_answer_is_positive_or_negative_func,  # Test for id="159"
        'negative': mnp_utils.get_answer_is_positive_or_negative_func,
        'is_normal': mnp_utils.get_answer_is_normal_func,
        'is_high': mnp_utils.get_answer_is_high_func,
        'and': mnp_utils.get_answer_and_operation,
        'sum': mnp_utils.get_answer_sum_func,
        'is_increasing': mnp_utils.get_answer_is_increasing_or_decreasing_func,
        'is_decreasing': mnp_utils.get_answer_is_increasing_or_decreasing_func,
        'trend': mnp_utils.get_answer_trend_func,
        'reason': mnp_utils.get_answer_reason_func,
        'is_healed': mnp_utils.get_answer_is_healed_func,
    }
    return switcher


def find_codes_specific_voc(voc, mapped_info, corresponding_code_list):
    if voc in mapped_info:
        snomed_codes = mapped_info[voc]
        if ',' in snomed_codes:
            codes = snomed_codes.split(',')
            corresponding_code_list.extend(codes)
        else:
            corresponding_code_list.append(snomed_codes)
    return corresponding_code_list


def find_corresponding_codes(cui, mapped_cui_information):
    corresponding_code_list = []
    corresponding_code_list.append(cui)
    mapped_info = mapped_cui_information[cui]
    voc_list = ['SNOMEDCT_US', 'ICD9CM', 'ICD10CM', 'ICD10', 'RXNORM', 'LNC', 'CPT', 'CHV', 'CVX', 'UMLS']
    for voc in voc_list:
        corresponding_code_list = find_codes_specific_voc(voc, mapped_info, corresponding_code_list)
    return corresponding_code_list


def get_current_visit_data(resource, set_answers, active_encounters_list, referred_resource_data=None):
    active_encounters_id = []
    for encounter in active_encounters_list:
        active_encounters_id.append(encounter['encounter_id'])
    try:
        ref_encounter = resource['resource']['encounter']['reference']
        encounter_id = ref_encounter.split('/')[1]
        if encounter_id in active_encounters_id:
            if resource['resource']['resourceType'] == 'Condition':
                set_answers = fhir_client.get_condition_visit_data(resource, set_answers, encounter_id)
            elif resource['resource']['resourceType'] == 'Observation':
                set_answers = fhir_client.get_observation_visit_data(resource, set_answers, encounter_id,
                                                                     active_encounters_list)
            elif resource['resource']['resourceType'] == 'Procedure':
                set_answers = fhir_client.get_procedure_visit_data(resource, set_answers)
            elif resource['resource']['resourceType'] == 'MedicationAdministration':
                set_answers = fhir_client.get_med_administration_visit_data(resource, set_answers,
                                                                            referred_resource_data)
            elif resource['resource']['resourceType'] == 'Immunization':
                set_answers = fhir_client.get_immunization_visit_data(resource, set_answers, encounter_id)
            elif resource['resource']['resourceType'] == 'CarePlan':
                set_answers = fhir_client.get_careplan_visit_data(resource, set_answers, encounter_id)
            elif resource['resource']['resourceType'] == 'AllergyIntolerance':
                set_answers = fhir_client.get_allergyintolerance_visit_data(resource, set_answers, encounter_id)
            elif resource['resource']['resourceType'] == 'DiagnosticReport':
                set_answers = fhir_client.get_diagnosticreport_visit_data(resource, set_answers, encounter_id)
            else:
                print('Unhandled resource type:\n ', resource['resource']['resourceType'])
    except KeyError:
        print('No encounter/reference information is found for a particular entry')
    return set_answers


def populate_more_encounter_details(resource, encounter_id, encounter_start_date, encounter_end_date, location):
    # Stores admit source, discharge, and whether readmitted
    hospitalization_info = []
    try:
        hospitalization = resource['resource']['hospitalization']

        try:
            admit = hospitalization['admitSource']['coding'][0]['display']
            hospitalization_info.append(admit)
        except KeyError:
            hospitalization_info.append('NA')
        try:
            discharge = hospitalization['dischargeDisposition']['coding'][0]['display']
            hospitalization_info.append(discharge)
        except KeyError:
            hospitalization_info.append('NA')
        try:
            readmission = hospitalization['reAdmission']['coding'][0]['display']
            hospitalization_info.append(readmission)
        except KeyError:
            hospitalization_info.append('NA')
    except KeyError:
        hospitalization_info.append('NA')
        hospitalization_info.append('NA')
        hospitalization_info.append('NA')

    # Stores participant information (Practitioner/RelatedPerson)
    try:
        participants = resource['resource']['participant']
        participants_info = []
        for participant in participants:
            each_participant_info = []
            try:
                period = participant['period']
                try:
                    start = period['start']
                except KeyError:
                    start = 'NA'
                try:
                    end = period['end']
                except KeyError:
                    end = 'NA'
            except KeyError:
                start = 'NA'
                end = 'NA'
            try:
                individual = participant['individual']
                try:
                    reference_participant = individual['reference']
                    participant_type = reference_participant.split('/')[0]
                    participant_id = reference_participant.split('/')[1]
                except KeyError:
                    participant_type = 'NA'
                    participant_id = 'NA'
            except KeyError:
                participant_type = 'NA'
                participant_id = 'NA'
            each_participant_info.append(start)
            each_participant_info.append(end)
            each_participant_info.append(participant_type)
            each_participant_info.append(participant_id)
            participants_info.append(each_participant_info)
    except KeyError:
        participants_info = []

    try:
        encounter_codes = []
        encounter_types = resource['resource']['type']
        for e_type in encounter_types:
            encounter_codings = e_type['coding']
            for e_coding in encounter_codings:
                encounter_codes.append(e_coding['code'])
    except KeyError:
        encounter_codes = []

    reasons = []
    try:
        reason_obj = resource['resource']['reason']
        for reason in reason_obj:
            reason_name = reason['coding'][0]['display']
            reasons.append(reason_name)
    except KeyError:
        pass

    encounter_details = {}
    if encounter_id != 'None':
        encounter_details = {'encounter_id': encounter_id, 'encounter_start_date': encounter_start_date,
                             'hospitalization_info': hospitalization_info,
                             'encounter_end_date': encounter_end_date, 'encounter_location': location,
                             'encounter_participants': participants_info, 'encounter_codes': encounter_codes,
                             'reason': reasons, 'admsn_dschg_readmsn': 'code'}
    return encounter_details


def get_all_active_inpatient_encounters(pat_id):
    active_encounters_list = []
    json_fhir_encounter_data = fhir_client.get_fhir_response('Encounter', pat_id)
    if json_fhir_encounter_data is None:
        return active_encounters_list
    entry = json_fhir_encounter_data['entry']
    for resource in entry:
        # Filtering the inpatient encounters
        try:
            encounter_class = resource['resource']['class']
            if encounter_class != 'inpatient':
                continue
        except KeyError:
            continue
        try:
            status = resource['resource']['status']
            if status == 'in-progress':
                try:
                    encounter_id = resource['resource']['id']
                except KeyError:
                    encounter_id = 'None'
                try:
                    encounter_period = resource['resource']['period']
                    try:
                        encounter_start_date = encounter_period['start']
                    except KeyError:
                        encounter_start_date = 'None'
                    try:
                        encounter_end_date = encounter_period['end']
                    except KeyError:
                        encounter_end_date = 'None'
                except KeyError:
                    encounter_start_date = 'None'
                    encounter_end_date = 'None'
                # Verify location reference
                try:
                    location = resource['resource']['location'][0]['location']['display']
                except KeyError:
                    location = 'None'

                # Get some more information about the encounter
                encounter_details = populate_more_encounter_details(
                    resource, encounter_id, encounter_start_date, encounter_end_date, location)
                active_encounters_list.append(encounter_details)
        except KeyError:
            try:
                encounter_id = resource['resource']['id']
            except KeyError:
                encounter_id = 'None'
            try:
                location = resource['resource']['location'][0]['location']['display']
            except KeyError:
                location = 'None'
            try:
                encounter_period = resource['resource']['period']
                try:
                    encounter_end_date = encounter_period['end']
                except KeyError:
                    try:
                        encounter_start_date = encounter_period['start']
                    except KeyError:
                        encounter_start_date = 'None'
                    encounter_details = populate_more_encounter_details(resource, encounter_id, encounter_start_date,
                                                                        'None', location)
                    active_encounters_list.append(encounter_details)
            except KeyError:
                print('Encounter status could not be determined')
    return active_encounters_list


def get_all_encounters(pat_id):
    encounters_list = []
    json_fhir_encounter_data = fhir_client.get_fhir_response('Encounter', pat_id)
    if json_fhir_encounter_data is None:
        return encounters_list
    entry = json_fhir_encounter_data['entry']
    for resource in entry:
        try:
            encounter_id = resource['resource']['id']
        except KeyError:
            encounter_id = 'None'
        try:
            encounter_period = resource['resource']['period']
            try:
                encounter_start_date = encounter_period['start']
            except KeyError:
                encounter_start_date = 'None'
            try:
                encounter_end_date = encounter_period['end']
            except KeyError:
                encounter_end_date = 'None'
        except KeyError:
            encounter_start_date = 'None'
            encounter_end_date = 'None'
        # Verify location reference
        try:
            location = resource['resource']['location'][0]['location']['display']
        except KeyError:
            location = 'None'

        # Get some more information about the encounter
        encounter_details = populate_more_encounter_details(
            resource, encounter_id, encounter_start_date, encounter_end_date, location)
        encounters_list.append(encounter_details)
    return encounters_list


def get_sorted_list_times_device_info(set_answers):
    list_times_device_info = []
    for i in set_answers:
        if i['performed_start_date'] != 'NA':
            performed_start_date = time_utils.get_final_date_time(i['performed_start_date'])
            device_act_code = i['device_action_code']
            device_id = i['device_id']
            list_times_device_info.append({'time': performed_start_date, 'item_info': i,
                                           'device_action_code': device_act_code, 'device_id': device_id})
    sorted_list_times_device_info = sorted(list_times_device_info, key=lambda k: k['time'],
                                           reverse=True)
    # Creating a dictionary to store all the action codes for each of the unique device ids for a patient
    # Multiple device ids representing the same device code might be associated with a patient
    device_list = {}
    for item in sorted_list_times_device_info:
        if item['device_id'] in device_list.keys():
            device_list[item['device_id']].append({'item_info': item['item_info'],
                                                   'device_action_code': item['device_action_code']})
        else:
            dict_action_codes_and_resource_info = {'item_info': item['item_info'],
                                                   'device_action_code': item['device_action_code']}
            device_list[item['device_id']] = [dict_action_codes_and_resource_info]
    return device_list


def get_answer_set(json_data_fhir, set_answers, cui, time, level, fhir_resource, mapped_cui_information, pat_id):
    corresponding_codes_cui = find_corresponding_codes(cui, mapped_cui_information)
    entry = json_data_fhir['entry']
    if time == 'visit' or time == 'status' or time == 'pmh' or time == 'history':
        if time in {'status', 'history', 'pmh'}:
            # Includes all the encounters irrespective of class and status
            active_encounters_list = get_all_encounters(pat_id)
        else:
            # Get all the active encounters for this patient
            active_encounters_list = get_all_active_inpatient_encounters(pat_id)

        for resource in entry:
            if resource['resource']['resourceType'] == 'Condition':
                codes_found_in_fhir = []
                codes_found_in_fhir_details = resource['resource']['code']['coding']
                for code_json in codes_found_in_fhir_details:
                    codes_found_in_fhir.append(code_json['code'])
                if any(c in corresponding_codes_cui for c in codes_found_in_fhir):
                    if level == 'NA':
                        try:
                            verification_status = resource['resource']['verificationStatus']
                            if verification_status == 'confirmed':
                                set_answers = get_current_visit_data(resource, set_answers, active_encounters_list)
                            else:
                                print('Verification status of the condition was not confirmed')
                        except KeyError:
                            print('Verification status of the condition was not confirmed')
                            set_answers = set_answers
                    else:
                        try:
                            verification_status = resource['resource']['verificationStatus']
                            if verification_status == 'confirmed' or verification_status == 'provisional':
                                set_answers = get_current_visit_data(resource, set_answers, active_encounters_list)
                            else:
                                print('Verification status of the condition was neither confirmed nor provisional')
                        except KeyError:
                            print('Verification status of the condition was neither confirmed nor provisional')
                            set_answers = set_answers
            elif resource['resource']['resourceType'] == 'Observation':
                codes_found_in_fhir = []
                codes_found_in_fhir_details = resource['resource']['code']['coding']
                for code_json in codes_found_in_fhir_details:
                    codes_found_in_fhir.append(code_json['code'])
                if any(c in corresponding_codes_cui for c in codes_found_in_fhir):
                    if level == 'NA':
                        try:
                            status = resource['resource']['status']
                            if status == 'final' or status == 'amended':
                                if 'encounter' in resource['resource']:
                                    set_answers = get_current_visit_data(resource, set_answers, active_encounters_list)
                                else:
                                    set_answers = fhir_client.get_observation_visit_data(resource, set_answers,
                                                                                         encounter_id=None,
                                                                                         active_encounters_list=[])
                            else:
                                print('Observation status was not final')
                        except KeyError:
                            print('Observation status was not final')
                            set_answers = set_answers
                    else:
                        try:
                            status = resource['resource']['status']
                            if status == 'final' or status == 'preliminary' or status == 'amended':
                                if 'encounter' in resource['resource']:
                                    set_answers = get_current_visit_data(resource, set_answers, active_encounters_list)
                                else:
                                    set_answers = fhir_client.get_observation_visit_data(resource, set_answers,
                                                                                         encounter_id=None,
                                                                                         active_encounters_list=[])
                            else:
                                print('Observation status was neither confirmed nor preliminary')
                        except KeyError:
                            print('Observation status was neither confirmed nor preliminary')
                            set_answers = set_answers
            elif resource['resource']['resourceType'] == 'MedicationStatement':
                # Create Medication resource and get the medication codes in fhir from the medication that is referenced
                try:
                    referred_med = resource['resource']['medicationReference']['reference']
                    referred_med_id = referred_med.split('/')[1]
                    # Call function that retrieves medication data from fhir
                    medication_json_data = fhir_client.get_fhir_response_id('Medication', referred_med_id)
                    try:
                        med_name = medication_json_data['code']['coding'][0]['display']
                    except KeyError:
                        med_name = 'NA'
                    codes_found_in_fhir = []
                    codes_found_in_fhir_details = medication_json_data['code']['coding']
                    for code_json in codes_found_in_fhir_details:
                        codes_found_in_fhir.append(code_json['code'])
                    if any(c in corresponding_codes_cui for c in codes_found_in_fhir):
                        set_answers = fhir_client.get_medication_data(resource, set_answers, med_name,
                                                                      referred_med_id, medication_json_data)
                except KeyError:
                    continue
            elif resource['resource']['resourceType'] == 'MedicationOrder':
                try:
                    codes_found_in_fhir_details = resource['resource']['medicationCodeableConcept']['coding']
                    codes_found_in_fhir = [coding['code'] for coding in codes_found_in_fhir_details]
                    if any(c in corresponding_codes_cui for c in codes_found_in_fhir):
                        set_answers = fhir_client.get_medication_data(resource, set_answers)
                except KeyError:
                    continue
            elif resource['resource']['resourceType'] == 'Procedure':
                codes_found_in_fhir = []
                device_codes_found_in_fhir = []
                codes_found_in_fhir_details = resource['resource']['code']['coding']
                for code_json in codes_found_in_fhir_details:
                    codes_found_in_fhir.append(code_json['code'])
                if 'focalDevice' in resource['resource']:
                    # Considering the first focal device
                    focal_device = resource['resource']['focalDevice'][0]
                    device_action_code = focal_device['action']['coding'][0]['code']
                    device_reference = focal_device['manipulated']['reference']
                    device_id = device_reference.split('/')[1]
                    device_json_data = fhir_client.get_fhir_response_id('Device', device_id)
                    device_codes_in_fhir_details = device_json_data['type']['coding']
                    for device_code in device_codes_in_fhir_details:
                        device_codes_found_in_fhir.append(device_code['code'])
                if any(c in corresponding_codes_cui for c in codes_found_in_fhir):
                    set_answers = get_current_visit_data(resource, set_answers, active_encounters_list)
                elif any(c in corresponding_codes_cui for c in device_codes_found_in_fhir):
                    settings.device_found = True
                    set_answers = get_current_visit_data(resource, set_answers, active_encounters_list)

            elif resource['resource']['resourceType'] == 'MedicationAdministration':
                try:
                    referred_med = resource['resource']['medicationReference']['reference']
                    referred_med_id = referred_med.split('/')[1]
                    medication_json_data = fhir_client.get_fhir_response_id('Medication', referred_med_id)
                    codes_found_in_fhir = []
                    codes_found_in_fhir_details = medication_json_data['code']['coding']
                    for code_json in codes_found_in_fhir_details:
                        codes_found_in_fhir.append(code_json['code'])
                    if any(c in corresponding_codes_cui for c in codes_found_in_fhir):
                        set_answers = get_current_visit_data(resource, set_answers, active_encounters_list,
                                                             medication_json_data)
                except KeyError:
                    continue
            elif resource['resource']['resourceType'] == 'Immunization':
                codes_found_in_fhir = []
                codes_found_in_fhir_details = resource['resource']['vaccineCode']['coding']
                for code_json in codes_found_in_fhir_details:
                    codes_found_in_fhir.append(code_json['code'])
                if any(c in corresponding_codes_cui for c in codes_found_in_fhir):
                    set_answers = get_current_visit_data(resource, set_answers, active_encounters_list)
            elif resource['resource']['resourceType'] == 'CarePlan':
                codes_found_in_fhir = []
                codes_found_in_fhir_category_details = resource['resource']['category']
                for category_details in codes_found_in_fhir_category_details:
                    codes_found_in_fhir_details = category_details['coding']
                    for code_json in codes_found_in_fhir_details:
                        codes_found_in_fhir.append(code_json['code'])
                if any(c in corresponding_codes_cui for c in codes_found_in_fhir):
                    if 'encounter' in resource['resource']:
                        set_answers = get_current_visit_data(resource, set_answers, active_encounters_list)
                    else:
                        set_answers = fhir_client.get_careplan_visit_data(resource, set_answers, encounter_id=None)
            elif resource['resource']['resourceType'] == 'AllergyIntolerance':
                codes_found_in_fhir = []
                codes_found_in_fhir_details = resource['resource']['substance']['coding']
                for code_json in codes_found_in_fhir_details:
                    codes_found_in_fhir.append(code_json['code'])
                if any(c in corresponding_codes_cui for c in codes_found_in_fhir):
                    if 'encounter' in resource['resource']:
                        set_answers = get_current_visit_data(resource, set_answers, active_encounters_list)
                    else:
                        set_answers = fhir_client.get_allergyintolerance_visit_data(resource, set_answers,
                                                                                    encounter_id=None)
            elif resource['resource']['resourceType'] == 'DiagnosticReport':
                codes_found_in_fhir = []
                codes_found_in_fhir_details = resource['resource']['code']['coding']
                for code_json in codes_found_in_fhir_details:
                    codes_found_in_fhir.append(code_json['code'])
                if any(c in corresponding_codes_cui for c in codes_found_in_fhir):
                    if 'encounter' in resource['resource']:
                        set_answers = get_current_visit_data(resource, set_answers, active_encounters_list)
                    else:
                        set_answers = fhir_client.get_diagnosticreport_visit_data(resource, set_answers,
                                                                                  encounter_id=None)
            else:
                print('Unhandled resource type:\n ', resource['resource']['resourceType'])

        if time == 'visit' or time == 'history':
            if len(set_answers) == 0:
                return None, fhir_resource
            else:
                if time == 'visit':
                    if settings.device_found is True:
                        set_updated_answers = []
                        device_list = get_sorted_list_times_device_info(set_answers)
                        device_ids_already_checked = []
                        for ans in set_answers:
                            if (ans['device_id'] in device_list.keys()) and (
                                    ans['device_id'] not in device_ids_already_checked):
                                device_ids_already_checked.append(ans['device_id'])
                                action_codes_resource_sorted_by_time = device_list[ans['device_id']]
                                latest_item = action_codes_resource_sorted_by_time[0]['item_info']
                                set_updated_answers.append(latest_item)
                        set_answers = list(set_updated_answers)
                    return set_answers, fhir_resource
                else:
                    return set_answers, fhir_resource

        elif time == 'pmh':
            if len(set_answers) > 0:
                if fhir_resource == 'Condition':
                    set_new_answers = []
                    for ans in set_answers:
                        encounter_id = ans['encounter_id']
                        json_fhir_en_data = fhir_client.get_fhir_response_id('Encounter', encounter_id)
                        if 'hospitalization' in json_fhir_en_data:
                            try:
                                admit = json_fhir_en_data['hospitalization']['admitSource']['coding'][0]['display']
                            except KeyError:
                                admit = 'NA'
                            try:
                                readmission = \
                                    json_fhir_en_data['hospitalization']['reAdmission']['coding'][0]['display']
                            except KeyError:
                                readmission = 'NA'
                        else:
                            admit = 'NA'
                            readmission = 'NA'
                        if 'period' in json_fhir_en_data:
                            try:
                                encounter_period = json_fhir_en_data['period']
                                try:
                                    encounter_start_date = encounter_period['start']
                                except KeyError:
                                    encounter_start_date = 'None'
                            except KeyError:
                                encounter_start_date = 'None'

                        # Considering the active conditions
                        if ans['problem_status'] == 'active':
                            if encounter_start_date != 'None' and ans['onset_datetime'] != 'None':
                                en_start_date_time = time_utils.get_final_date_time(encounter_start_date)
                                prob_onset_time = time_utils.get_final_date_time(ans['onset_datetime'])

                                if prob_onset_time <= en_start_date_time:
                                    set_new_answers.append(ans)
                        elif ans['problem_status'] == 'None':
                            if ans['onset_datetime'] != 'None' and ans['abatement_datetime'] == 'None':
                                if encounter_start_date != 'None' and ans['onset_datetime'] != 'None':
                                    en_start_date_time = time_utils.get_final_date_time(encounter_start_date)
                                    prob_onset_time = time_utils.get_final_date_time(ans['onset_datetime'])

                                    if prob_onset_time <= en_start_date_time:
                                        set_new_answers.append(ans)

                    if len(set_new_answers) == 0:
                        return None, fhir_resource
                    else:
                        set_answers = list(set_new_answers)
                        return set_answers, fhir_resource
                elif fhir_resource in {'Immunization', 'MedicationOrder', 'CarePlan', 'AllergyIntolerance',
                                       'DiagnosticReport', 'Observation', 'Procedure'}:
                    return set_answers, fhir_resource
                else:
                    return None, None
            else:
                return None, fhir_resource
        elif time == 'status':
            if settings.device_found is False:
                if fhir_resource == 'Condition':
                    set_new_answers = []
                    for i in set_answers:
                        status_problem = i['problem_status']
                        if status_problem == 'active':
                            set_new_answers.append(i)
                        elif status_problem == 'None':
                            if i['onset_datetime'] != 'None' and i['abatement_datetime'] == 'None':
                                set_new_answers.append(i)
                        else:
                            continue
                    set_answers = list(set_new_answers)
                elif fhir_resource in {'AllergyIntolerance', 'CarePlan'}:
                    set_new_answers = []
                    for i in set_answers:
                        status_problem = i['status']
                        if status_problem == 'active':
                            set_new_answers.append(i)
                    set_answers = list(set_new_answers)
                elif fhir_resource == 'Observation':
                    # Considering all the observations having final or amended status
                    if len(set_answers) == 0:
                        return None, fhir_resource
                    else:
                        return set_answers, fhir_resource
                elif fhir_resource == 'Procedure':
                    if any(ans['diagnostic_report_found'] == 'Yes' for ans in set_answers):
                        set_answers = set_answers
                    else:
                        set_new_answers = []
                        for ans in set_answers:
                            proc_status = ans['proc_status']
                            if proc_status == 'in-progress':
                                set_new_answers.append(ans)
                            elif proc_status == 'NA':
                                if ans['performed_start_date'] != 'NA' and ans['performed_end_date'] == 'NA':
                                    set_new_answers.append(ans)
                        set_answers = list(set_new_answers)

                elif fhir_resource == 'MedicationStatement':
                    set_new_answers = []
                    for i in set_answers:
                        if (i['med_status'] == 'active') or (i['effective_start_date'] != 'NA' and
                                                             i['effective_end_date'] == 'NA'):
                            set_new_answers.append(i)
                        else:
                            continue
                    set_answers = list(set_new_answers)
                elif fhir_resource == 'MedicationAdministration':
                    set_new_answers = []
                    for i in set_answers:
                        if (i['med_administration_status'] == 'in-progress') or (i['med_admin_start_date'] != 'NA' and
                                                                                 i['med_admin_end_date'] == 'NA'):
                            set_new_answers.append(i)
                        else:
                            continue
                    set_answers = list(set_new_answers)
                if len(set_answers) == 0:
                    return None, fhir_resource
                else:
                    return set_answers, fhir_resource
            else:
                set_new_answers = []
                device_list = get_sorted_list_times_device_info(set_answers)
                device_ids_already_checked = []
                for ans in set_answers:
                    if ans['device_id'] in device_list.keys() and \
                            ans['device_id'] not in device_ids_already_checked:
                        device_ids_already_checked.append(ans['device_id'])
                        action_codes_and_resource_sorted_by_time = device_list[ans['device_id']]
                        latest_action_code = action_codes_and_resource_sorted_by_time[0]['device_action_code']
                        if latest_action_code == 'explanted':
                            print('No device with the id is currently implanted.')
                        else:
                            set_new_answers.append(ans)

                set_answers = list(set_new_answers)
                if len(set_answers) == 0:
                    return None, fhir_resource
                else:
                    return set_answers, fhir_resource
        else:
            print('Invalid temporal term: ' + time)
            return None, None
    else:
        if time == 'plan':
            print("Not implemented for time plan except those related to discharge")
        else:
            print("Not implemented for time: {0}".format(time))
        return None, None


def get_answer_set_encounter(set_answers, cui, time, level, fhir_resource, pat_id):
    # Get all the active encounters for this patient
    if time == 'history':
        active_encounters_list = get_all_encounters(pat_id)
    else:
        active_encounters_list = get_all_active_inpatient_encounters(pat_id)
    # Will be executed for event
    set_answers_admission = []
    set_answers_redmission = []
    set_answers_discharge = []

    if len(active_encounters_list) > 0:
        for en in active_encounters_list:
            hospitalization_details = en['hospitalization_info']
            final_encounter_details = {'encounter_id': en['encounter_id'],
                                       'encounter_start_date': en['encounter_start_date'],
                                       'admit_source': hospitalization_details[0],
                                       'discharge_disposition': hospitalization_details[1],
                                       'readmission': hospitalization_details[2],
                                       'encounter_end_date': en['encounter_end_date'],
                                       'encounter_location': en['encounter_location'],
                                       'admsn_dschg_readmsn': cui}

            # If hospitalization information is present
            set_answers_discharge.append(final_encounter_details)
            set_answers_admission.append(final_encounter_details)
            if final_encounter_details['readmission'] != 'NA':
                set_answers_redmission.append(final_encounter_details)
    if cui == 'admission':
        set_answers = list(set_answers_admission)
    elif cui == 'readmission':
        set_answers = list(set_answers_redmission)
    else:
        set_answers = list(set_answers_discharge)

    return set_answers, fhir_resource


def get_answer_set_participants(set_answers, cui, time, level, fhir_resource, mapped_cui_information, pat_id):
    set_answers_practitioners = []
    set_answers_related_persons = []
    corresponding_codes_cui = find_corresponding_codes(cui, mapped_cui_information)
    if time == 'history':
        active_encounters_list = get_all_encounters(pat_id)
    else:
        active_encounters_list = get_all_active_inpatient_encounters(pat_id)
    if len(active_encounters_list) == 0:
        return set_answers_practitioners, set_answers_related_persons, fhir_resource
    for en in active_encounters_list:
        if len(en['encounter_participants']) > 0:
            for ps in en['encounter_participants']:
                if ps[2] == 'Practitioner':
                    practitioner_json_data = fhir_client.get_fhir_response_id(ps[2], ps[3])
                    codes_found_in_fhir = []
                    # Considering no practitioner with the given id is present in FHIR
                    if practitioner_json_data is not None:
                        if 'practitionerRole' in practitioner_json_data:
                            roles = practitioner_json_data['practitionerRole']
                            for role in roles:
                                if 'specialty' in role:
                                    specialties = role['specialty']
                                    for specialty in specialties:
                                        if 'coding' in specialty:
                                            codes = specialty['coding']
                                            for code in codes:
                                                codes_found_in_fhir.append(code['code'])
                        if any(c in corresponding_codes_cui for c in codes_found_in_fhir):
                            # Changing the FHIR resource from 'Encounter' to 'Practitioner'
                            fhir_resource = 'Practitioner'
                            set_answers_practitioners = fhir_client.get_practitioner_data(set_answers_practitioners,
                                                                                          practitioner_json_data, ps,
                                                                                          en)
                # Adding all the related persons in the final set
                else:
                    fhir_resource = 'RelatedPerson'
                    related_person_details = {'participant_start': ps[0], 'participant_end': ps[1],
                                              'participant_type': ps[2], 'participant_id': ps[3]}
                    set_answers_related_persons.append(related_person_details)
    return set_answers_practitioners, set_answers_related_persons, fhir_resource


def get_answer_set_encounters_with_code(cui, time, fhir_resource, mapped_cui_information, pat_id):
    if time == 'history':
        candidate_encounters_list = get_all_encounters(pat_id)
    elif time == 'pmh':
        all_encounters_list = get_all_encounters(pat_id)
        active_encounters_list = get_all_active_inpatient_encounters(pat_id)
        active_encounter_ids = set([en['encounter_id'] for en in active_encounters_list])
        candidate_encounters_list = [en for en in all_encounters_list if en['encounter_id'] not in active_encounter_ids]
    else:
        candidate_encounters_list = get_all_active_inpatient_encounters(pat_id)

    filtered_encounters_list = []
    corresponding_codes_cui = find_corresponding_codes(cui, mapped_cui_information)
    for en in candidate_encounters_list:
        codes_found_in_fhir = en['encounter_codes']
        if any(c in corresponding_codes_cui for c in codes_found_in_fhir):
            filtered_encounters_list.append(en)
            fhir_resource = 'Encounter'

    return filtered_encounters_list, fhir_resource


def get_fhir_json_data_answer_set(set_answers, cui, time, level, fhir_resource, mapped_cui_information, pat_id):
    if cui not in {'admission', 'discharge', 'readmission'}:
        if fhir_resource != 'Encounter':
            json_data_fhir = fhir_client.get_fhir_response(fhir_resource, pat_id)
            if json_data_fhir is not None:
                set_answers, fhir_resource = get_answer_set(json_data_fhir, set_answers, cui, time, level,
                                                        fhir_resource, mapped_cui_information, pat_id)
            else:
                return None, fhir_resource
        else:
            set_answers_practitioners, set_answers_related_persons, fhir_resource = get_answer_set_participants(
                set_answers, cui, time, level, fhir_resource, mapped_cui_information, pat_id)
            # For doctor
            if fhir_resource == 'Practitioner':
                set_answers = list(set_answers_practitioners)
            # For has_event
            elif fhir_resource == 'RelatedPerson':
                set_answers = list(set_answers_related_persons)
            # Case where Encounter resource(s) may be requested
            else:
                set_encounters, fhir_resource = get_answer_set_encounters_with_code(
                    cui, time, fhir_resource, mapped_cui_information, pat_id)
                if len(set_encounters) > 0:
                    set_answers = list(set_encounters)

    # If admission, discharge or readmission related question is asked
    else:
        set_answers, fhir_resource = get_answer_set_encounter(set_answers, cui, time, level, fhir_resource, pat_id)
    return set_answers, fhir_resource


def get_answer(root_node, set_answers, mapped_cui_information, dict_object_types, pat_id):
    root_func = root_node.get('value')
    fhir_resource = None
    if 'has_' in root_func:
        fhir_resource, cui, time, level = get_corresponding_resource_cui_time(root_func, mapped_cui_information,
                                                                              dict_object_types)
        if fhir_resource is None:
            return None, None
        else:
            # Checking if multiple FHIR resources need to be called for the question initially
            if '/' in fhir_resource:
                fhir_resources = fhir_resource.split('/')
                for (ind, fhir_resource) in enumerate(fhir_resources):
                    set_answers, fhir_resource = get_fhir_json_data_answer_set(
                        set_answers, cui, time, level, fhir_resource, mapped_cui_information, pat_id)
                    # If for the first fhir resource, answer is found, then no need to query the second resource
                    if set_answers is not None:
                        break
                    else:
                        # Re-initializing for searching the next resource
                        if ind < (len(fhir_resources) - 1):
                            set_answers = []
                        continue
            else:
                set_answers, fhir_resource = get_fhir_json_data_answer_set(set_answers, cui, time, level, fhir_resource,
                                                                           mapped_cui_information, pat_id)

            return set_answers, fhir_resource

    elif 'time_within' in root_func:
        set_ans = []
        time_to_check = root_func.split('(')[1].split(')')[0].split(',')[1].replace('`', '').replace("'", "").strip()
        if time_to_check == 'overnight' or time_to_check == 'last night':
            st, ed = time_utils.get_overnight_time_range()
            set_ans.append(st)
            set_ans.append(ed)
            return set_ans, None
        elif 'hours' in time_to_check:
            num_hrs = time_to_check.split(' ')[-2]
            st, ed = time_utils.get_last_n_hrs_time_range(num_hrs)
            set_ans.append(st)
            set_ans.append(ed)
            return set_ans, None
        elif time_to_check == 'since last night':
            st, ed = time_utils.get_since_last_night_time_range()
            set_ans.append(st)
            set_ans.append(ed)
            return set_ans, None
        elif time_to_check == 'yesterday':
            st, ed = time_utils.get_yesterday_time_range()
            set_ans.append(st)
            set_ans.append(ed)
            return set_ans, None
        elif time_to_check == 'today' or time_to_check == 'since today':
            st, ed = time_utils.get_today_time_range()
            set_ans.append(st)
            set_ans.append(ed)
            return set_ans, None
        elif time_to_check == 'last week' or time_to_check == 'the last week' or time_to_check == 'past week' \
                or time_to_check == 'the past week':
            st, ed = time_utils.get_last_week_time_range()
            set_ans.append(st)
            set_ans.append(ed)
            return set_ans, None
        elif time_to_check == 'this morning':
            st, ed = time_utils.get_morning_time_range()
            set_ans.append(st)
            set_ans.append(ed)
            return set_ans, None
        elif re.match(r'^(after|since) ([12][0-9]{3})$', time_to_check):
            time_components = re.match(r'^(after|since) ([12][0-9]{3})$', time_to_check)
            year = int(time_components.group(2))
            st, ed = time_utils.get_since_year_range(year)
            set_ans.append(st)
            set_ans.append(ed)
            return set_ans, None
        elif re.match(r'^(in) ([12][0-9]{3})$', time_to_check):
            time_components = re.match(r'^(in) ([12][0-9]{3})$', time_to_check)
            year = int(time_components.group(2))
            st, ed = time_utils.get_in_year_range(year)
            set_ans.append(st)
            set_ans.append(ed)
            return set_ans, None
        elif re.match(r'^(in) (__MONTH__) ([12][0-9]{3})$'.replace('__MONTH__', '|'.join(month_list)), time_to_check):
            time_components = re.match(r'^(in) (__MONTH__) ([12][0-9]{3})$'.replace('__MONTH__', '|'.join(month_list)),
                                       time_to_check)
            month = time_components.group(2)
            month_num = month_to_number[month]
            year = int(time_components.group(3))
            st, ed = time_utils.get_in_month_year_range(month_num, year)
            set_ans.append(st)
            set_ans.append(ed)
            return set_ans, None
        elif re.match(r'^(in the )*(last|past|previous|since last|since past) (\d{0,})( )*(year|years|decade|decades)$',
                      time_to_check):
            time_components = re.match(
                r'^(in the )*(last|past|previous|since last|since past) (\d{0,})( )*(year|years|decade|decades)$',
                time_to_check)
            num_units_match = time_components.group(3)
            if num_units_match == '':
                num_units = 1
            else:
                num_units = int(num_units_match)
            unit_type = time_components.group(5)
            # converting everything in terms of years
            if unit_type in {'decade', 'decades'}:
                num_units *= 12
            st, ed = time_utils.get_last_n_years(num_units)
            set_ans.append(st)
            set_ans.append(ed)
            return set_ans, None
        elif time_to_check == 'this year':
            st, ed = time_utils.get_this_year_range()
            set_ans.append(st)
            set_ans.append(ed)
            return set_ans, None
    elif 'at_location' in root_func:
        if len(root_node.getchildren()) == 0:
            location_to_check = root_func.split(',', 1)[1].strip()
            location_to_check = location_to_check[1:-2]
            return location_to_check, 'at_location'
        else:
            location_to_check = root_node.getchildren()[1].get('value')
            answer_to_match = get_answer(
                root_node.getchildren()[0], set_answers, mapped_cui_information, dict_object_types, pat_id)
            if location_to_check == answer_to_match:
                return 'Yes', None
            else:
                return 'No', None
    elif 'greater_than' in root_func:
        value_to_check_with_unit = \
            root_func.split('(')[1].split(')')[0].split(',')[1].replace('`', '').replace("'", "").strip()
        value_to_check = re.findall('\\b\\d+\\b', value_to_check_with_unit)
        # Taking the only number present in the list of numbers containing a particular value
        value_to_check = float(value_to_check[0])
        return value_to_check, 'greater_than'

    elif 'less_than' in root_func:
        value_to_check_with_unit = \
            root_func.split('(')[1].split(')')[0].split(',')[1].replace('`', '').replace("'", "").strip()
        value_to_check = re.findall('\\b\\d+\\b', value_to_check_with_unit)
        value_to_check = float(value_to_check[0])
        return value_to_check, 'less_than'

    elif root_func == 'is_normal(x)':
        return 'Nothing to check', 'is_normal'

    elif root_func == 'is_healed(x)':
        return 'Nothing to check', 'is_healed'

    elif root_func == 'is_large(x)':
        return 'Nothing to check', 'is_large'

    elif root_func == 'is_significant(x)':
        return 'Nothing to check', 'is_significant'

    elif root_func == 'is_positive(x)':
        return 'Nothing to check', 'is_positive'

    elif root_func == 'is_negative(x)':
        return 'Nothing to check', 'is_negative'

    elif root_func == 'is_serious(x)':
        return 'Nothing to check', 'is_serious'

    if len(root_node.getchildren()) == 1:
        for child_node in root_node.getchildren():
            set_answers, fhir_resource = get_answer(
                child_node, set_answers, mapped_cui_information, dict_object_types, pat_id)
            if set_answers is None:
                return set_answers, fhir_resource
    else:
        list_set_answers_children = []
        for child_node in root_node.getchildren():
            set_answers, fhir_resource = get_answer(
                child_node, set_answers, mapped_cui_information, dict_object_types, pat_id)
            if set_answers is None:
                return set_answers, fhir_resource
            list_set_answers_children.append(set_answers)
            list_set_answers_children.append(fhir_resource)

    # Done processing all the children
    func_to_call = switcher.get(root_func)
    # Check if a separate function exists for the root node
    if func_to_call is not None:
        if root_func == 'and':
            return func_to_call(list_set_answers_children)
        elif root_func == 'max' or root_func == 'min' or root_func == 'is_positive' or root_func == 'positive' or \
                root_func == 'is_negative' or root_func == 'is_increasing' or root_func == 'is_decreasing':
            return func_to_call(set_answers, fhir_resource, root_func)
        else:
            return func_to_call(set_answers, fhir_resource)
    elif root_func != 'lambda x' and root_func != 'lambda x.' and root_func != 'summary':
        # Looking for any cui
        num_list = re.findall('\\b\\d+\\b', root_func)
        if root_func == 'x':
            print("'after' function is not implemented yet.")
        elif len(num_list) > 0:
            for num in num_list:
                if len(num) > 6:
                    print("Searching for a specific code on some result / function 'is_result' is not implemented yet.")
        else:
            print('Function: {0} is not implemented yet'.format(root_func))
        return None, None

    return set_answers, fhir_resource


def get_response_object(status, message, answer, fhir_resource):
    return {'status': status, 'message': message, 'answer': answer, 'resource': fhir_resource}


def get_formatted_response(answer, fhir_resource):
    if answer is None and fhir_resource is None:
        message = 'Some function(s) is/are not implemented'
        status = 'ERROR'
    elif answer is None and fhir_resource is not None:
        message = 'No answers were retrieved from FHIR or associated encounter was not active or encounter ' \
                  'information was not found on FHIR'
        status = 'OK'
    else:
        message = 'Answer found'
        status = 'OK'

    response = get_response_object(status, message, answer, fhir_resource)
    return response


def parse_xml_file(xml_file_to_read, mapped_cui_information, dict_object_types, pat_id):
    tree = ET.parse(xml_file_to_read)
    root = tree.getroot()
    items = root.findall('Item')
    for item in items:
        id = item.get('id')
        print("Item id: " + id)
        questions = item.findall('Question')
        for question in questions:
            settings.init()
            set_answers = []
            logical_form_tree = question.find('LogicalFormTree')
            root_node = logical_form_tree.find('Node')
            answer, fhir_resource = get_answer(
                root_node, set_answers, mapped_cui_information, dict_object_types, pat_id)

            response = get_formatted_response(answer, fhir_resource)
            print(response)


def main():
    parser = argparse.ArgumentParser(description='process user given parameters')
    parser.add_argument("-codes_file", "--mapped_codes_file", required=True, dest="mapped_codes_file",
                        help="path to mapped codes file")
    parser.add_argument("-ann_file", "--annotated_file", required=True, dest="xml_input",
                        help="path to annotated xml file")
    parser.add_argument("-pat_id", "--patient_id", required=True, dest="pat_id",
                        help="Id of patient against which the fhir calls are made")
    args = parser.parse_args()
    path_to_mapped_file = args.mapped_codes_file
    xml_file_to_read = args.xml_input
    pat_id = args.pat_id
    m_f = open(path_to_mapped_file, 'r')
    mapped_cui_information = json.load(m_f)
    mapped_cui_information = dict(mapped_cui_information)
    mapped_codes_smtype = mapped_cui_information.values()
    set_semantic_types = set()
    for mapped_info_cui in mapped_codes_smtype:
        semantic_type = mapped_info_cui['semantic_type']
        set_semantic_types.add(semantic_type)
    dict_object_types = construct_semtype_resource_mapping(set_semantic_types)
    parse_xml_file(xml_file_to_read, mapped_cui_information, dict_object_types, pat_id)


def get_answer_for_logical_form(root_node, path_to_mapped_file, pat_id, current_time=None):
    settings.init()

    # Use the given current_time, if available, else datetime.now() is used.
    if current_time is not None:
        time_utils.current_time = current_time

    with open(path_to_mapped_file, 'r') as m_f:
        mapped_cui_information = json.load(m_f)

    mapped_cui_information = dict(mapped_cui_information)
    mapped_codes_smtype = mapped_cui_information.values()
    set_semantic_types = set()
    for mapped_info_cui in mapped_codes_smtype:
        semantic_type = mapped_info_cui['semantic_type']
        set_semantic_types.add(semantic_type)
    dict_object_types = construct_semtype_resource_mapping(set_semantic_types)

    set_answers = []
    answer, fhir_resource = get_answer(root_node, set_answers, mapped_cui_information, dict_object_types, pat_id)

    response = get_formatted_response(answer, fhir_resource)
    return response


switcher = switch_build_root_func()
if __name__ == '__main__':
    main()

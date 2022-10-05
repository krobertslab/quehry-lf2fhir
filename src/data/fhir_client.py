from datetime import datetime
import src.data.time_utils as time_utils
import requests


def get_fhir_response_id(resource, id):
    query_url = 'http://127.0.0.1:3001/' + resource
    query_url_id = query_url + '/' + id
    parameters = {'_offset': 0, '_count': 500}
    req = requests.get(query_url_id, params=parameters)
    if req.status_code == 200:
        resource_data = req.json()
        return resource_data


def get_fhir_response(fhir_resource, pat_id):
    query_url = 'http://127.0.0.1:3001/' + fhir_resource
    # parameters = {'patient': '5b8723c67bfdf14a0c3ce7bc'}
    parameters = {'patient': pat_id, '_offset': 0, '_count': 500}
    r = requests.get(query_url, params=parameters)
    if r.status_code == 200:
        data = r.json()
        if data['total'] > 0:
            return data
        else:
            print('No entry exists for the requested FHIR resource: {0}'.format(fhir_resource))
            return None
    else:
        print('Status not found 200 while requesting the FHIR resource: {0}'.format(fhir_resource))
        return None


def get_enocunter_fhir_response(pat_id):
    query_url = 'http://127.0.0.1:3001/' + 'Encounter'
    parameters = {'patient': pat_id, '_offset': 0, '_count': 500}
    req = requests.get(query_url, params=parameters)
    if req.status_code == 200:
        encounter_data = req.json()
        return encounter_data


def get_condition_visit_data(resource, set_answers, encounter_id):
    try:
        onset_datetime = str(resource['resource']['onsetDateTime'])
    except KeyError:
        onset_datetime = 'None'
    try:
        abatement_datetime = str(resource['resource']['abatementDateTime'])
    except KeyError:
        abatement_datetime = 'None'
    try:
        problem_name = resource['resource']['code']['coding'][0]['display']
    except KeyError:
        problem_name = 'None'
    try:
        body_site = resource['resource']['bodySite'][0]['coding'][0]['display']
    except KeyError:
        body_site = 'None'
    try:
        status = resource['resource']['clinicalStatus']
    except KeyError:
        status = 'None'
    try:
        resource_id = resource['resource']['id']
    except KeyError:
        resource_id = 'None'
    try:
        code = resource['resource']['code']['coding'][0]['code']
    except KeyError:
        code = 'None'
    try:
        severity = resource['resource']['severity']['coding'][0]['display']
    except KeyError:
        severity = 'None'

    condition_details = {'onset_datetime': onset_datetime, 'abatement_datetime': abatement_datetime,
                         'problem_name': problem_name, 'associated_body_site': body_site, 'problem_status': status,
                         'id': resource_id, 'code': code, 'severity': severity, 'encounter_id': encounter_id}
    set_answers.append(condition_details)
    return set_answers


def get_components_values(components):
    code_loinc_systolic = "8480-6"
    code_loinc_diastolic = "8462-4"

    comp_systolic_value = None
    comp_systolic_unit = None
    comp_diastolic_value = None
    comp_diastolic_unit = None
    for comp in components:
        component_codes = comp['code']['coding']
        for comp_code in component_codes:
            if comp_code['code'] == code_loinc_systolic:
                comp_systolic_value = comp['valueQuantity']['value']
                comp_systolic_unit = comp['valueQuantity']['unit']
            elif comp_code['code'] == code_loinc_diastolic:
                comp_diastolic_value = comp['valueQuantity']['value']
                comp_diastolic_unit = comp['valueQuantity']['unit']

    if comp_systolic_value is not None and comp_systolic_unit is not None and \
            comp_diastolic_value is not None and comp_diastolic_unit is not None:
        if comp_systolic_unit == comp_diastolic_unit:
            obs_val = str(comp_systolic_value) + "/" + str(comp_diastolic_value)
            obs_unit = comp_systolic_unit
        else:
            obs_val = 'NA'
            obs_unit = 'NA'
    else:
        obs_val = 'NA'
        obs_unit = 'NA'
    return obs_val, obs_unit


def get_observation_visit_data(resource, set_answers, encounter_id, active_encounters_list):
    # Getting the encounter location associated with the observation
    encounter_location = 'NA'
    for encounter in active_encounters_list:
        if encounter['encounter_id'] == encounter_id:
            encounter_location = encounter['encounter_location']
            break
    try:
        components = resource['resource']['component']
    except:
        components = None

    if components is not None:
        # Handling case for Blood Pressure components
        obs_val, obs_unit = get_components_values(components)
    else:
        try:
            obs_val = resource['resource']['valueQuantity']['value']
        except KeyError:
            try:
                obs_val = resource['resource']['valueCodeableConcept']['coding'][0]['display']
            except KeyError:
                obs_val = 'NA'
        try:
            obs_unit = resource['resource']['valueQuantity']['unit']
        except KeyError:
            obs_unit = 'NA'
    try:
        obs_time = resource['resource']['effectiveDateTime']
    except KeyError:
        obs_time = 'NA'
    try:
        obs_name = resource['resource']['code']['coding'][0]['display']
    except KeyError:
        obs_name = 'NA'
    try:
        obs_start_time = resource['resource']['effectivePeriod']['start']
    except KeyError:
        obs_start_time = 'NA'
    try:
        obs_end_time = resource['resource']['effectivePeriod']['end']
    except KeyError:
        obs_end_time = 'NA'
    try:
        obs_interpretation = resource['resource']['interpretation']['coding'][0]['code']
    except KeyError:
        obs_interpretation = 'NA'
    try:
        obs_interpretation_txt = resource['resource']['interpretation']['coding'][0]['display']
    except KeyError:
        obs_interpretation_txt = 'NA'
    try:
        resource_id = resource['resource']['id']
    except KeyError:
        resource_id = 'NA'
    try:
        code = resource['resource']['code']['coding'][0]['code']
    except KeyError:
        code = 'NA'

    observation_details = {'obs_start_time': obs_start_time, 'obs_end_time': obs_end_time,
                           'obs_effective_time': obs_time, 'obs_name': obs_name,
                           'obs_val': str(obs_val), 'obs_unit': obs_unit,
                           'observation_interpretation': obs_interpretation, 'id': resource_id, 'code': code,
                           'obs_interpret_txt': obs_interpretation_txt, 'obs_location': encounter_location}
    set_answers.append(observation_details)
    return set_answers


def get_medication_data(resource, set_answers, med_name=None, referred_med_id=None, medication_json_data=None):
    add_medication_resource_to_list = False
    try:
        med_status = resource['resource']['status']
    except KeyError:
        med_status = 'NA'

    if med_name is None:
        try:
            med_name = resource['resource']['medicationCodeableConcept']['coding'][0]['display']
        except KeyError:
            med_name = 'NA'

    if referred_med_id is not None:
        resource_id = referred_med_id
    else:
        resource_id = resource['resource']['id']

    try:
        was_not_taken = resource['resource']['wasNotTaken']
    except KeyError:
        was_not_taken = False

    if was_not_taken is True:
        print("A medication found was not taken.")
    else:
        try:
            effective_start_date = resource['resource']['effectivePeriod']['start']
        except KeyError:
            effective_start_date = 'NA'
        try:
            effective_end_date = resource['resource']['effectivePeriod']['end']
        except KeyError:
            effective_end_date = 'NA'
        try:
            effective_date = resource['resource']['effectiveDateTime']
        except KeyError:
            # Try another format
            try:
                effective_date = resource['resource']['dateWritten']
            except KeyError:
                effective_date = 'NA'
        try:
            if medication_json_data is not None:
                code = medication_json_data['code']['coding'][0]['code']
            else:
                code = resource['resource']['medicationCodeableConcept']['coding'][0]['code']
        except KeyError:
            code = 'NA'
        try:
            dosage_info = resource['resource']['dosage'][0]
        except KeyError:
            # Try another format
            try:
                dosage_info = resource['resource']['dosageInstruction'][0]
            except KeyError:
                dosage_info = {}
        try:
            as_needed = dosage_info['asNeededBoolean']
        except KeyError:
            as_needed = 'NA'
        try:
            timing = dosage_info['timing']
        except KeyError:
            timing = {}
        try:
            repeat = timing['repeat']
        except KeyError:
            repeat = {}
        try:
            frequency = repeat['frequency']
        except KeyError:
            frequency = 'NA'
        try:
            period = repeat['period']
        except KeyError:
            period = 'NA'
        try:
            period_units = repeat['periodUnits']
        except KeyError:
            period_units = 'NA'
        try:
            quantity = dosage_info['quantityQuantity']
        except KeyError:
            # Try another format
            try:
                quantity = dosage_info['doseSimpleQuantity']
            except KeyError:
                quantity = {}
        try:
            quantity_each_time = quantity['value']
        except KeyError:
            quantity_each_time = 'NA'
        try:
            quantity_unit = quantity['unit']
        except KeyError:
            quantity_unit = 'NA'
        try:
            dosage_info_text = dosage_info['text']
        except KeyError:
            # Construct a dosage info text
            if as_needed and as_needed != 'NA':
                dosage_info_text = 'As needed'
            else:
                dosage_info_components = []
                if quantity_each_time != 'NA':
                    dosage_info_components.append(quantity_each_time)
                    if quantity_unit != 'NA':
                        dosage_info_components.append(quantity_unit)
                    else:
                        dosage_info_components.append('quantity')
                if frequency != 'NA':
                    if frequency > 1:
                        dosage_info_components.append('{} times'.format(frequency))
                    elif frequency == 1:
                        dosage_info_components.append('one time')
                if period != 'NA' and period_units != 'NA':
                    if period > 1:
                        dosage_info_components.append('per {} {}'.format(period, period_units))
                    elif period == 1:
                        dosage_info_components.append('per {}'.format(period_units))
                if len(dosage_info_components) > 0:
                    dosage_info_text = ' '.join([str(c) for c in dosage_info_components])
                else:
                    try:
                        dosage_info_text = dosage_info['additionalInstructions']['coding'][0]['display']
                    except KeyError:
                        dosage_info_text = 'NA'

        total_daily_dose_quantity = 'NA'
        if period_units == 'd':
            if quantity_each_time != 'NA' and frequency != 'NA' and period != 'NA':
                total_daily_dose_quantity = (quantity_each_time * (frequency / period))
                total_daily_dose_quantity = round(total_daily_dose_quantity, 2)
        elif period_units == 'h':
            if quantity_each_time != 'NA' and frequency != 'NA' and period != 'NA':
                total_daily_dose_quantity = (quantity_each_time * ((24 / period) * frequency))
                total_daily_dose_quantity = round(total_daily_dose_quantity, 2)

        if med_status == 'active' and effective_date != 'NA':
            period_medication_consumption = \
                abs((time_utils.current_time - time_utils.get_final_date_time(effective_date)).days)
        elif effective_start_date != 'NA' and effective_end_date == 'NA':
            period_medication_consumption = \
                abs((time_utils.current_time - time_utils.get_final_date_time(effective_start_date)).days)
        elif effective_start_date != 'NA' and effective_end_date != 'NA':
            period_medication_consumption = \
                abs((time_utils.get_final_date_time(effective_end_date) -
                     time_utils.get_final_date_time(effective_start_date)).days)
        else:
            period_medication_consumption = 'NA'

        if total_daily_dose_quantity != 'NA' and period_medication_consumption != 'NA':
            total_medication_consumed = total_daily_dose_quantity * period_medication_consumption
        else:
            total_medication_consumed = 'NA'

        condition_name = 'NA'
        try:
            reason_reference = resource['resource']['reasonReference']['reference']
            reference_components = reason_reference.split('/')
            assert len(reference_components) == 2, 'Unhandled reason reference: {}'.format(reason_reference)
            assert reference_components[0] == 'Condition', 'Unhandled reason reference: {}'.format(reason_reference)
            condition_id = reference_components[1]
            condition_json_data = get_fhir_response_id('Condition', condition_id)
            try:
                condition_name = condition_json_data['code']['coding'][0]['display']
            except KeyError:
                pass
        except KeyError:
            pass

        # check if status is not 'NA', then if it is active or completed, if 'NA' -
        # then check if start date is available
        if med_status != 'NA':
            if med_status in {'active', 'completed', 'intended', 'stopped'}:
                add_medication_resource_to_list = True
        else:
            if effective_start_date != 'NA' or effective_date != 'NA':
                add_medication_resource_to_list = True

        ref_encounter = resource['resource']['encounter']['reference']
        encounter_id = ref_encounter.split('/')[1]

        if add_medication_resource_to_list is True:
            medication_details = {'med_status': med_status, 'effective_start_date': effective_start_date,
                                  'effective_end_date': effective_end_date, 'effective_date': effective_date,
                                  'med_name': med_name, 'as_needed': as_needed, 'dosage_info_text': dosage_info_text,
                                  'frequency': str(frequency), 'period': str(period), 'period_units': period_units,
                                  'quantity_each_time': quantity_each_time, 'quantity_unit': quantity_unit,
                                  'total_med_administered_or_consumed': str(total_medication_consumed),
                                  'reason': condition_name,
                                  'id': resource_id, 'code': code, 'encounter_id': encounter_id}
            set_answers.append(medication_details)

    return set_answers


def get_procedure_visit_data(resource, set_answers):
    add_procedure_resource_to_list = False
    try:
        proc_status = resource['resource']['status']
    except KeyError:
        proc_status = 'NA'

    try:
        referred_condition = resource['resource']['reasonReference']['reference']
        condition_id = referred_condition.split('/')[1]
        condition_json_data = get_fhir_response_id('Condition', condition_id)
        try:
            condition_name = condition_json_data['code']['coding'][0]['display']
        except KeyError:
            condition_name = 'NA'
    except KeyError:
        condition_name = 'NA'

    try:
        not_performed = resource['resource']['notPerformed']
    except KeyError:
        not_performed = False

    if not_performed is True:
        print("A procedure found was not performed as scheduled.")
    else:
        try:
            performed_start_date = resource['resource']['performedPeriod']['start']
        except KeyError:
            performed_start_date = 'NA'
        try:
            performed_end_date = resource['resource']['performedPeriod']['end']
        except KeyError:
            performed_end_date = 'NA'
        try:
            performed_date = resource['resource']['performedDateTime']
        except KeyError:
            performed_date = 'NA'
        try:
            proc_body_site = resource['resource']['bodySite'][0]['coding'][0]['display']
        except KeyError:
            proc_body_site = 'NA'
        try:
            procedure_name = resource['resource']['code']['coding'][0]['display']
        except KeyError:
            procedure_name = 'NA'
        try:
            resource_id = resource['resource']['id']
        except KeyError:
            resource_id = 'NA'
        try:
            code = resource['resource']['code']['coding'][0]['code']
        except KeyError:
            code = 'NA'

        try:
            diagnostic_report_found = 'No'
            procedure_report = resource['resource']['report']
            # Get the diagnostic report id for each of the reports available related to this procedure
            # Considering the first report
            if 'reference' in procedure_report[0]:
                diagnostic_report_id = procedure_report[0]['reference'].split('/')[1]
            else:
                diagnostic_report_id = 'NA'
            diagnostic_report_json_data = get_fhir_response_id('DiagnosticReport', diagnostic_report_id)
            if diagnostic_report_json_data is not None:
                try:
                    diagnostic_report_result = diagnostic_report_json_data['result']
                    # Assuming if result attribute is present, at least one result would be present in the array
                    # Considering the first result/observation
                    if 'reference' in diagnostic_report_result[0]:
                        observation_id = diagnostic_report_result[0]['reference'].split('/')[1]
                        diagnostic_report_found = 'Yes'
                    else:
                        diagnostic_report_found = 'No'
                        observation_id = 'NA'
                    observation_json_data = get_fhir_response_id('Observation', observation_id)
                    try:
                        components = observation_json_data['component']
                    except:
                        components = None

                    if components is not None:
                        ob_val, ob_unit = get_components_values(components)
                    else:
                        try:
                            ob_val = observation_json_data['valueQuantity']['value']
                        except KeyError:
                            try:
                                ob_val = resource['resource']['valueCodeableConcept']['coding'][0]['display']
                            except KeyError:
                                ob_val = 'NA'
                        try:
                            ob_unit = observation_json_data['valueQuantity']['unit']
                        except KeyError:
                            ob_unit = 'NA'
                    try:
                        ob_interpretation = observation_json_data['interpretation']['coding'][0]['code']
                    except KeyError:
                        ob_interpretation = 'NA'
                    try:
                        obs_interpretation_txt = observation_json_data['interpretation']['coding'][0]['display']
                    except KeyError:
                        obs_interpretation_txt = 'NA'
                except KeyError:
                    ob_val = 'NA'
                    ob_unit = 'NA'
                    ob_interpretation = 'NA'
                    obs_interpretation_txt = 'NA'
            else:
                ob_val = 'NA'
                ob_unit = 'NA'
                ob_interpretation = 'NA'
                obs_interpretation_txt = 'NA'
        except KeyError:
            ob_val = 'NA'
            ob_unit = 'NA'
            ob_interpretation = 'NA'
            obs_interpretation_txt = 'NA'

        try:
            focal_device = resource['resource']['focalDevice'][0]
            device_action_code = focal_device['action']['coding'][0]['code']
            device_reference = focal_device['manipulated']['reference']
            device_id = device_reference.split('/')[1]
            # Calling Device resource again
            device_json_data = get_fhir_response_id('Device', device_id)
            # Only the first device is taken
            device_name = device_json_data['type']['coding'][0]['display']

        except KeyError:
            device_action_code = 'NA'
            device_id = 'NA'
            device_name = 'NA'

        try:
            proc_loc = resource['resource']['location']['display']
        except KeyError:
            proc_loc = 'NA'

        if proc_status != 'NA':
            if proc_status in {'in-progress', 'completed'}:
                add_procedure_resource_to_list = True
        else:
            if performed_start_date != 'NA' or performed_date != 'NA':
                add_procedure_resource_to_list = True
        if add_procedure_resource_to_list is True:
            procedure_details = {'proc_status': proc_status,
                                 'performed_start_date': performed_start_date,
                                 'performed_end_date': performed_end_date,
                                 'performed_date': performed_date,
                                 'procedure_name': procedure_name,
                                 'procedure_body_site': proc_body_site,
                                 'observation_val': str(ob_val),
                                 'unit_observed_val': ob_unit,
                                 'observation_interpretation': ob_interpretation,
                                 'observation_interpret_txt': obs_interpretation_txt,
                                 'device_action_code': device_action_code,
                                 'device_id': device_id,
                                 'device_name': device_name,
                                 'procedure_location': proc_loc,
                                 'id': resource_id, 'code': code,
                                 'diagnostic_report_found': diagnostic_report_found,
                                 'reason': condition_name}
            set_answers.append(procedure_details)

    return set_answers


def get_med_administration_visit_data(resource, set_answers, medication_json_data):
    add_med_admin_resource_to_list = False
    try:
        med_name = medication_json_data['code']['coding'][0]['display']
    except KeyError:
        med_name = 'NA'
    try:
        resource_id = resource['resource']['id']
    except KeyError:
        resource_id = 'NA'
    try:
        code = medication_json_data['code']['coding'][0]['code']
    except KeyError:
        code = 'NA'
    try:
        med_admin_status = resource['resource']['status']
    except KeyError:
        med_admin_status = 'NA'
    try:
        not_given = resource['resource']['wasNotGiven']
    except KeyError:
        not_given = False

    if not_given is True:
        print("A medication found was not administered.")
    else:
        try:
            effective_med_ad_start_date = resource['resource']['effectiveTimePeriod']['start']
        except KeyError:
            effective_med_ad_start_date = 'NA'
        try:
            effective_med_ad_end_date = resource['resource']['effectiveTimePeriod']['end']
        except KeyError:
            effective_med_ad_end_date = 'NA'
        try:
            med_ad_effective_time = resource['resource']['effectiveTimeDateTime']
        except KeyError:
            med_ad_effective_time = 'NA'
        try:
            dosage = resource['resource']['dosage']
            try:
                dosage_text = dosage['text']
            except KeyError:
                dosage_text = 'NA'
            try:
                quantity_each_administration = dosage['quantity']['value']
            except KeyError:
                quantity_each_administration = 'NA'
            try:
                quantity_unit = dosage['quantity']['unit']
            except KeyError:
                quantity_unit = 'NA'
            try:
                rate_ratio = dosage['rateRatio']
                rate_numerator = rate_ratio['numerator']
                rate_denominator = rate_ratio['denominator']
                numerator_value = rate_numerator['value']
                numerator_unit = rate_numerator['unit']
                denominator_value = rate_denominator['value']
                denominator_unit = rate_denominator['unit']

            except KeyError:
                numerator_value = 'NA'
                numerator_unit = 'NA'
                denominator_value = 'NA'
                denominator_unit = 'NA'
            # Quantity conveys the total amount administered over period of time of a single administration if duration
            # or rate is not present
            if med_ad_effective_time != 'NA':
                total_med_administered = quantity_each_administration
                unit = quantity_unit
                duration_med_admin = 'Instantaneous event'
            else:
                if effective_med_ad_start_date != 'NA' and numerator_value != 'NA' and numerator_unit != 'NA' and \
                        denominator_value != 'NA' and denominator_unit != 'NA':
                    start_date = time_utils.get_final_date_time(effective_med_ad_start_date)
                    if effective_med_ad_end_date != 'NA':
                        end_date = time_utils.get_final_date_time(effective_med_ad_end_date)
                    else:
                        end_date = time_utils.current_time
                    duration = (end_date - start_date).total_seconds() / 3600
                    if denominator_unit in {'minutes', 'mins', 'min', 'minute'}:
                        total_med_administered = (duration/(float(denominator_value)/60)) * float(numerator_value)
                    elif denominator_unit in {'hours', 'hour', 'hrs', 'hr'}:
                        total_med_administered = (duration / (float(denominator_value))) * float(numerator_value)
                    elif denominator_unit in {'days', 'day'}:
                        total_med_administered = (duration / (float(denominator_value) * 24)) * float(numerator_value)
                    else:
                        print('Unit of time is not present in the dosage rate or '
                              'not supported for units other than hours/minutes.')
                        total_med_administered = 'NA'
                    unit = numerator_unit
                    duration_med_admin = duration
                else:
                    print('Total medication dose cannot be calculated and '
                          'the administration is not an instantaneous event.')
                    total_med_administered = 'NA'
                    unit = 'NA'
                    duration_med_admin = 'NA'
        except KeyError:
            dosage_text = 'NA'
            quantity_each_administration = 'NA'
            total_med_administered = 'NA'
            unit = 'NA'
            duration_med_admin = 'NA'
        if med_admin_status != 'NA':
            if med_admin_status in {'in-progress', 'completed'}:
                add_med_admin_resource_to_list = True
        else:
            if effective_med_ad_start_date != 'NA' or med_ad_effective_time != 'NA':
                add_med_admin_resource_to_list = True
        if add_med_admin_resource_to_list is True:
            med_admin_details = {'med_administration_status': med_admin_status,
                                 'med_admin_start_date': effective_med_ad_start_date,
                                 'med_admin_end_date': effective_med_ad_end_date,
                                 'medication_name': med_name,
                                 'med_admin_effective_date': med_ad_effective_time,
                                 'dosage_info_text': dosage_text,
                                 'quantity_each_administration': quantity_each_administration,
                                 'quantity_unit': unit,
                                 'total_med_administered_or_consumed': str(total_med_administered),
                                 'id': resource_id, 'code': code,
                                 'duration_med_admin': duration_med_admin}
            set_answers.append(med_admin_details)
    return set_answers


def get_immunization_visit_data(resource, set_answers, encounter_id):
    try:
        resource_id = resource['resource']['id']
    except KeyError:
        resource_id = 'NA'
    try:
        imm_datetime = str(resource['resource']['date'])
    except KeyError:
        imm_datetime = 'NA'
    try:
        code = resource['resource']['vaccineCode']['coding'][0]['code']
    except KeyError:
        code = 'NA'
    try:
        imm_name = resource['resource']['vaccineCode']['coding'][0]['display']
    except KeyError:
        imm_name = 'NA'
    try:
        status = resource['resource']['status']
    except KeyError:
        status = 'NA'

    immunization_details = {'id': resource_id, 'imm_datetime': imm_datetime, 'code': code, 'imm_name': imm_name,
                            'status': status, 'encounter_id': encounter_id}
    set_answers.append(immunization_details)
    return set_answers


def get_careplan_visit_data(resource, set_answers, encounter_id):
    try:
        resource_id = resource['resource']['id']
    except KeyError:
        resource_id = 'NA'
    try:
        code = resource['resource']['category'][0]['coding'][0]['code']
    except KeyError:
        code = 'NA'
    try:
        name = resource['resource']['category'][0]['coding'][0]['display']
    except KeyError:
        name = 'NA'
    try:
        status = resource['resource']['status']
    except KeyError:
        status = 'NA'
    try:
        start_date = resource['resource']['period']['start']
    except KeyError:
        start_date = 'NA'
    try:
        end_date = resource['resource']['period']['end']
    except KeyError:
        end_date = 'NA'
    activities = []
    try:
        activities_obj = resource['resource']['activity']
    except KeyError:
        activities_obj = []
    for activity in activities_obj:
        activity_detail = activity['detail']
        activity_name = activity_detail['code']['coding'][0]['display']
        activity_status = activity_detail['status']
        activity_prohibited = activity_detail['prohibited']
        activities.append({
            'name': activity_name,
            'status': activity_status,
            'prohibited': activity_prohibited
        })
    reasons = []
    try:
        addresses_obj = resource['resource']['addresses']
    except KeyError:
        addresses_obj = []
    for add in addresses_obj:
        try:
            reason_reference = add['reference']
            reference_components = reason_reference.split('/')
            assert len(reference_components) == 2, 'Unhandled reason reference: {}'.format(reason_reference)
            assert reference_components[0] == 'Condition', 'Unhandled reason reference: {}'.format(reason_reference)
            condition_id = reference_components[1]
            condition_json_data = get_fhir_response_id('Condition', condition_id)
            condition_name = condition_json_data['code']['coding'][0]['display']
            reasons.append(condition_name)
        except KeyError:
            continue

    careplan_details = {'id': resource_id, 'code': code, 'name': name, 'status': status, 'start_date': start_date,
                        'end_date': end_date, 'activities': activities, 'reason': reasons, 'encounter_id': encounter_id}
    set_answers.append(careplan_details)
    return set_answers


def get_allergyintolerance_visit_data(resource, set_answers, encounter_id):
    try:
        resource_id = resource['resource']['id']
    except KeyError:
        resource_id = 'NA'
    try:
        code = resource['resource']['substance']['coding'][0]['code']
    except KeyError:
        code = 'NA'
    try:
        name = resource['resource']['substance']['coding'][0]['display']
    except KeyError:
        name = 'NA'
    try:
        status = resource['resource']['status']
    except KeyError:
        status = 'NA'
    try:
        start_date = resource['resource']['recordedDate']
    except KeyError:
        start_date = 'NA'
    try:
        criticality = resource['resource']['criticality']
    except KeyError:
        criticality = 'NA'
    try:
        intolerance_type = resource['resource']['type']
    except KeyError:
        intolerance_type = 'NA'
    try:
        category = resource['resource']['category']
    except KeyError:
        category = 'NA'

    resource_details = {'id': resource_id, 'code': code, 'name': name, 'status': status, 'start_date': start_date,
                        'criticality': criticality, 'type': intolerance_type, 'category': category,
                        'encounter_id': encounter_id}
    set_answers.append(resource_details)
    return set_answers


def get_diagnosticreport_visit_data(resource, set_answers, encounter_id):
    try:
        resource_id = resource['resource']['id']
    except KeyError:
        resource_id = 'NA'
    try:
        code = resource['resource']['code']['coding'][0]['code']
    except KeyError:
        code = 'NA'
    try:
        name = resource['resource']['code']['coding'][0]['display']
    except KeyError:
        name = 'NA'
    try:
        status = resource['resource']['status']
    except KeyError:
        status = 'NA'
    try:
        effective_date = resource['resource']['effectiveDateTime']
    except KeyError:
        effective_date = 'NA'
    try:
        issued_date = resource['resource']['issued']
    except KeyError:
        issued_date = 'NA'
    try:
        results = resource['resource']['result']
    except KeyError:
        results = []
    observations_details = []
    for res in results:
        res_ref = res['reference']
        res_ref_components = res_ref.split('/')
        assert len(res_ref_components) == 2, 'Unhandled reference: {}'.format(res_ref)
        assert res_ref_components[0] == 'Observation', 'Unhandled reference for DiagnosticReport: {}'.format(res_ref)
        observation_id = res_ref_components[1]
        obs_resource = get_fhir_response_id('Observation', observation_id)
        obs_resource_data = {'resource': obs_resource}
        try:
            obs_encounter_ref = obs_resource_data['resource']['encounter']['reference']
            obs_enc_ref_components = obs_encounter_ref.split('/')
            assert len(obs_enc_ref_components) == 2, 'Unhandled observation encounter reference: {}'.format(
                obs_encounter_ref)
            obs_encounter_id = obs_enc_ref_components[1]
        except KeyError:
            obs_encounter_id = None
        obs_details = []
        obs_details = get_observation_visit_data(obs_resource_data, obs_details, obs_encounter_id,
                                                 active_encounters_list=[])
        observations_details.extend(obs_details)

    resource_details = {'id': resource_id, 'code': code, 'name': name, 'status': status,
                        'effective_date': effective_date, 'issued_date': issued_date,
                        'observations': observations_details, 'encounter_id': encounter_id}
    set_answers.append(resource_details)
    return set_answers


def get_practitioner_data(set_answers_practitioners, practitioner_json_data, ps, en):
    practitioner_name = practitioner_json_data['name']
    given_name = practitioner_name['given'][0]
    family_name = practitioner_name['family'][0]
    prefix = practitioner_name['prefix'][0]
    full_name = prefix + ' ' + given_name + ' ' + family_name
    practitioner_details = {
        'participant_start': ps[0],
        'encounter_start_date': en['encounter_start_date'],
        'participant_end': ps[1],
        'participant_type': ps[2],
        'participant_id': ps[3],
        'full_name': full_name
    }
    set_answers_practitioners.append(practitioner_details)
    return set_answers_practitioners

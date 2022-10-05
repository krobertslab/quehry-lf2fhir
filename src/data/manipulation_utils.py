from datetime import datetime
import src.data.time_utils as time_utils
import src.data.settings as settings


def get_answer_delta_func(set_answers, fhir_resource):
    if set_answers:
        return 'Yes', fhir_resource
    else:
        return 'No', fhir_resource


def find_latest_date_time(all_date_times):
    if len(all_date_times) > 0:
        latest_time = max(dt for dt in all_date_times)
        latest_time_index = all_date_times.index(latest_time)
    else:
        latest_time_index = -1
    return latest_time_index


def get_latest_answer(set_answers, fhir_resource, effective_date, start_date='NA'):
    all_date_times = []
    for item in set_answers:
        date_time = None
        effective_date_time_str = item[effective_date]
        if effective_date_time_str != 'NA' and effective_date_time_str != 'None':
            date_time = time_utils.get_final_date_time(effective_date_time_str)
        elif item[start_date] != 'NA':
            date_time = time_utils.get_final_date_time(item[start_date])
        if date_time is not None:
            all_date_times.append(date_time)
    latest_time_index = find_latest_date_time(all_date_times)
    if latest_time_index > -1:
        item = set_answers[latest_time_index]
        return item, fhir_resource
    else:
        return None, fhir_resource


def find_earliest_date_time(all_date_times):
    if len(all_date_times) > 0:
        earliest_time = min(dt for dt in all_date_times)
        earliest_time_index = all_date_times.index(earliest_time)
    else:
        earliest_time_index = -1
    return earliest_time_index


def get_earliest_answer(set_answers, fhir_resource, effective_date, start_date='NA'):
    all_date_times = []
    for item in set_answers:
        date_time = None
        effective_date_time_str = item[effective_date]
        if effective_date_time_str != 'NA' and effective_date_time_str != 'None':
            date_time = time_utils.get_final_date_time(effective_date_time_str)
        elif item[start_date] != 'NA':
            date_time = time_utils.get_final_date_time(item[start_date])
        if date_time is not None:
            all_date_times.append(date_time)
    earliest_time_index = find_earliest_date_time(all_date_times)
    if earliest_time_index > -1:
        item = set_answers[earliest_time_index]
        return item, fhir_resource
    else:
        return None, fhir_resource


def get_answer_latest_func(set_answers, fhir_resource):
    if set_answers is not None:
        if fhir_resource == 'Observation':
            effective_date = 'obs_effective_time'
            start_date = 'obs_start_time'
            return get_latest_answer(set_answers, fhir_resource, effective_date, start_date)
        elif fhir_resource == 'MedicationAdministration':
            effective_date = 'med_admin_effective_date'
            start_date = 'med_admin_start_date'
            return get_latest_answer(set_answers, fhir_resource, effective_date, start_date)
        elif fhir_resource in {'MedicationStatement', 'MedicationOrder'}:
            effective_date = 'effective_date'
            start_date = 'effective_start_date'
            return get_latest_answer(set_answers, fhir_resource, effective_date, start_date)
        elif fhir_resource == 'Procedure':
            effective_date = 'performed_date'
            start_date = 'performed_start_date'
            return get_latest_answer(set_answers, fhir_resource, effective_date, start_date)
        elif fhir_resource == 'Condition':
            effective_date = 'onset_datetime'
            return get_latest_answer(set_answers, fhir_resource, effective_date)
        # Getting the latest date for the encounter for has_doctor
        elif fhir_resource == 'Encounter':
            effective_date = 'encounter_start_date'
            return get_latest_answer(set_answers, fhir_resource, effective_date)
        elif fhir_resource == 'Practitioner':
            effective_date = 'participant_start'
            return get_latest_answer(set_answers, fhir_resource, effective_date)
        elif fhir_resource == 'Immunization':
            effective_date = 'imm_datetime'
            return get_latest_answer(set_answers, fhir_resource, effective_date)
        elif fhir_resource in {'CarePlan', 'AllergyIntolerance'}:
            effective_date = 'start_date'
            return get_latest_answer(set_answers, fhir_resource, effective_date)
        elif fhir_resource == 'DiagnosticReport':
            effective_date = 'effective_date'
            return get_latest_answer(set_answers, fhir_resource, effective_date)
        return None, None
    return set_answers, fhir_resource


def get_answer_earliest_func(set_answers, fhir_resource):
    if set_answers is not None:
        if fhir_resource == 'Observation':
            effective_date = 'obs_effective_time'
            start_date = 'obs_start_time'
            return get_earliest_answer(set_answers, fhir_resource, effective_date, start_date)
        elif fhir_resource == 'MedicationAdministration':
            effective_date = 'med_admin_effective_date'
            start_date = 'med_admin_start_date'
            return get_earliest_answer(set_answers, fhir_resource, effective_date, start_date)
        elif fhir_resource in {'MedicationStatement', 'MedicationOrder'}:
            effective_date = 'effective_date'
            start_date = 'effective_start_date'
            return get_earliest_answer(set_answers, fhir_resource, effective_date, start_date)
        elif fhir_resource == 'Procedure':
            effective_date = 'performed_date'
            start_date = 'performed_start_date'
            return get_earliest_answer(set_answers, fhir_resource, effective_date, start_date)
        elif fhir_resource == 'Condition':
            effective_date = 'onset_datetime'
            return get_earliest_answer(set_answers, fhir_resource, effective_date)
        elif fhir_resource == 'Encounter':
            effective_date = 'encounter_start_date'
            return get_earliest_answer(set_answers, fhir_resource, effective_date)
        elif fhir_resource == 'Practitioner':
            effective_date = 'participant_start'
            return get_earliest_answer(set_answers, fhir_resource, effective_date)
        elif fhir_resource == 'Immunization':
            effective_date = 'imm_datetime'
            return get_earliest_answer(set_answers, fhir_resource, effective_date)
        elif fhir_resource in {'CarePlan', 'AllergyIntolerance'}:
            effective_date = 'start_date'
            return get_earliest_answer(set_answers, fhir_resource, effective_date)
        elif fhir_resource == 'DiagnosticReport':
            effective_date = 'effective_date'
            return get_earliest_answer(set_answers, fhir_resource, effective_date)
        return None, None
    return set_answers, fhir_resource


def get_max_or_min_answer(set_answers, fhir_resource, value, func):
    if len(set_answers) > 0:
        obs_val_list = []
        for item in set_answers:
            val = item[value]
            if val != 'NA':
                # Blood pressure case
                if '/' in val:
                    val_components = val.split('/')
                    assert len(val_components) == 2, 'invalid blood pressure value: {}'.format(val)
                    obs_val_list.append((float(val_components[0]), float(val_components[1])))
                else:
                    obs_val_list.append(float(val))
        if len(obs_val_list) > 0:
            if func == 'max':
                apply_func = max
            else:
                apply_func = min
            if isinstance(obs_val_list[0], tuple):
                final_val_sys = apply_func(v[0] for v in obs_val_list)
                final_val_dia = apply_func(v[1] for v in obs_val_list)
                return 'Highest Systolic BP was {} and highest Diastolic BP was {}'.format(
                    final_val_sys, final_val_dia), fhir_resource
            else:
                final_val = apply_func(v for v in obs_val_list)
            return final_val, fhir_resource
        else:
            return None, fhir_resource
    else:
        return None, fhir_resource


def get_answer_max_or_min_func(set_answers, fhir_resource, func):
    if set_answers is not None:
        if fhir_resource == 'Procedure':
            value = 'observation_val'
            return get_max_or_min_answer(set_answers, fhir_resource, value, func)
        elif fhir_resource == 'Observation':
            value = 'obs_val'
            return get_max_or_min_answer(set_answers, fhir_resource, value, func)
        return None, None
    return set_answers, fhir_resource


def get_answer_count_func(set_answers, fhir_resource):
    if set_answers is not None:
        if fhir_resource in {'Condition', 'Observation', 'Procedure', 'CarePlan', 'Immunization', 'Encounter',
                             'DiagnosticReport', 'MedicationOrder'}:
            if len(set_answers) > 0:
                count = len(set_answers)
                text_to_display = str(count)
                return text_to_display, fhir_resource
            else:
                return None, fhir_resource
        return None, None
    return set_answers, fhir_resource


def get_answer_sum_func(set_answers, fhir_resource):
    if set_answers is not None:
        if fhir_resource == 'MedicationAdministration':
            if len(set_answers) > 0:
                sum = 0.0
                for ans in set_answers:
                    unit = ans['quantity_unit']
                    if 'overlapping_hrs_within_time_range' in ans:
                        if ans['overlapping_hrs_within_time_range'] != 'NA' and ans['rate_med_admin'] != 'NA':
                            sum += ans['rate_med_admin'] * ans['overlapping_hrs_within_time_range']
                        else:
                            sum += ans['total_med_administered_or_consumed']
                    else:
                        if ans['med_admin_end_date'] != 'NA':
                            med_admin_end_date_updated = time_utils.get_final_date_time(ans['med_admin_end_date'])
                            if med_admin_end_date_updated > time_utils.current_time:
                                med_admin_end_date_updated = time_utils.current_time
                            total_med_administered_or_consumed = float(ans['total_med_administered_or_consumed'])
                            duration = ans['duration_med_admin']
                            rate = total_med_administered_or_consumed / duration
                            med_admin_st_date_updated = time_utils.get_final_date_time(ans['med_admin_start_date'])
                            updated_duration_till_current_time = \
                                (med_admin_end_date_updated - med_admin_st_date_updated).total_seconds() / 3600
                            actual_med_administered_or_consumed = rate * updated_duration_till_current_time
                            sum += actual_med_administered_or_consumed
                        elif ans['med_admin_effective_date'] != 'NA':
                            sum += ans['total_med_administered_or_consumed']

                if unit != 'NA':
                    return str(sum) + ' ' + unit, fhir_resource
                else:
                    return str(sum), fhir_resource
            else:
                return None, fhir_resource
        elif fhir_resource in {'Observation', 'Procedure'}:
            if len(set_answers) > 0:
                sum = 0.0
                if fhir_resource == 'Observation':
                    unit = set_answers[0]['obs_unit']
                    first_val = set_answers[0]['obs_val']
                else:
                    unit = set_answers[0]['unit_observed_val']
                    first_val = set_answers[0]['observation_val']

                if '/' not in first_val:
                    for ans in set_answers:
                        if fhir_resource == 'Observation':
                            sum += float(ans['obs_val'])
                        else:
                            sum += float(ans['observation_val'])

                    return str(sum) + ' ' + unit, fhir_resource
                else:
                    print('Sum is not calculated for observations such as BP having two components.')
                    return None, fhir_resource
            else:
                return None, fhir_resource
        else:
            return None, None
    return set_answers, fhir_resource


def get_answer_loc_func(answer, fhir_resource):
    if answer is not None:
        if fhir_resource == 'Condition':
            location = answer['associated_body_site']
            return location, fhir_resource
        elif fhir_resource == 'Procedure':
            location = answer['procedure_body_site']
            return location, fhir_resource
        else:
            return None, None

    return answer, fhir_resource


def get_answer_dose_func(answer, fhir_resource):
    if answer is not None:
        if fhir_resource in {'MedicationStatement', 'MedicationAdministration', 'MedicationOrder'}:
            dose = answer['dosage_info_text']
            return dose, fhir_resource
        else:
            return None, None
    return answer, fhir_resource


def get_answer_duration_func(answer, fhir_resource):
    if answer is not None:
        if not isinstance(answer, list):
            if settings.device_found is False:
                if fhir_resource == 'Procedure':
                    if answer['performed_start_date'] != 'NA' and answer['performed_end_date'] != 'NA':
                        start_date = time_utils.get_final_date_time(answer['performed_start_date'])
                        end_date = time_utils.get_final_date_time(answer['performed_end_date'])
                        if end_date > time_utils.current_time:
                            duration = (time_utils.current_time - start_date).total_seconds() / 3600
                        else:
                            duration = (end_date - start_date).total_seconds() / 3600
                        duration_str = time_utils.get_formatted_duration_string(duration)
                        return duration_str, fhir_resource
                elif fhir_resource == 'MedicationAdministration':
                    if answer['med_admin_start_date'] != 'NA' and answer['med_admin_end_date'] != 'NA':
                        start_date = time_utils.get_final_date_time(answer['med_admin_start_date'])
                        end_date = time_utils.get_final_date_time(answer['med_admin_end_date'])
                        if end_date > time_utils.current_time:
                            duration = (time_utils.current_time - start_date).total_seconds() / 3600
                        else:
                            duration = (end_date - start_date).total_seconds() / 3600
                        duration_str = time_utils.get_formatted_duration_string(duration)
                        return duration_str, fhir_resource
                elif fhir_resource == 'Encounter':
                    start_date = time_utils.get_final_date_time(answer['encounter_start_date'])
                    end_date_str = answer['encounter_end_date']

                    end_date = time_utils.get_final_date_time(end_date_str) if end_date_str != 'None' else datetime.max

                    if end_date > time_utils.current_time:
                        duration = (time_utils.current_time - start_date).total_seconds() / 3600
                    else:
                        duration = (end_date - start_date).total_seconds() / 3600
                    duration_str = time_utils.get_formatted_duration_string(duration)
                    return duration_str, fhir_resource
                elif fhir_resource == 'CarePlan':
                    start_date = time_utils.get_final_date_time(answer['start_date'])
                    end_date = time_utils.get_final_date_time(answer['end_date'])
                    if end_date > time_utils.current_time:
                        duration = (time_utils.current_time - start_date).total_seconds() / 3600
                    else:
                        duration = (end_date - start_date).total_seconds() / 3600
                    duration_str = time_utils.get_formatted_duration_string(duration)
                    return duration_str, fhir_resource
                    return duration, fhir_resource
                elif fhir_resource == 'Condition':
                    start_date = time_utils.get_final_date_time(answer['onset_datetime'])
                    end_date_str = answer['abatement_datetime']
                    if end_date_str != 'None':
                        end_date = time_utils.get_final_date_time(end_date_str)
                    else:
                        end_date = time_utils.current_time
                    if end_date > time_utils.current_time:
                        duration = (time_utils.current_time - start_date).total_seconds() / 3600
                    else:
                        duration = (end_date - start_date).total_seconds() / 3600
                    duration_str = time_utils.get_formatted_duration_string(duration)
                    return duration_str, fhir_resource
                elif fhir_resource == 'Immunization':
                    start_date = time_utils.get_final_date_time(answer['imm_datetime'])
                    end_date = time_utils.current_time
                    duration = (end_date - start_date).total_seconds() / 3600
                    duration_str = time_utils.get_formatted_duration_string(duration)
                    return duration_str, fhir_resource
                elif fhir_resource == 'MedicationOrder':
                    if answer['effective_date'] != 'NA':
                        start_date_str = answer['effective_date']
                    else:
                        start_date_str = answer['effective_start_date']
                    start_date = time_utils.get_final_date_time(start_date_str)
                    if answer['effective_end_date'] != 'NA':
                        end_date = time_utils.get_final_date_time(answer['effective_end_date'])
                    elif answer['med_status'] == 'active':
                        end_date = time_utils.current_time
                    else:
                        duration = {'start_date': start_date_str, 'end_date': 'NA'}
                        return duration, fhir_resource
                    duration = (end_date - start_date).total_seconds() / 3600
                    duration_str = time_utils.get_formatted_duration_string(duration)
                    return duration_str, fhir_resource
            # If related to device
            else:
                if answer['performed_start_date'] != 'NA':
                    start_date = time_utils.get_final_date_time(answer['performed_start_date'])
                    end_date = time_utils.current_time
                    duration = (end_date - start_date).total_seconds() / 3600
                    duration = str(duration) + ' hours'
                    return duration, fhir_resource
        else:
            answer, fhir_resource = get_answer_latest_func(answer, fhir_resource)
            duration, fhir_resource = get_answer_duration_func(answer, fhir_resource)
            return duration, fhir_resource
    return None, None


def get_answer_is_positive_or_negative_func(answer, fhir_resource, func):
    if answer is not None:
        if isinstance(answer, list):
            set_filtered_answers = []
            if fhir_resource == 'Procedure' or fhir_resource == 'Observation':
                for ans in answer:
                    interpretation = ans['observation_interpretation']
                    if func == 'is_positive' or func == 'positive':
                        if interpretation in {'POS', 'H'}:
                            set_filtered_answers.append(ans)
                    elif func == 'is_negative' or func == 'negative':
                        if interpretation == 'NEG':
                            set_filtered_answers.append(ans)
                if len(set_filtered_answers) > 0:
                    return set_filtered_answers, fhir_resource
                else:
                    if func == 'is_positive' or func == 'positive':
                        print('No resource found with positive result.')
                    elif func == 'is_negative' or func == 'negative':
                        print('No resource found with negative result.')
                    return None, fhir_resource
            else:
                return None, None
        else:
            if fhir_resource == 'Procedure' or fhir_resource == 'Observation':
                interpretation = answer['observation_interpretation']
                if func == 'is_positive' or func == 'positive':
                    if interpretation in {'POS', 'H'}:
                        return 'Yes', fhir_resource
                    else:
                        return 'No', fhir_resource
                elif func == 'is_negative' or func == 'negative':
                    if interpretation == 'NEG':
                        return 'Yes', fhir_resource
                    else:
                        return 'No', fhir_resource
            else:
                return None, None
    return answer, fhir_resource


def get_answer_is_high_func(answer, fhir_resource):
    if answer is not None:
        if fhir_resource == 'Procedure':
            interpretation = answer['observation_interpretation']
            if interpretation == 'H':
                return 'Yes', fhir_resource
        else:
            return None, None
    return answer, fhir_resource


def get_answer_is_normal_func(answer, fhir_resource):
    if answer is not None:
        if fhir_resource == 'Observation':
            interpretation = answer['observation_interpretation']
            if interpretation == 'N':
                return 'Yes', fhir_resource
        else:
            return None, None
    return answer, fhir_resource


def get_answer_is_healed_func(answer, fhir_resource):
    if answer is not None:
        if fhir_resource == 'Condition':
            if answer['problem_status'] == 'resolved':
                return 'Yes', fhir_resource
            else:
                return 'No, it is {}'.format(answer['problem_status']), fhir_resource
        else:
            return None, None
    return answer, fhir_resource


def get_answer_time_func(answer, fhir_resource):
    if answer is not None:
        # Get discharge/admission time of encounter
        if fhir_resource == 'Encounter':
            if isinstance(answer, dict):
                action = answer['admsn_dschg_readmsn']
                if action in {'admission', 'readmission', 'code'}:
                    time = answer['encounter_start_date']
                elif action == 'discharge':
                    time = answer['encounter_end_date']
                else:
                    return None, None
                return time, fhir_resource
            elif len(list(answer)) == 0:
                return None, fhir_resource
            else:
                action = list(answer)[0]['admsn_dschg_readmsn']
                if action in {'admission', 'readmission', 'code'}:
                    time = list(answer)[0]['encounter_start_date']
                elif action == 'discharge':
                    time = list(answer)[0]['encounter_end_date']
                else:
                    return None, None
                return time, fhir_resource
        elif fhir_resource == 'Procedure':
            if isinstance(answer, dict):
                time = {'start_time': None, 'end_time': None}
                if answer['performed_date'] != 'NA':
                    time['start_time'] = answer['performed_date']
                else:
                    time['start_time'] = answer['performed_start_date']
                time['end_time'] = answer['performed_end_date']
                return time, fhir_resource
            else:
                print("Time function cannot be applied to a list.")
                return None, None
        elif fhir_resource == 'MedicationAdministration':
            if isinstance(answer, dict):
                time = {'start_time': None, 'end_time': None}
                if answer['med_admin_effective_date'] != 'NA':
                    time['start_time'] = answer['med_admin_effective_date']
                else:
                    time['start_time'] = answer['med_admin_start_date']
                time['end_time'] = answer['med_admin_end_date']
                return time, fhir_resource
            else:
                print("Time function cannot be applied to a list.")
                return None, None
        elif fhir_resource == 'MedicationOrder':
            if isinstance(answer, dict):
                time = {'start_time': None, 'end_time': None}
                if answer['effective_date'] != 'NA':
                    time['start_time'] = answer['effective_date']
                else:
                    time['start_time'] = answer['effective_start_date']
                time['end_time'] = answer['effective_end_date']
                return time, fhir_resource
            else:
                print("Time function cannot be applied to a list.")
                return None, None
        elif fhir_resource == 'Observation':
            if isinstance(answer, dict):
                time = {'start_time': None, 'end_time': None}
                if answer['obs_effective_time'] != 'NA':
                    time['start_time'] = answer['obs_effective_time']
                else:
                    time['start_time'] = answer['obs_start_time']
                time['end_time'] = answer['obs_end_time']
                return time, fhir_resource
            else:
                print("Time function cannot be applied to a list.")
                return None, None
        elif fhir_resource == 'CarePlan':
            if isinstance(answer, dict):
                time = {'start_time': answer['start_date'], 'end_time': answer['end_date']}
                return time, fhir_resource
            else:
                print("Time function cannot be applied to a list.")
                return None, None
        elif fhir_resource == 'Condition':
            if isinstance(answer, dict):
                time = {'start_time': answer['onset_datetime'], 'end_time': answer['abatement_datetime']}
                return time, fhir_resource
            else:
                print("Time function cannot be applied to a list.")
                return None, None
        elif fhir_resource == 'Immunization':
            if isinstance(answer, dict):
                time = answer['imm_datetime']
                return time, fhir_resource
            else:
                print("Time function cannot be applied to a list.")
                return None, None
        elif fhir_resource == 'AllergyIntolerance':
            if isinstance(answer, dict):
                time = answer['start_date']
                return time, fhir_resource
            else:
                print("Time function cannot be applied to a list.")
                return None, None
        elif fhir_resource == 'DiagnosticReport':
            if isinstance(answer, dict):
                if answer['effective_date'] != 'NA':
                    time = answer['effective_date']
                else:
                    time = answer['issued_date']
                return time, fhir_resource
            else:
                print("Time function cannot be applied to a list.")
                return None, None
        else:
            return None, None
    return answer, fhir_resource


def get_answer_is_increasing_or_decreasing_func(set_answers, fhir_resource, func):
    if set_answers is not None:
        if fhir_resource == 'Observation':
            if len(set_answers) >= 2:
                all_effective_date_times = []
                for item in set_answers:
                    effective_date_time_str = item['obs_effective_time']
                    if effective_date_time_str != 'NA':
                        effective_date_time = time_utils.get_final_date_time(effective_date_time_str)
                        all_effective_date_times.append(effective_date_time)
                latest_time_index = find_latest_date_time(all_effective_date_times)
                if latest_time_index > -1:
                    most_latest_item = set_answers[latest_time_index]
                    del set_answers[latest_time_index]
                    second_most_latest_item, fhir_resource = get_answer_latest_func(set_answers, fhir_resource)
                    if '/' not in most_latest_item['obs_val']:
                        if func == 'is_increasing':
                            if most_latest_item['obs_val'] > second_most_latest_item['obs_val']:
                                return 'Yes', fhir_resource
                            else:
                                return 'No', fhir_resource
                        else:
                            if most_latest_item['obs_val'] < second_most_latest_item['obs_val']:
                                return 'Yes', fhir_resource
                            else:
                                return 'No', fhir_resource
                    else:
                        most_latest_sys_bp = most_latest_item['obs_val'].split('/')[0]
                        most_latest_dias_bp = most_latest_item['obs_val'].split('/')[1]
                        second_most_latest_sys_bp = second_most_latest_item['obs_val'].split('/')[0]
                        second_most_latest_dias_bp = second_most_latest_item['obs_val'].split('/')[1]
                        if func == 'is_increasing':
                            if most_latest_sys_bp > second_most_latest_sys_bp and \
                                    most_latest_dias_bp > second_most_latest_dias_bp:
                                return 'Both Systolic and Diastolic Blood Pressures have risen.', fhir_resource
                            elif most_latest_sys_bp > second_most_latest_sys_bp and \
                                    most_latest_dias_bp <= second_most_latest_dias_bp:
                                return 'Systolic Blood Pressure has risen but not Diastolic Blood Pressure.', \
                                       fhir_resource
                            elif most_latest_sys_bp <= second_most_latest_sys_bp and \
                                    most_latest_dias_bp > second_most_latest_dias_bp:
                                return 'Diastolic Blood Pressure has risen but not Systolic Blood Pressure.', \
                                       fhir_resource
                            else:
                                return 'Both Systolic and Diastolic Blood Pressures have not risen.', fhir_resource
                        else:
                            if most_latest_sys_bp < second_most_latest_sys_bp and \
                                    most_latest_dias_bp < second_most_latest_dias_bp:
                                return 'Both Systolic and Diastolic Blood Pressures have dropped.', fhir_resource
                            elif most_latest_sys_bp < second_most_latest_sys_bp and \
                                    most_latest_dias_bp >= second_most_latest_dias_bp:
                                return 'Systolic Blood Pressure has dropped but not Diastolic Blood Pressure.', \
                                       fhir_resource
                            elif most_latest_sys_bp >= second_most_latest_sys_bp and \
                                    most_latest_dias_bp < second_most_latest_dias_bp:
                                return 'Diastolic Blood Pressure has dropped but not Systolic Blood Pressure.', \
                                       fhir_resource
                            else:
                                return 'Both Systolic and Diastolic Blood Pressures have not dropped.', fhir_resource

                else:
                    return None, fhir_resource
            else:
                print('At least 2 observation instances should exist for the patient.')
                return None, fhir_resource
        else:
            return None, None
    else:
        return set_answers, fhir_resource


def get_trend_for_time_and_values(list_ans_times_and_values, set_answers, fhir_resource):
    if len(list_ans_times_and_values) >= 3:
        sorted_list_ans_times_and_values = \
            sorted(list_ans_times_and_values, key=lambda k: k['time'], reverse=True)
        sorted_three_items = sorted_list_ans_times_and_values[:3]
        if '/' in sorted_three_items[0]['value']:
            # Blood Pressure case where the values are like ['120/55', '105/65', '111/61']
            sorted_three_items_bp_values = [x['value'].split('/') for x in sorted_three_items]
            assert all(len(x) == 2 for x in sorted_three_items_bp_values), sorted_three_items
            systolic_values = [x[0] for x in sorted_three_items_bp_values]
            diastolic_values = [x[1] for x in sorted_three_items_bp_values]
            # Systolic trend
            if systolic_values[0] > systolic_values[1] > systolic_values[2]:
                systolic_trend = 'Increasing'
            elif systolic_values[2] > systolic_values[1] > systolic_values[0]:
                systolic_trend = 'Decreasing'
            else:
                systolic_trend = 'No trend in'
            # Diastolic trend
            if diastolic_values[0] > diastolic_values[1] > diastolic_values[2]:
                diastolic_trend = 'Increasing'
            elif diastolic_values[2] > diastolic_values[1] > diastolic_values[0]:
                diastolic_trend = 'Decreasing'
            else:
                diastolic_trend = 'No trend in'

            if systolic_trend == diastolic_trend:
                trend_message = systolic_trend
                if systolic_trend == 'No trend in':
                    trend_message = 'No trend'
                return trend_message, fhir_resource
            else:
                return '{} Systolic BP / {} Diastolic BP'.format(systolic_trend, diastolic_trend), fhir_resource
        if (float(sorted_three_items[0]['value']) > float(sorted_three_items[1]['value'])) and (
                float(sorted_three_items[1]['value']) > float(sorted_three_items[2]['value'])):
            return 'Increasing', fhir_resource
        elif (float(sorted_three_items[0]['value']) < float(sorted_three_items[1]['value'])) and (
                float(sorted_three_items[1]['value']) < float(sorted_three_items[2]['value'])):
            return 'Decreasing', fhir_resource
        else:
            return 'No trend', fhir_resource
    else:
        if len(set_answers) >= 3:
            if fhir_resource == 'Procedure':
                return 'Less than 3 observations have performed start date, trend cannot be determined.', fhir_resource
            elif fhir_resource == 'Observation':
                return 'Less than 3 observations have effective datetime or period, trend cannot be determined.', \
                       fhir_resource
            else:
                print('Trend not implemented for any resource other than Procedure and Observation.')
                return None, None
        else:
            return 'Less than 3 observations found, trend cannot be determined.', fhir_resource


def get_answer_trend_func(set_answers, fhir_resource):
    if set_answers is not None:
        if fhir_resource == 'Procedure':
            if len(set_answers) > 0:
                list_ans_times_and_values = []
                for ans in set_answers:
                    if ans['performed_date'] != 'NA':
                        performed_date = time_utils.get_final_date_time(ans['performed_date'])
                        obs_val = ans['observation_val']
                        list_ans_times_and_values.append({'time': performed_date, 'value': obs_val})
                    elif ans['performed_start_date'] != 'NA':
                        performed_start_date = time_utils.get_final_date_time(ans['performed_start_date'])
                        obs_val = ans['observation_val']
                        list_ans_times_and_values.append({'time': performed_start_date, 'value': obs_val})
                    else:
                        print("Effective datetime or period is not available for an observation "
                              "associated with the procedure.")

                return get_trend_for_time_and_values(list_ans_times_and_values, set_answers, fhir_resource)
            else:
                return None, fhir_resource
        elif fhir_resource == 'Observation':
            if len(set_answers) > 0:
                list_ans_times_and_values = []
                for ans in set_answers:
                    if ans['obs_effective_time'] != 'NA':
                        obs_effective_time = time_utils.get_final_date_time(ans['obs_effective_time'])
                        obs_val = ans['obs_val']
                        list_ans_times_and_values.append({'time': obs_effective_time, 'value': obs_val})
                    elif ans['obs_start_time'] != 'NA':
                        obs_start_time = time_utils.get_final_date_time(ans['obs_start_time'])
                        obs_val = ans['obs_val']
                        list_ans_times_and_values.append({'time': obs_start_time, 'value': obs_val})
                    else:
                        print("Effective datetime or period is not available for an observation.")

                return get_trend_for_time_and_values(list_ans_times_and_values, set_answers, fhir_resource)
            else:
                return None, fhir_resource
        else:
            return None, None
    else:
        return set_answers, fhir_resource


def get_answer_reason_func(answer, fhir_resource):
    if answer is not None:
        if fhir_resource in {'Procedure', 'MedicationOrder', 'CarePlan', 'Encounter'}:
            reason = answer['reason']
            if isinstance(reason, list):
                if len(reason) > 0:
                    reason = ', '.join(reason)
                else:
                    reason = 'No reason associated with the {} resource'.format(fhir_resource)
            return reason, fhir_resource
        else:
            return None, None
    return answer, fhir_resource


def get_answer_and_operation(list_set_answers_children):
    set_to_return = []
    if len(list_set_answers_children) == 4:
        fhir_resource = list_set_answers_children[1]
        set_answers_has_op = list_set_answers_children[0]
        item_to_check = list_set_answers_children[2]
        operation_to_perform_for_check = list_set_answers_children[3]
        second_item_to_check = None

    else:
        # First element - lambda results,
        # Second element - fhir resource,
        # Third element - first item to check (may be list, in case of time range, or a value,
        # Fourth element - operation to perform for checking (e.g. greater_than),
        # Fifth element - second item to check (a list of time range),
        # Sixth element - None
        set_answers_has_op = list_set_answers_children[0]
        fhir_resource = list_set_answers_children[1]
        item_to_check = list_set_answers_children[2]
        operation_to_perform_for_check = list_set_answers_children[3]
        second_item_to_check = list_set_answers_children[4]

    if set_answers_has_op is None and fhir_resource is None:
        return None, None

    elif set_answers_has_op is None and fhir_resource is not None:
        return None, fhir_resource

    else:
        if fhir_resource == 'Encounter':
            for item in set_answers_has_op:
                encounter_date = item['encounter_start_date']
                if encounter_date != 'NA':
                    encounter_date_updated = time_utils.get_final_date_time(encounter_date)
                    if isinstance(item_to_check, list):
                        if item_to_check[0] <= encounter_date_updated <= item_to_check[1]:
                            set_to_return.append(item)
                    elif operation_to_perform_for_check == 'at_location':
                        if item_to_check == item['encounter_location']:
                            set_to_return.append(item)

            return set_to_return, fhir_resource
        elif fhir_resource == 'Procedure':
            for item in set_answers_has_op:
                performed_start_date = item['performed_start_date']
                performed_end_date = item['performed_end_date']
                performed_date = item['performed_date']
                performed_date_updated = None
                performed_start_date_updated = None
                if performed_date != 'NA':
                    performed_date_updated = time_utils.get_final_date_time(performed_date)
                elif performed_start_date != 'NA':
                    performed_start_date_updated = time_utils.get_final_date_time(performed_start_date)

                if isinstance(item_to_check, list):
                    if performed_date_updated is not None:
                        if item_to_check[0] <= performed_date_updated <= item_to_check[1]:
                            set_to_return.append(item)
                    elif performed_start_date_updated is not None:
                        if item['proc_status'] == 'in-progress':
                            if performed_start_date_updated <= item_to_check[1]:
                                set_to_return.append(item)
                        else:
                            if performed_end_date != 'NA':
                                performed_end_date_updated = time_utils.get_final_date_time(performed_end_date)
                                if performed_start_date_updated <= item_to_check[1] \
                                        and item_to_check[0] <= performed_end_date_updated:
                                    set_to_return.append(item)
                elif operation_to_perform_for_check == 'at_location':
                    if item_to_check == item['procedure_location']:
                        set_to_return.append(item)
                elif operation_to_perform_for_check == 'greater_than':
                    if '/' not in item['observation_val']:
                        if float(item['observation_val']) > item_to_check:
                            set_to_return.append(item)
                    else:
                        print('Not implemented for Blood Pressure measurement.')
                elif operation_to_perform_for_check == 'less_than':
                    if '/' not in item['observation_val']:
                        if float(item['observation_val']) < item_to_check:
                            set_to_return.append(item)
                    else:
                        print('Not implemented for Blood Pressure measurement.')
                elif operation_to_perform_for_check == 'is_positive':
                    interpretation = item['observation_interpretation']
                    if interpretation == 'POS':
                        set_to_return.append(item)
                elif operation_to_perform_for_check == 'is_negative':
                    interpretation = item['observation_interpretation']
                    if interpretation == 'NEG':
                        set_to_return.append(item)

            return set_to_return, fhir_resource
        elif fhir_resource == 'Condition':
            for item in set_answers_has_op:
                if item['onset_datetime'] != 'None':
                    con_st_date = time_utils.get_final_date_time(item['onset_datetime'])
                if item['abatement_datetime'] != 'None':
                    con_end_date = time_utils.get_final_date_time(item['abatement_datetime'])
                if isinstance(item_to_check, list):
                    if item['problem_status'] == 'active' or (item['onset_datetime'] != 'None'
                                                              and item['abatement_datetime'] == 'None'):
                            if con_st_date <= item_to_check[1]:
                                set_to_return.append(item)
                    else:
                        if item['abatement_datetime'] != 'None':
                            if con_st_date <= item_to_check[1] and item_to_check[0] <= con_end_date:
                                set_to_return.append(item)
                elif operation_to_perform_for_check == 'is_healed':
                        if item['problem_status'] == 'resolved':
                            set_to_return.append(item)
                elif operation_to_perform_for_check == 'is_significant':
                    severity_display = item['severity'].lower()
                    if severity_display in {'moderate', 'moderate to severe', 'severe', 'fatal'}:
                        set_to_return.append(item)

            return set_to_return, fhir_resource
        elif fhir_resource == 'MedicationAdministration':
            for item in set_answers_has_op:
                med_admin_st_date = item['med_admin_start_date']
                med_admin_end_date = item['med_admin_end_date']
                med_admin_effective_date = item['med_admin_effective_date']
                med_admin_st_date_updated = None
                med_admin_effective_date_updated = None
                if med_admin_effective_date != 'NA':
                    med_admin_effective_date_updated = time_utils.get_final_date_time(med_admin_effective_date)
                elif med_admin_st_date != 'NA':
                    med_admin_st_date_updated = time_utils.get_final_date_time(med_admin_st_date)
                if isinstance(item_to_check, list):
                    if med_admin_effective_date_updated is not None:
                        if item_to_check[0] <= med_admin_effective_date_updated <= item_to_check[1]:
                            # Adding overlapping hours
                            item['overlapping_hrs_within_time_range'] = 'NA'
                            item['rate_med_admin'] = 'NA'
                            set_to_return.append(item)
                    elif med_admin_st_date_updated is not None:
                        if item['med_administration_status'] == 'in-progress' or (item['med_admin_start_date'] != 'NA'
                                                                  and item['med_admin_end_date'] == 'NA'):
                                if med_admin_st_date_updated <= item_to_check[1]:
                                    # Adding overlapping hours
                                    med_admin_end_date_updated = time_utils.current_time
                                    max_time_range_start_or_admin_start = max(med_admin_st_date_updated,
                                                                              item_to_check[0])
                                    if med_admin_end_date_updated >= item_to_check[1]:
                                        overlap_duration_in_hrs = \
                                            (item_to_check[1] -
                                             max_time_range_start_or_admin_start).total_seconds() / 3600
                                    else:
                                        overlap_duration_in_hrs = \
                                            (med_admin_end_date_updated -
                                             max_time_range_start_or_admin_start).total_seconds() / 3600

                                    duration = item['duration_med_admin']
                                    if item['total_med_administered_or_consumed'] != 'NA':
                                        rate_med_admin = float(item['total_med_administered_or_consumed']) / duration
                                    item['overlapping_hrs_within_time_range'] = overlap_duration_in_hrs
                                    item['rate_med_admin'] = rate_med_admin
                                    set_to_return.append(item)
                        else:
                            if med_admin_end_date != 'NA':
                                med_admin_end_date_updated = time_utils.get_final_date_time(med_admin_end_date)
                                if med_admin_st_date_updated <= item_to_check[1] and item_to_check[0] <= \
                                        med_admin_end_date_updated:
                                    # Adding overlapping hours
                                    max_time_range_start_or_admin_start = max(med_admin_st_date_updated,
                                                                              item_to_check[0])
                                    if med_admin_end_date_updated >= item_to_check[1]:
                                        overlap_duration_in_hrs = \
                                            (item_to_check[1] -
                                             max_time_range_start_or_admin_start).total_seconds() / 3600
                                    else:
                                        overlap_duration_in_hrs = \
                                            (med_admin_end_date_updated -
                                             max_time_range_start_or_admin_start).total_seconds() / 3600

                                    duration = item['duration_med_admin']
                                    if item['total_med_administered_or_consumed'] != 'NA':
                                        rate_med_admin = float(item['total_med_administered_or_consumed']) / duration
                                    item['overlapping_hrs_within_time_range'] = overlap_duration_in_hrs
                                    item['rate_med_admin'] = rate_med_admin
                                    set_to_return.append(item)

            return set_to_return, fhir_resource
        elif fhir_resource == 'Observation':
            if second_item_to_check is None:
                for item in set_answers_has_op:
                    date_time = None
                    effective_date_time_str = item['obs_effective_time']
                    if effective_date_time_str != 'NA':
                        date_time = time_utils.get_final_date_time(effective_date_time_str)
                    elif item['obs_start_time'] != 'NA':
                        date_time = time_utils.get_final_date_time(item['obs_start_time'])
                    if date_time is not None:
                        if isinstance(item_to_check, list):
                            if item_to_check[0] <= date_time <= item_to_check[1]:
                                set_to_return.append(item)
                        else:
                            if operation_to_perform_for_check == 'greater_than':
                                if '/' not in item['obs_val']:
                                    if float(item['obs_val']) > item_to_check:
                                        set_to_return.append(item)
                                else:
                                    print('Not implemented for Blood Pressure measurement.')
                            elif operation_to_perform_for_check == 'less_than':
                                if '/' not in item['obs_val']:
                                    if float(item['obs_val']) < item_to_check:
                                        set_to_return.append(item)
                                else:
                                    print('Not implemented for Blood Pressure measurement.')
                            elif operation_to_perform_for_check == 'is_normal':
                                interpretation = item['observation_interpretation']
                                if interpretation == 'N':
                                    set_to_return.append(item)
                            elif operation_to_perform_for_check == 'at_location':
                                if item_to_check == item['obs_location']:
                                    set_to_return.append(item)
                            elif operation_to_perform_for_check == 'is_large':
                                interpretation = item['observation_interpretation']
                                if interpretation in {'A', 'AA', 'H', 'HH', 'HU', '>'}:
                                    set_to_return.append(item)
                            elif operation_to_perform_for_check == 'is_serious':
                                # Ref: https://www.hl7.org/fhir/dstu2/valueset-observation-interpretation.html
                                interpretation = item['observation_interpretation']
                                if interpretation in {'AA', 'HH', 'HU'}:
                                    set_to_return.append(item)
                            elif operation_to_perform_for_check == 'is_significant':
                                interpretation = item['observation_interpretation']
                                if interpretation in {'D', 'U'}:
                                    set_to_return.append(item)
                            elif operation_to_perform_for_check == 'is_positive':
                                interpretation = item['observation_interpretation']
                                if interpretation == 'POS':
                                    set_to_return.append(item)
                            elif operation_to_perform_for_check == 'is_negative':
                                interpretation = item['observation_interpretation']
                                if interpretation == 'NEG':
                                    set_to_return.append(item)

                return set_to_return, fhir_resource
            else:
                for item in set_answers_has_op:
                    date_time = None
                    effective_date_time_str = item['obs_effective_time']
                    if effective_date_time_str != 'NA':
                        date_time = time_utils.get_final_date_time(effective_date_time_str)
                    elif item['obs_start_time'] != 'NA':
                        date_time = time_utils.get_final_date_time(item['obs_start_time'])
                    if date_time is not None:
                        if isinstance(second_item_to_check, list):
                            if second_item_to_check[0] <= date_time <= second_item_to_check[1]:
                                if operation_to_perform_for_check == 'greater_than':
                                    if '/' not in item['obs_val']:
                                        if float(item['obs_val']) > item_to_check:
                                            set_to_return.append(item)
                                    else:
                                        print('Not implemented for Blood Pressure measurement.')
                                elif operation_to_perform_for_check == 'less_than':
                                    if '/' not in item['obs_val']:
                                        if float(item['obs_val']) < item_to_check:
                                            set_to_return.append(item)
                                    else:
                                        print('Not implemented for Blood Pressure measurement.')
                        else:
                            print('Not implemented when the second item to check is not a time range.')
                return set_to_return, fhir_resource
        elif fhir_resource == 'DiagnosticReport':
            for item in set_answers_has_op:
                date_time = None
                effective_date_time_str = item['effective_date']
                if effective_date_time_str != 'NA':
                    date_time = time_utils.get_final_date_time(effective_date_time_str)
                if date_time is not None:
                    if isinstance(item_to_check, list):
                        if item_to_check[0] <= date_time <= item_to_check[1]:
                            set_to_return.append(item)
            return set_to_return, fhir_resource
        elif fhir_resource == 'Immunization':
            for item in set_answers_has_op:
                date_time = None
                effective_date_time_str = item['imm_datetime']
                if effective_date_time_str != 'NA':
                    date_time = time_utils.get_final_date_time(effective_date_time_str)
                if date_time is not None:
                    if isinstance(item_to_check, list):
                        if item_to_check[0] <= date_time <= item_to_check[1]:
                            set_to_return.append(item)
            return set_to_return, fhir_resource
        elif fhir_resource == 'CarePlan':
            for item in set_answers_has_op:
                start_time = None
                end_time = None
                start_time_str = item['start_date']
                end_time_str = item['end_date']
                if start_time_str != 'NA':
                    start_time = time_utils.get_final_date_time(start_time_str)
                if end_time_str != 'NA':
                    end_time = time_utils.get_final_date_time(end_time_str)
                if isinstance(item_to_check, list):
                    if start_time is not None and start_time <= item_to_check[1]:
                        if end_time is None or item_to_check[0] <= end_time:
                            set_to_return.append(item)
            return set_to_return, fhir_resource
        elif fhir_resource == 'MedicationOrder':
            for item in set_answers_has_op:
                eff_time = None
                start_time = None
                end_time = None
                eff_time_str = item['effective_date']
                start_time_str = item['effective_start_date']
                end_time_str = item['effective_end_date']
                if eff_time_str != 'NA':
                    eff_time = time_utils.get_final_date_time(eff_time_str)
                if start_time_str != 'NA':
                    start_time = time_utils.get_final_date_time(start_time_str)
                if end_time_str != 'NA':
                    end_time = time_utils.get_final_date_time(end_time_str)
                if isinstance(item_to_check, list):
                    if eff_time is not None and item_to_check[0] <= eff_time <= item_to_check[1]:
                        set_to_return.append(item)
                    elif start_time is not None and start_time <= item_to_check[1]:
                        if end_time is None or item_to_check[0] <= end_time:
                            set_to_return.append(item)
            return set_to_return, fhir_resource
        else:
            return None, None


import calendar
from datetime import timedelta, datetime

dict_time_ranges = dict()
current_time = datetime.now()


def get_overnight_time_range():
    yesterday = current_time - timedelta(days=1)
    yesterday = yesterday.strftime('%Y-%m-%d')
    overnight_start = datetime.strptime(yesterday + 'T20:00:00.000000', '%Y-%m-%dT%H:%M:%S.%f')
    overnight_end = datetime.strptime(current_time.strftime('%Y-%m-%d') + 'T06:00:00.000000', '%Y-%m-%dT%H:%M:%S.%f')
    return overnight_start, overnight_end


def get_since_last_night_time_range():
    yesterday = current_time - timedelta(days=1)
    yesterday = yesterday.strftime('%Y-%m-%d')
    last_night_start = datetime.strptime(yesterday + 'T20:00:00.000000', '%Y-%m-%dT%H:%M:%S.%f')
    end_date = str(current_time).split(' ')[0]
    end_time = str(current_time).split(' ')[1]
    if '.' in end_time:
        time_format = '%Y-%m-%dT%H:%M:%S.%f'
    else:
        time_format = '%Y-%m-%dT%H:%M:%S'
    end_date_time = datetime.strptime(end_date + 'T' + end_time, time_format)
    return last_night_start, end_date_time


def get_yesterday_time_range():
    yesterday = current_time - timedelta(days=1)
    yesterday = yesterday.strftime('%Y-%m-%d')
    yesterday_start = datetime.strptime(yesterday + 'T00:00:00.000000', '%Y-%m-%dT%H:%M:%S.%f')
    yesterday_end = datetime.strptime(yesterday + 'T23:59:59.000000', '%Y-%m-%dT%H:%M:%S.%f')
    return yesterday_start, yesterday_end


def get_today_time_range():
    today_date = str(current_time).split(' ')[0]
    today_time = str(current_time).split(' ')[1]
    if '.' in today_time:
        time_format = '%Y-%m-%dT%H:%M:%S.%f'
    else:
        time_format = '%Y-%m-%dT%H:%M:%S'
    today_start = datetime.strptime(today_date + 'T00:00:00.000000', '%Y-%m-%dT%H:%M:%S.%f')
    today_end = datetime.strptime(today_date + 'T' + today_time, time_format)
    return today_start, today_end


def get_last_n_hrs_time_range(n):
    n = int(n)
    last_n_hrs_date_time = current_time - timedelta(hours=n)
    st_date = str(last_n_hrs_date_time).split(' ')[0]
    st_time = str(last_n_hrs_date_time).split(' ')[1]
    end_date = str(current_time).split(' ')[0]
    end_time = str(current_time).split(' ')[1]
    if '.' in st_time:
        time_format = '%Y-%m-%dT%H:%M:%S.%f'
    else:
        time_format = '%Y-%m-%dT%H:%M:%S'
    last_n_hrs_start = datetime.strptime(st_date + 'T' + st_time, time_format)
    last_n_hrs_end = datetime.strptime(end_date + 'T' + end_time, time_format)
    return last_n_hrs_start, last_n_hrs_end


def get_last_week_time_range():
    last_week_date_time = current_time - timedelta(weeks=1)
    st_date = str(last_week_date_time).split(' ')[0]
    st_time = str(last_week_date_time).split(' ')[1]
    end_date = str(current_time).split(' ')[0]
    end_time = str(current_time).split(' ')[1]
    if '.' in st_time:
        time_format = '%Y-%m-%dT%H:%M:%S.%f'
    else:
        time_format = '%Y-%m-%dT%H:%M:%S'
    last_week_start = datetime.strptime(st_date + 'T' + st_time, time_format)
    last_week_end = datetime.strptime(end_date + 'T' + end_time, time_format)
    return last_week_start, last_week_end


def get_morning_time_range():
    today_date = str(current_time).split(' ')[0]
    morning_start = datetime.strptime(today_date + 'T04:00:00.000000', '%Y-%m-%dT%H:%M:%S.%f')
    morning_end = datetime.strptime(today_date + 'T09:59:59.000000', '%Y-%m-%dT%H:%M:%S.%f')
    return morning_start, morning_end


def get_since_year_range(year):
    begin = datetime(year, 1, 1)
    end_date = str(current_time).split(' ')[0]
    end_time = str(current_time).split(' ')[1]
    if '.' in end_time:
        time_format = '%Y-%m-%dT%H:%M:%S.%f'
    else:
        time_format = '%Y-%m-%dT%H:%M:%S'
    end_date_time = datetime.strptime(end_date + 'T' + end_time, time_format)
    return begin, end_date_time


def get_in_year_range(year):
    begin = datetime(year, 1, 1)
    end = datetime(year, 12, 31, 23, 59, 59)
    return begin, end


def get_in_month_year_range(month, year):
    _, num_days_in_month = calendar.monthrange(year, month)
    begin = datetime(year, month, 1)
    end = datetime(year, month, num_days_in_month, 23, 59, 59)
    return begin, end


def get_last_n_years(n):
    begin_date_time = current_time - timedelta(days=n*365)
    st_date = str(begin_date_time).split(' ')[0]
    st_time = str(begin_date_time).split(' ')[1]
    end_date = str(current_time).split(' ')[0]
    end_time = str(current_time).split(' ')[1]
    if '.' in st_time:
        time_format = '%Y-%m-%dT%H:%M:%S.%f'
    else:
        time_format = '%Y-%m-%dT%H:%M:%S'
    last_n_hrs_start = datetime.strptime(st_date + 'T' + st_time, time_format)
    last_n_hrs_end = datetime.strptime(end_date + 'T' + end_time, time_format)
    return last_n_hrs_start, last_n_hrs_end


def get_this_year_range():
    begin, end = get_in_year_range(current_time.year)
    return begin, end


def get_final_date_time(strs):
    if 'Z' in strs:
        strs = strs.replace('Z', '')
    if 'T' not in strs:
        time = datetime.strptime(strs, '%Y-%m-%d')
    else:
        if '+' in strs[-6] or '-' in strs[-6]:
            strs = strs[::-1].replace(':', '', 1)[::-1]
            try:
                offset = int(strs[-5:])
            except:
                print('Error')

            delta = timedelta(hours=offset / 100)
            if '.' in strs:
                time = datetime.strptime(strs[:-5], "%Y-%m-%dT%H:%M:%S.%f")
            else:
                time = datetime.strptime(strs[:-5], "%Y-%m-%dT%H:%M:%S")
            time -= delta
        else:
            if '.' in strs:
                time = datetime.strptime(strs, "%Y-%m-%dT%H:%M:%S.%f")
            else:
                time = datetime.strptime(strs, "%Y-%m-%dT%H:%M:%S")
    return time


def get_formatted_duration_string(num_hours, keep_first_n_components=3):
    if num_hours == 0:
        duration = '0 hours'
        return duration
    num_years = num_hours // (24 * 365)
    fraction_year_remain = num_hours % (24 * 365)
    num_months = fraction_year_remain // (24 * 30)
    fraction_month_remain = fraction_year_remain % (24 * 30)
    num_weeks = fraction_month_remain // (24 * 7)
    fraction_week_remain = fraction_month_remain % (24 * 7)
    num_days = fraction_week_remain // 24
    num_hours = fraction_week_remain % 24
    duration_components = []
    if num_years > 0:
        duration_components.append(int(num_years))
        duration_components.append('years' if num_years > 1 else 'year')
    if num_months > 0:
        duration_components.append(int(num_months))
        duration_components.append('months' if num_months > 1 else 'month')
    if num_weeks > 0:
        duration_components.append(int(num_weeks))
        duration_components.append('weeks' if num_weeks > 1 else 'week')
    if num_days > 0:
        duration_components.append(int(num_days))
        duration_components.append('days' if num_days > 1 else 'day')
    if num_hours > 0:
        duration_components.append(round(num_hours, 1))
        duration_components.append('hours' if num_hours > 1 else 'hour')
    duration_components = duration_components[:keep_first_n_components*2]
    duration = ' '.join([str(dc) for dc in duration_components])
    return duration

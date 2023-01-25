import requests
import datetime
import math
import pandas as pd
from numpy import mean
 
# Function to convert datetime to string. It is needed to specify dates in the thingspeak request.
def convert_date_to_string(date_time):
    format = "%Y-%m-%d%%20%H:%M:%S"  # The format
    datetime_str = datetime.datetime.strftime(date_time, format)
    return datetime_str

# Function to convert string to datetime. It is needed to translate dates from thingspeak into charts.
def convert_string_to_date(date_str):
    format_winter_time = "%Y-%m-%dT%H:%M:%S+01:00"
    format_summer_time = "%Y-%m-%dT%H:%M:%S+02:00"
    try:
        datetime_date = datetime.datetime.strptime(date_str, format_winter_time)
    except:
        datetime_date = datetime.datetime.strptime(date_str, format_summer_time)
    return datetime_date

# Second function to convert string to datetime. It is needed to translate dates from sliders into datetime. 
def convert_string_to_date2(date_str):
    format = "%Y-%m-%dT%H:%M"  # The format
    datetime_date = datetime.datetime.strptime(date_str, format)
    return datetime_date

def convert_string_to_number(s):
    try:
        return int(s)
    except ValueError:
        return float(s)

def get_data_from_thingspeak(field,start_date,end_date):
    data_list = (requests.get(f"https://thingspeak.com/channels/2007557/fields/{field}.json?start={start_date}&end={end_date}&timezone=Europe%2FWarsaw").json()['feeds'])
    # data_list.copy() == data_list[:]
    for data_dict in data_list[:]:
        del data_dict['entry_id']
        if str(data_dict[f'field{field}']) == "None":
            data_list.remove(data_dict)
            continue
        data_dict['created_at'] = convert_string_to_date(data_dict['created_at'])
        data_dict['value'] = convert_string_to_number(data_dict[f'field{field}'])
        del data_dict[f'field{field}']
    return data_list

# Function to prepare list with dictionaries with dates and values
def prepare_data(field,start,end):
    data = []
    step=datetime.timedelta(days=2)
    temp_start = start
    temp_end = temp_start + step
    # Thingspeak has a limit 8000 results, so the while loop enables getting more results in several requests
    while (temp_end < end):
        start_date = convert_date_to_string(temp_start)
        end_date = convert_date_to_string(temp_end)
        data = data + get_data_from_thingspeak(field,start_date,end_date)
        temp_start = temp_end
        temp_end = temp_start + step
    start_date = convert_date_to_string(temp_start)
    end_date = convert_date_to_string(end)
    data = data + get_data_from_thingspeak(field,start_date,end_date)
    if field != 7:
        data = limit_data(data)
    return data

# I assume that about 100 results are enough to draw graphs. If there are more than 100, arithmetic averages are calculated.
def limit_data(data_list):
    step = round(len(data_list) / 100)
    if step <= 1:
        return data_list
    limited_data_list = []
    for i in range(0,len(data_list),step):
        sum = 0
        datetime_list = []
        for j in range(0,step):
            try:
                datetime_list.append(data_list[i+j]['created_at'])
                sum += data_list[i+j]['value']   
            except IndexError:
                break
        pd_timestamp = pd.Series(datetime_list).mean()
        new_datetime = pd_timestamp.round('s').to_pydatetime()
        new_val = round(sum/len(datetime_list),2)
        limited_data_list.append({'created_at': new_datetime, 'value': new_val})
    return limited_data_list

def get_min_val(data):
    min_val = min(data)
    return min_val

def get_max_val(data):
    max_val = max(data)
    return max_val

def get_avg_val(data):
    avg_val = mean(data)
    return round(avg_val,2)

def get_amplitude_val(data):
    amp_val = get_max_val(data) - get_min_val(data)
    return round(amp_val,2)

field = 4
start = datetime.datetime(2023,1,5,11,0,0)
end = datetime.datetime(2023,1,6,10,4,0)
#data = prepare_data(field,start,end)
#print(data)


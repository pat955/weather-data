import requests
import json
import os
from datetime import datetime, date, timedelta

# Global variables
TODAY = date.today()
TOMORROW = TODAY + timedelta(days=1)
CLIENT_ID = 'weather-data/0.1 github.com/pat955'
HEADERS = {'User-Agent': 'My User Agent 1.0', 'From': 'github.com/pat955/weather-data'}
LOCFORECASTENDPOINT = 'https://api.met.no/weatherapi/locationforecast/2.0/compact'
ELEVATION_ENDPOINT = 'https://api.open-meteo.com/v1/elevation'
WD = 'weather_data.json'
OPTION_FORMAT = {'1': 'mm', '2': '°C', '3': 'm/s'}
NOMINATIM_ENDPOINT = 'https://nominatim.openstreetmap.org/search?format=geojson'

def main():
    """
    First we get what city the user want to get information about and what they want to know.
    Then we use that information to get coordinates, make sure we can use the cached data (if there is any).
    The data gets redone if it has expired or if the previous coordinates arent the same (different cities)
    Then we extract all the timeseries and remove todays
    Lastly we call week_print that prints each days_average and break down.
    """
    user_input_city, coord_params = input_loop()
    options = options_loop()
    
    clean_data = get_clean_weather_json(coord_params)
    all_timeseries = (get_all_timeseries(clean_data))
    relevant_timeseries = remove_todays_timeseries(all_timeseries)    

    week_print(all_timeseries, user_input_city, options)


def week_print(timeseries, user_input_city, options):
    """
    Print a weekly weather report for the specified city based on the provided time series data.

    :param timeseries: Relevant time series data for a week. Big list
    :param user_input_city: The name of the city for which the report is generated. Str
    :param options: List of settings for the report. List
    :return: None
    """
    current_date = TODAY
    complete_cohorts = 0 

    for i in range(1, 7+1):
        current_date = current_date + timedelta(days=1)
        day_rep, complete_cohorts = day_report(timeseries, complete_cohorts, options)
        day_average = {}
        print(f'Rapport {current_date.day}.{current_date.month}.{current_date.year} for {user_input_city.capitalize()}:')

        for hours_string, average in day_rep.items():
            day_average = compound_day_average(day_average, hours_string, average)
            result_string = f'kl.{hours_string} | '
            for opt, average in average.items():
                opt_format = OPTION_FORMAT[opt]
                result_string += f'{round(float(average), 1)} {opt_format} | '
            print(result_string)
        day_print(day_average)


def compound_day_average(day_average, hours_string, average): 
    """
    Compounds all averages into a day_average. Is used in a day loop.

    :param day_average: dict of the previous day averages, first round is an empty dict.
    :param hours_string: ex. 06-12. str
    :param average: current average.
    :return: day_average = {'1': x, '2': y}. Dict 
    """
    if day_average == {}:
        day_average = average
    day_average = {k: day_average.get(k, 0) + average.get(k, 0) for k in day_average}
    return day_average


def day_print(day_average):
    """
    Prints day averages in a pretty fashion.
    :day_average: key = index from options, value = compounded averages of all day cohorts. dict
    :return: None, prints
    """
    day_str = '| '
    for i, average in day_average.items():
        day_str += f'{round(average/4, 1)} '+ str(OPTION_FORMAT[i]) + ' | '
    print('.'*39)
    print(f'Snitt:   {day_str}')
    print('=======================================')


def option_results(next_timeserie, options):
    """
    Apply get function of options to averages
    :param next_timeserie: singular next timeserie. dict
    :return: Averages ex. {'1': 0.1, '3': 1.2} . dict
    """
    averages = {}
    possible_answers = {'1': get_rain, '2': get_temperature, '3': get_wind_speed}
    for opt, func in possible_answers.items():
        if opt in options:
            if opt not in averages:
                averages[opt] = 0
            averages[opt] += func(next_timeserie)
    return averages


def day_report(timeseries, complete_cohorts, options):
    """
    Possible answers are used to call function for each option
    6 hours is one cohort, data has 36 hours not incl today. if 6 cohort havent been used,
    averages are compounded and split into six until we reach 6 hours timeseries. 

    :param timeseries: all relevant timeseries. list
    :param complete_cohorts: current completed cohorts. int
    :param options: user options. list
    :return: day_dict, all 4 kohorts of the day split into timestamps and then into options. ex. {'00-06': {'2': 10, '3': 2}, ...}. dict 
    :return: complete cohorts. int
    """
    possible_answers = {'1': get_rain, '2': get_temperature, '3': get_wind_speed}
    day_dict = {}
    kohort_lengde = ('00-06', '06-12', '12-18', '18-24')           
    if complete_cohorts < 6:
        for quarter in range(4):
            for hour in range(6):
                next_timeserie = next_timeseries(timeseries)
                average = option_results(next_timeserie, options)
                    
            day_dict[kohort_lengde[quarter]] = divide_dict(average)
            
            complete_cohorts += 1
    else:
        for quarter in range(4):
            next_timeserie = next_timeseries(timeseries)
            average = option_results(next_timeserie, options)
            day_dict[kohort_lengde[quarter]] = divide_dict(average)
    return day_dict, complete_cohorts  


def divide_dict(dictionary, split_amount=6):
    for key, val in dictionary.items():
        dictionary[key] = val/6
    return dictionary


def input_loop():
    """
    Asks user for input, 'q' to quit. It checks if the city exists and if it does, keeps the response to avoid calling it again.
    :return: either reccursion because the city does not exist or return city name and full coordinates.
    """
    user_input = input('Skriv inn en by, pass på å skrive det riktig og at den eksisterer: ')
    if user_input == 'q':
        quit()
    response = check_if_city_exists(user_input)

    if response:
        return user_input, get_full_coordinates(response)
    print('Ikke eksisterende by, prøv igjen.\n')
    return input_loop()


def options_loop(lst=[]):
    """
    Get a valid option list, 'd' for done, 'a' for all and 'q' to exit script.
    :param lst: defaults to empty list, can be used to update settings
    :return: either reccursion if invalid answer or list of setting. list
    """
    possible_answers = ['1', '2', '3']
    if lst == possible_answers:
        return list(set(lst))
    answer = input('Which of these would you like to enable?\n1. Rain\n2. Temperature\n3. Windspeed\nPress a number or "a" for all or "d" when done: ')
    if answer == 'q':
        exit()
    elif answer == 'a':
        return possible_answers
    elif answer == 'd':
        if lst == []:
            print('\nCan\'t be done with no options, press "a" for all.')
            return options_loop([])
        return list(set(lst))
    elif answer in possible_answers:
        lst.append(answer)
        print(lst)
    return options_loop(lst)


def get_full_coordinates(nominatim_response):
    """
    Get latitude, longitude and altitude. Altitude requires another API so it has to be separated.
    :param nominatim_response: to avoid calling nminatim several times, if the city exists call get full coordinates on the response. str
    :return: all coordinates needed for accurate locationforecast. ex. {'lat': 60, 'lon': 11, 'altitude': 151 }
    """
    lat, lon = get_lat_and_lon(nominatim_response)
    lat, lon = round(float(lat)), round(float(lon))
    return {'lat': lat, 'lon': lon, 'altitude': get_altitude({'latitude': lat, 'longitude': lon})}
    

def get_altitude(coordinates):
    elevation_response = requests.get(ELEVATION_ENDPOINT, coordinates)
    elevation = (elevation_response.json())['elevation'][0]
    return int(elevation)


def get_lat_and_lon(response):
    coords = [float(num) for num in response.json()['features'][0]['geometry']['coordinates']]
    return coords[1], coords[0]


def get_clean_weather_json(coordinates):
    """
    Checks if file exists, is expired, empty and has the same coordinates as previous call. If so reuse data.
    :param coordinates: coordinates used for requests and comparison. dict
    :return: loaded json file. dict
    """
    if os.path.exists(WD):
        expired = get_expiration() > datetime.now()
        if os.path.getsize(WD) <= 3 or expired:
            print('expired: ', expired)
            os.remove(WD)
            make_new_weather_data_file(coordinates)
        else:
            with open(WD, "r") as file:
                json_coords = json.load(file)['geometry']['coordinates']
                if json_coords != [coordinates['lon'], coordinates['lat'], coordinates['altitude']]:
                    print('changed', json_coords, coordinates)
                    make_new_weather_data_file(coordinates)
    else:
        make_new_weather_data_file(coordinates)

    with open("weather_data.json", "r") as opened_file:
        return json.load(opened_file)


def make_new_weather_data_file(coordinates):
    """
    Make new request, add headers and response data to json file. local caching and for speed.
    :param coordinates: coordinates of dict to use as parameter for met.no
    :return: None
    """
    response = make_request(LOCFORECASTENDPOINT, True, coordinates)
    headers = response.headers
    request_data = response.json()
    request_data['headers'] = dict(headers)
    with open("weather_data.json", "w") as file:
        json.dump(request_data, file)


def check_if_city_exists(city):
    """
    :param city: city name. str
    :return: False if it doesn't exist or response if it does to avoid a second call. bool/response 
    """
    response = make_request(NOMINATIM_ENDPOINT, True, {'city': city})
    if len(response.text) <= 124:
        return False
    return response
    

def get_temperature(timeserie):
    return timeserie['data']['instant']['details']['air_temperature']


def get_wind_speed(timeserie):
    return timeserie['data']['instant']['details']['wind_speed']


def get_rain(timeserie):
    """
    Get predicted rain amount. No rain data in instant so next, 1 hour, 6 and twelve are those we can use.
    :param timeserie: a timeserie. dict
    :return: either an amount, or 0.0 if a value can't be found. float
    """
    time_intervals = ['next_1_hours', 'next_6_hours', 'next_12_hours']
    for interval in time_intervals:
        try: 
            return timeserie['data'][interval]['details']['precipitation_amount']
        except:
            pass
    return 0.0
    

def make_request(endpoint, with_headers, params={}):
    """
    :param endpoint: endpoint, url. str
    :param with_headers: bool 
    :param params: parameters for request. dict 
    :return: response. response
    """
    headers = HEADERS if with_headers else {}
    auth = (CLIENT_ID, '') if with_headers else None
    response = requests.get(endpoint, params=params, headers=headers, auth=auth)
    error_handling(response.status_code)
    return response


def error_handling(status_code):
    """
    Simple error handling
    :param status_code: status code from response. int
    :return: True if ok or prints error message and recalls main.
    """
    if status_code == requests.codes.ok:
        return True
    else:
        print('Error! Status Code:', status_code, '\nPlease retry. 5XX errors are out of our control.')
        main()


def get_all_timeseries(data):
    return data['properties']['timeseries']


def remove_todays_timeseries(timeseries):
    while datetime.strptime(timeseries[0]['time'], '%Y-%m-%dT%H:%M:%SZ').date() == TODAY:
        timeseries.pop(0)
    return timeseries


def next_timeseries(timeseries):
    return timeseries.pop(0)


def get_expiration():
    with open(WD, "r") as file:
        expiration = json.load(file)['headers']['Expires']
    return datetime.strptime(expiration, '%a, %d %b %Y %H:%M:%S %Z')


def quit():
    print('Quitting...')
    exit()


main()
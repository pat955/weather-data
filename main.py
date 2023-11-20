import requests
import json
import os
from datetime import datetime, date, timedelta

TODAY = date.today()
TOMORROW = TODAY + timedelta(days=1)
CLIENT_ID = 'weather-data/0.1 github.com/pat955'
HEADERS = {'User-Agent': 'My User Agent 1.0', 'From': 'github.com/pat955/weather-data'}
LOCFORECASTENDPOINT = 'https://api.met.no/weatherapi/locationforecast/2.0/compact'
ELEVATION_ENDPOINT = 'https://api.open-meteo.com/v1/elevation'
OSLO_COORDINATES = {'lat': '60', 'lon': '10', 'altitude': '148'}
WD = 'weather_data.json'
OPTION_FORMAT = {'1': 'mm', '2': '°C', '3': 'm/s'}



# Se hva de har å si om last_modified i metno og hvordan jeg skal bruke det.

def main():
    user_input_city = input_loop()
    options = options_loop()
    
    coord_params = get_full_coordinates(user_input_city)
    
    clean_data = get_clean_weather_json(coord_params)
    all_timeseries = get_timeseries(clean_data)
    all_timeseries = remove_todays_timeseries(all_timeseries)
    
    
    current_date = TOMORROW
    fullførte_kohorter = 0 

    for i in range(1, 7+1):
        day_rep, fullførte_kohorter = day_report(all_timeseries, fullførte_kohorter, options)
        dags_gjennomsnitt = {}
        
        print(f'Rapport {current_date.day}.{current_date.month}.{current_date.year} for {user_input_city.capitalize()}:')
        
        for hours_string, gjennomsnitter in day_rep.items():
            string = f'kl.{hours_string} | '
            for opt, gjennomsnitt in gjennomsnitter.items():
                opt_format = OPTION_FORMAT[opt]
                string += f'{round(float(gjennomsnitt),1)} {opt_format} | '
            print(string)
            #if total_gjennomsnitter == {}:
             #   total_gjennomsnitter = gjennomsnitter
            #total_gjennomsnitter = {k: total_gjennomsnitter.get(k, 0) + gjennomsnitter.get(k, 0) for k in total_gjennomsnitter}
        
        #print(f'Gjennomsnittstemperatur er {round(total_gjennomsnitter/4, 2)}°C')
        print('======================================')
        current_date = current_date + timedelta(days=1)
        
def day_report(timeseries, fullførte_kohorter, options):
    possible_answers = {'1': get_rain, '2': get_temperature, '3': get_wind_speed}
    day_dict = {}
    kohort_lengde = ('00-06', '06-12', '12-18', '18-24')           

    if fullførte_kohorter < 6:

        for quarter in range(4):
            gjennomsnitt = {}
            for hour in range(6):
                
                next_timeserie = next_timeseries(timeseries)
                for opt, func in possible_answers.items():

                    if opt in options:
                        if opt not in gjennomsnitt:
                            gjennomsnitt[opt] = 0
                        gjennomsnitt[opt] += func(next_timeserie)
                    
                
            day_dict[kohort_lengde[quarter]] = del_dict(gjennomsnitt)
            
            fullførte_kohorter += 1
    else:
        for quarter in range(4):
            gjennomsnitt = {}
            next_timeserie = next_timeseries(timeseries)
            for opt, func in possible_answers.items():
                if opt in options:
                    if opt not in gjennomsnitt:
                        gjennomsnitt[opt] = 0
                    gjennomsnitt[opt] += func(next_timeserie)
            
            day_dict[kohort_lengde[quarter]] = del_dict(gjennomsnitt)
    return day_dict, fullførte_kohorter  

def del_dict(dictionary, split_amount=6):
    for key, val in dictionary.items():
        dictionary[key] = val/6
    return dictionary


def day_report1(timeseries, fullførte_kohorter):
    day_dict = {}
    kohort_lengde = ('00-06', '06-12', '12-18', '18-24', '00-06', '06-12')
  
    if fullførte_kohorter < 6:
        for quarter in range(4):
            gjennomsnitt_temp = 0
            for hour in range(6):
                next_timeserie = next_timeseries(timeseries)
                gjennomsnitt_temp += get_temperature(next_timeserie)
                print(get_rain(next_timeserie))
                
            day_dict[kohort_lengde[quarter]] = gjennomsnitt_temp/6
            fullførte_kohorter += 1
    else:
        for quarter in range(4):
            day_dict[kohort_lengde[quarter]] = get_temperature(next_timeseries(timeseries))
    return day_dict, fullførte_kohorter

def options_loop(lst=[]):
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

    if answer in possible_answers:
        
        lst.append(answer)
        print(lst)
    return options_loop(lst)

def log(*args, **kwargs):
    pass

def get_headers(coordinates):
    lat, lon = coordinates['lat'], coordinates['lon']
    headers_endpoint = f'https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={lat}&lon={lon}'
    return requests.get(url=headers_endpoint, headers=HEADERS, auth=(CLIENT_ID, '')).headers
   
def get_full_coordinates(user_input):
    nomi_endpoint = f'https://nominatim.openstreetmap.org/search?city={user_input}&format=geojson'
    lat, lon = get_coordinates(make_request(nomi_endpoint))
    return {'lat': round(float(lat), 2), 'lon': round(float(lon), 2), 'altitude': get_altitude({'latitude': lat, 'longitude': lon})}
    
def get_altitude(coordinates):
    elevation_response = requests.get(ELEVATION_ENDPOINT, coordinates)
    elevation = (elevation_response.json())['elevation'][0]
    return int(elevation)

def get_clean_weather_json(coordinates):
    if os.path.exists(WD):
        if os.path.getsize(WD) <= 3 or get_expiration() > datetime.now():
            os.remove(WD)
            make_new_weather_data_file(coordinates)
        else:
            with open(WD, "r") as file:
                json_coords = json.load(file)['geometry']['coordinates']
                if json_coords != [coordinates['lon'], coordinates['lat'], coordinates['altitude']]:
                    print(f'coordinates did not match: {json_coords} /= [',coordinates['lon'], coordinates['lat'],coordinates['altitude'], ']')
                    make_new_weather_data_file(coordinates)
    else:
        make_new_weather_data_file(coordinates)

    with open("weather_data.json", "r") as opened_file:
        return json.load(opened_file)

def make_new_weather_data_file(coordinates):
    response = make_request(LOCFORECASTENDPOINT, coordinates)
    headers = response.headers
    request_data = response.json()
    request_data['headers'] = dict(headers)
    with open("weather_data.json", "w") as file:
        json.dump(request_data, file)

def input_loop():
    user_input = input('Skriv inn en by, pass på å skrive det riktig og at den eksisterer: ')
    if user_input == 'q':
        exit()
    elif user_input == 'c':
        os.remove('weather_data.json')
        return input_loop()
    
    if check_if_city_exists(user_input):
        return user_input
    print('Ikke eksisterende by, prøv igjen.\n')
    return input_loop()

def get_coordinates(response):
    # round 2
    data = response.json()
    rounded_coords = [float(round(num)) for num in data['features'][0]['geometry']['coordinates']]
    return rounded_coords[1], rounded_coords[0]

def check_if_city_exists(city):
    url = f'https://nominatim.openstreetmap.org/search?city={city}&format=geojson'
    response = requests.get(url=url, headers=HEADERS, auth=(CLIENT_ID, ''))
    return not len(response.text) <= 124
    
def get_temperature(timeserie):
    return timeserie['data']['instant']['details']['air_temperature']

def get_rain(timeserie):
    try:
        return timeserie['data']['next_1_hours']['details']['precipitation_amount']
    except:
        try:
            return timeserie['data']['next_6_hours']['details']['precipitation_amount']
        except:
            try:
                return timeserie['data']['next_12_hours']['details']['precipitation_amount']
            except:
                return 0.0

def get_wind_speed(timeserie):
    return timeserie['data']['instant']['details']['wind_speed']
    
def get_timeseries(data):
    return data['properties']['timeseries']

def remove_todays_timeseries(timeseries):
    while datetime.strptime(timeseries[0]['time'], '%Y-%m-%dT%H:%M:%SZ').date() == TODAY:
        t = timeseries.pop(0)
    return timeseries

def next_timeseries(timeseries):
    return timeseries.pop(0)

def get_expiration():
    with open(WD, "r") as file:
        expiration = json.load(file)['headers']['Expires']
    return datetime.strptime(expiration, '%a, %d %b %Y %H:%M:%S %Z')

def get_last_modified():
    with open(WD, "r") as file:
        modified = json.load(file)['headers']['Last-Modified']
    return datetime.strptime(modified, '%a, %d %b %Y %H:%M:%S %Z')

def make_request_without_headers(endpoint, params=None):
    if params == None:
        return requests.get(endpoint)
    return requests.get(endpoint, params)

def make_request(endpoint, params=None):
    if params == None:
        return requests.get(endpoint, headers=HEADERS, auth=(CLIENT_ID, ''))
    return requests.get(endpoint, params, headers=HEADERS, auth=(CLIENT_ID,''))
    

main()
# -A for authentication, -i to display body and header -I for only the latter. -s to not display progressbar(?) jsonpp to make it readable
# curl -A "weather-data/0.1 github.com/pat955" -i -s 'https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=51.5&lon=0'|json_pp

# Remove json_pp if using -I

# curl -A "weather-data/0.1 github.com/pat955" -i -H 'If-Modified-Since: Tue, 16 Jun 2020 12:11:59 GMT' \
#  -s 'https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=51.5&lon=0'
"""
def status_code_200(response):
    if response.status_code == 200:
        return True 
    
    print('Error! Returned status code %s' % request_data.status_code)
    print('Message: %s' % json['error']['message'])
    print('Reason: %s' % json['error']['reason'])
    return False
"""

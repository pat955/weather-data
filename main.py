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
OSLO_COORDINATES = {'lat': '60', 'lon': '11', 'altitude': '148'}

# Se hva de har å si om last_modified i metno og hvordan jeg skal bruke det.
# last_modified = datetime.strptime(get_last_modified(data_headers), '%a, %d %b %Y %H:%M:%S %Z')
# request_data = get_clean_weather_json(expires, coord_params)
    

def main():
    user_input_city = input_loop()
    
    coord_params = get_full_coordinates(user_input_city)
    data_headers = get_headers(coord_params)
    expires = datetime.strptime(get_expiration(data_headers), '%a, %d %b %Y %H:%M:%S %Z')

    all_timeseries = get_timeseries(get_clean_weather_json(expires, coord_params))
    print(f'Temperatur i morgen for {user_input_city.capitalize()} {TOMORROW.day}.{TOMORROW.month}.{TOMORROW.year}:')
    gjennomsnitt_temp, rang = 0, 24
    kohort = None
    for i in range(1, rang+1):
        if i % 6 == 0:
            pass
        date, hours, temperature = get_temperature(next_timeseries(all_timeseries))
        gjennomsnitt_temp += temperature
        
        print(f'kl.{hours[:2]}: {round(float(temperature))}°C')
    print(f'Gjennomsnittstemperatur er {round(gjennomsnitt_temp/rang, 2)}°C!')

def log(*args, **kwargs):
    pass

def get_headers(coordinates):
    lat, lon = coordinates['lat'], coordinates['lon']
    headers_endpoint = f'https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={lat}&lon={lon}'
    return requests.head(url=headers_endpoint, headers=HEADERS, auth=(CLIENT_ID, '')).headers
   

def get_full_coordinates(user_input):
    nomi_endpoint = f'https://nominatim.openstreetmap.org/search?city={user_input}&format=geojson'
    lat, lon = get_coordinates(make_request(nomi_endpoint))
    return {'lat': int(lat), 'lon': int(lon), 'altitude': get_altitude({'latitude': lat, 'longitude': lon})}
    
def get_altitude(coordinates):
    elevation_response = requests.get(ELEVATION_ENDPOINT, coordinates)
    elevation = (elevation_response.json())['elevation'][0]
    return int(elevation)

def get_clean_weather_json(expires, coordinates):
    wd = 'weather_data.json'
    if os.path.exists(wd):
        
        if os.path.getsize(wd) <= 3 or expires > datetime.now():
            os.remove(wd)
            make_new_weather_data_file(coordinates)
        else:
            with open(wd, "r") as file:
                json_coords = json.load(file)['geometry']['coordinates']
                if json_coords != [coordinates['lon'], coordinates['lat'], coordinates['altitude']]:
                    print(f'coordinates did not match: {json_coords} /= [', coordinates['lon'], coordinates['lat'], coordinates['altitude'])
                    make_new_weather_data_file(coordinates)
    else:
        make_new_weather_data_file(coordinates)

    with open("weather_data.json", "r") as opened_file:
        return json.load(opened_file)

def make_new_weather_data_file(coordinates):
    request_data = make_request(LOCFORECASTENDPOINT, coordinates)
    with open("weather_data.json", "w") as file:
        json.dump(request_data.json(), file)

def input_loop():
    user_input = input('Skriv inn en by, pass på å skrive det riktig og at den eksisterer: ')
    if user_input == 'q':
        exit()
    elif user_input == 'c':
        os.remove('weather_data.json')
    
    if check_if_city_exists(user_input):
        return user_input
    print('Ikke eksisterende by, prøv igjen.\n')
    return input_loop()

def get_coordinates(response):
    data = response.json()
    rounded_coords = [float(round(num)) for num in data['features'][0]['geometry']['coordinates']]
    return rounded_coords[1], rounded_coords[0]

def check_if_city_exists(city):
    url = f'https://nominatim.openstreetmap.org/search?city={city}&format=geojson'
    response = requests.get(url=url, headers=HEADERS, auth=(CLIENT_ID, ''))
    return not len(response.text) <= 124

def make_request_without_headers(endpoint, params=None):
    if params == None:
        return requests.get(endpoint)
    return requests.get(endpoint, params)

def make_request(endpoint, params=None):
    if params == None:
        return requests.get(endpoint, headers=HEADERS, auth=(CLIENT_ID, ''))
    return requests.get(endpoint, params, headers=HEADERS, auth=(CLIENT_ID,''))
    
def get_expiration(headers):
    return headers['Expires']

def get_last_modified(headers):
    return headers['Last-Modified']
    
def get_temperature(timeserie):
    time_object = datetime.strptime(timeserie['time'], '%Y-%m-%dT%H:%M:%SZ')
    
    total_time = f'{time_object}'
    hours = total_time[11:-3]
    date = total_time[:10]
    
    temperature = timeserie['data']['instant']['details']['air_temperature']
    return date, hours, temperature


def get_timeseries(data):
    return data['properties']['timeseries']


def next_timeseries(timeseries, skip_today=True):
    if not skip_today:
        return timeseries.pop(0)
    count = -1
    for timeserie in timeseries:
        count += 1
        if datetime.strptime(timeserie['time'], '%Y-%m-%dT%H:%M:%SZ').date() == TODAY:
            continue
        return timeseries.pop(count)


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

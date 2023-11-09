import requests
import json
import os
from datetime import datetime, date

TODAY = date.today()
CLIENT_ID = 'weather-data/0.1 github.com/pat955'
HEADERS = {'User-Agent': 'My User Agent 1.0', 'From': 'github.com/pat955/weather-data'}
LOCFORECASTENDPOINT = 'https://api.met.no/weatherapi/locationforecast/2.0/compact'
oslo_coordinates = {'lat': '60', 'lon': '11', 'altitude': '148'}

def main():
    user_input_city = input_loop()

    nomi_endpoint = f'https://nominatim.openstreetmap.org/search?city={user_input_city}&format=geojson'
    city_data = requests.get(nomi_endpoint, headers=HEADERS, auth=(CLIENT_ID, ''))
    city_coordinates = get_coordinates(city_data)
    coords = {'lat': city_coordinates[0], 'lon': city_coordinates[1]}

    #print(get_coordinates(city_data.json()))
    endpoint = 'https://api.met.no/weatherapi/locationforecast/2.0/compact'
    headers_endpoint = 'https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=60&lon=11'
    data_headers = requests.head(url=headers_endpoint, headers=HEADERS, auth=(CLIENT_ID, '')).headers

    expires = datetime.strptime(get_expiration(data_headers), '%a, %d %b %Y %H:%M:%S %Z')
    last_modified = datetime.strptime(get_last_modified(data_headers), '%a, %d %b %Y %H:%M:%S %Z')

    # Check if same area 
    request_data = get_clean_weather_json(expires, last_modified, oslo_coordinates)
    print(request_data)
    
    all_timeseries = get_timeseries(request_data)
    print('Temperatur i morgen for Oslo:')
    gjennomsnitt_temp, rang = 0, 5
    for i in range(rang):
        
        date, hours, temperature = get_temperature(next_timeseries(all_timeseries))
        gjennomsnitt_temp += temperature
        print(f'{date} kl. {hours}: {temperature}°C')
    print(f'Gjennomsnittstemperatur er {gjennomsnitt_temp/rang:.2f}°C!')
  
def get_clean_weather_json(expires, last_modified, coordinates):
    wd = 'weather_data.json'
    if os.path.exists(wd):
        if os.path.getsize(wd) <= 2 or expires < last_modified:
            make_new_weather_data_file(coordinates)
        else:
            with open("weather_data.json", "r") as file:
                json_coords = json.load(file)['geometry']['coordinates']
                if json_coords != coordinates:
                    make_new_weather_data_file(coordinates)
    else:
        make_new_weather_data_file(coordinates)

    with open("weather_data.json", "r") as opened_file:
        return json.load(opened_file)

def make_new_weather_data_file(coordinates):
    os.remove('weather_data.json')
    request_data = make_request_data(LOCFORECASTENDPOINT, coordinates)
    with open("weather_data.json", "w") as file:
        json.dump(request_data.json(), file)

def input_loop():
    user_input = input('Skriv inn en by, pass på å skrive det riktig og at den eksisterer: ')
    if user_input == 'q':
        exit()

    if check_if_city_exists(user_input):
        return user_input
    print('Ikke eksisterende by, prøv igjen.\n')
    return input_loop()

def get_coordinates(response):
    data = response.json()
    return [round(num, 2) for num in data['features'][0]['geometry']['coordinates']]

def check_if_city_exists(city):
    url = f'https://nominatim.openstreetmap.org/search?city={city}&format=geojson'
    response = requests.get(url=url, headers=HEADERS, auth=(CLIENT_ID, ''))
    if len(response.text) <= 124:
        return False
    return True

def make_request_data(endpoint, params):
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

def status_code_200(response):
    if response.status_code == 200:
        return True 
    
    print('Error! Returned status code %s' % request_data.status_code)
    print('Message: %s' % json['error']['message'])
    print('Reason: %s' % json['error']['reason'])
    return False

main()
# -A for authentication, -i to display body and header -I for only the latter. -s to not display progressbar(?) jsonpp to make it readable
# curl -A "weather-data/0.1 github.com/pat955" -i -s 'https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=51.5&lon=0'|json_pp

# Remove json_pp if using -I

# curl -A "weather-data/0.1 github.com/pat955" -i -H 'If-Modified-Since: Tue, 16 Jun 2020 12:11:59 GMT' \
#  -s 'https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=51.5&lon=0'


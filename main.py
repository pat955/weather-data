import requests
import json

client_id = 'weather-data/0.1 github.com/pat955'
endpoint = 'https://api.met.no/weatherapi/locationforecast/2.0/compact'

headers = {
    'User-Agent': 'My User Agent 1.0',
    'From': 'github.com/pat955/weather-data' 
}

oslo_coordinates = {
    'lat': '60',
    'lon': '11',
    'altitude': '148',
}


r = requests.get(endpoint, oslo_coordinates, headers=headers, auth=(client_id,''))
request_data = r
def get_temperature():
    pair_results

def parse_json(data, args):
    loaded_data = json.loads(data)
    res = loaded_data[args[0]]

    for argument in args[1:]:
        res = res[argument]
        
    return res
    
if r.status_code == 200:
    print('Data retrieved!')
    data = r.text
    print(data)

else:
    print('Error! Returned status code %s' % r.status_code)
    print('Message: %s' % json['error']['message'])
    print('Reason: %s' % json['error']['reason'])




# -A for authentication, -i to display body and header -I for only the latter. -s to not display progressbar(?) jsonpp to make it readable
# curl -A "weather-data/0.1 github.com/pat955" -i -s 'https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=51.5&lon=0'|json_pp

# Remove json_pp if using -I
# curl -A "weather-data/0.1 github.com/pat955" -I -s 'https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=51.5&lon=0'

# curl -A "weather-data/0.1 github.com/pat955" -i -H 'If-Modified-Since: Tue, 16 Jun 2020 12:11:59 GMT' \
#  -s 'https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=51.5&lon=0'


# curl -A "weather-data/0.1 github.com/pat955" -s 'https://api.met.no/weatherapi/radar/2.0/available.json?type=lx_reflectivity&area=central_norway'|json_pp
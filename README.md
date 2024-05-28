# Weather data CLI
This project is mainly used as a learning tool for APIs and improving my python skills. Uses [met.no API](https://api.met.no/) for data. [Meteo Elevation API](https://api.open-meteo.com/v1/elevation') for elevation to more accurately get weather data from met.no.

## How to use
In terminal, with git and python installed:
```
git clone https://github.com/pat955/weather-data
cd weather-data
python main.py
```

It should look like this:
```
Skriv inn en by, pass på å skrive det riktig og at den eksisterer: vilnius
Hvilken av disse vil du aktivere?
1. Regnmengde
2. Temperatur
3. Vindhastighet
Press et nummer for innstillingen eller "a" for alle, "d" når ferdig: a
Rapport 29.5.2024 for Vilnius:
kl.00-06 | 0.0 mm | 17.3 °C | 2.0 m/s | 
kl.06-12 | 0.0 mm | 25.6 °C | 2.5 m/s | 
kl.12-18 | 0.0 mm | 20.1 °C | 0.7 m/s | 
kl.18-24 | 0.0 mm | 14.7 °C | 2.1 m/s | 
.......................................
Snitt:   | 0.0 mm | 23.8 °C | 2.3 m/s | 
=======================================
Rapport 30.5.2024 for Vilnius:
kl.00-06 | 0.0 mm | 18.4 °C | 1.7 m/s | 
kl.06-12 | 0.0 mm | 26.8 °C | 0.7 m/s | 
kl.12-18 | 0.0 mm | 21.9 °C | 2.0 m/s | 
kl.18-24 | 3.3 mm | 20.0 °C | 1.3 m/s | 
.......................................
Snitt:   | 0.8 mm | 26.4 °C | 1.8 m/s | 
...
```
It will show a total of 7 days.

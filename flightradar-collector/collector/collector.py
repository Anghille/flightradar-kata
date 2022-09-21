from FlightRadar24.api import FlightRadar24API, Flight
from datetime import datetime
from time import sleep
import json




FR_API = FlightRadar24API()


def write_file(data: dict[dict]) -> None:
    """ 
    Write a dict of dict as a Json file to the path /input

    parameter:
    ---------

    data: dict[dict]
      The dictionnary containing all informations for each flight, the flight
      id beeing the primary key of the dict

    return:
    --------
    None
    """
    with open(f"C:/users/pierr/desktop/flight_data_{datetime.strftime(datetime.now(), '%Y-%m-%d_%H%M%S')}.json", "w") as f:
        for line in data:
            f.write(str(line).replace("N/A", "null")+"\n")

def get_airline_name(airline_iata: str, airline_icao: str, airlines: dict) -> str:
    """
    Return the icao or the iata flight airline code, depending of the 
    airline code returned by the api

    parameters:
    -----------

    airline_iata: str
       The 2 charaters code identifying the airline of the aircraft

    airline_icao: str
       The 3 characters code identifying the airline of the aircraft

    return:
    --------

    airline_icao|airline_iata: str
      Depending of the airlines, icao or iata code must be used
      to identify the airline. return the corresponding code to
      correctly identify the airline
    """
    if airline_icao in airlines.keys():
        return airlines[airline_icao]
    elif airline_iata in airlines.keys():
        return airlines[airline_iata]
    else:
        return "N/A"

def get_airport_data(airport_iata: str, airports: dict[dict]) -> dict:
    """
    Return None if the airport is not found in the 
    FlightRadar24 snapshot

    parameters:
    -------------
    airport_iata; str
      the airtport iata code which consist of 3 characters

    aiports: dict[dict]
      dict of airports and their coordinate, name and altitude

    return:
    -------
    airports[key]: dict|str
      Airports data encapsulated as a dict, such as longitude, latitude,
      altitude, name...
      
    """
    if airport_iata in airports.keys():
        return airports[airport_iata]
    return "N/A"

def extract_airports() -> dict[dict]:
    """
    Extract a snapshot of all the airports identified by Flightradar24

    parameters:
    ---------
    None

    return:
    -------

    airports: dict[dict]
      A json-like formated data containing airports name, latitude, longitude, iata code,
      country and altitude. Airport iata code is used as primary key
    """
    airports = {x["iata"]:x for x in FR_API.get_airports()}
    airports["N/A"] = "N/A"
    return airports


def extract_airlines() -> dict:
    """
    Extract a snapshot of all the airlines identified by Flightradar24

    parameters:
    ---------
    None

    return:
    -------

    airlines: dict
      A json-like formated data containing airlines name and icao code
      the icao code is used as the primary key
    """
    airlines = {x["ICAO"]:x["Name"] for x in FR_API.get_airlines()}
    airlines["N/A"] = "N/A"
    return airlines


def get_flight_enriched_data():
    """
    Extract flights data from FlightRadar24 API and 
    enrich data with airline and airport data

    parameters:
    -----------
    None

    return:
    -----------
    
    data: dict[dict]
       Flights data enriched with airport name, latitude, longitude...
       and airline name
    """

    # List[Flight]
    # Contains all flight informations
    flights = FR_API.get_flights()

    # Get airlines and airports json-like data
    airlines = extract_airlines()
    airports = extract_airports()

    return [{"aircraft_id":x.id,
             "aircraft_code":x.aircraft_code, 
             "airline_iata":x.airline_iata,
             "airline_name": get_airline_name(x.airline_iata, x.airline_icao, airlines),
             "callsign":x.callsign,
             "destination_airport_iata":get_airport_data(x.destination_airport_iata, airports),
             "origin_airport_iata":get_airport_data(x.origin_airport_iata, airports),
             "latitude": x.latitude,
             "longitude":x.longitude,
             "on_ground":x.on_ground,
             "time":x.time} for x in flights]

def main():
    """
    Execute the main get_flight_enriched_data as well as write
    data to /input/flight_data.json format
    """
    data = get_flight_enriched_data()
    write_file(data)


    
if __name__ == "__main__":
    while True:
        main()
        sleep(5)


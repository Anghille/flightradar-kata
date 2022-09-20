from FlightRadar24.api import FlightRadar24API, Flight
from time import sleep


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
    with open(f"/input/flight_data.json", "w") as f:
         json.dump(data, f)


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
        return airline_icao
    elif airline_iata in airlines.keys():
        return airline_iata
    else:
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
    airports["N/A"] = None
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
    airlines["N/A"] = None
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

    return {x.id:{"aircraft_code":x.aircraft_code, 
                  "airline_iata":x.airline_iata,
                  "airline_name": airlines[get_airline_name(x.airline_iata, x.airline_icao, airlines)],
                  "callsign":x.callsign,
                  "destination_airport_iata":airports[x.destination_airport_iata],
                  "origin_airport_iata":airports[x.origin_airport_iata],
                  "latitude": x.latitude,
                  "longitude":x.longitude,
                  "on_ground":x.on_ground,
                  "time":x.time} for x in flights}

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


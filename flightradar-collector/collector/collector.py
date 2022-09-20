from FlightRadar24.api import FlightRadar24API, Flight
from time import sleep


def write_file(data: Dict[Dict]) -> None:
    """ 
    Write a dict of dict as a Json file to the path /input

    parameter:
    ---------

    data: Dict[Dict]
      The dictionnary containing all informations for each flight, the flight
      id beeing the primary key of the dict

    return:
    --------
    None
    """
    with open(f"/input/flight_data.json", "w") as f:
         json.dump(data, f)


def get_airport_name(airline_iata: str, airline_icao: str) -> str:
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
    return airline_iata


def extract_airports() -> Dict[Dict]:
    """
    Extract a snapshot of all the airports identified by Flightradar24

    parameters:
    ---------
    None

    return:
    -------

    airports: Dict[Dict]
      A json-like formated data containing airports name, latitude, longitude, iata code,
      country and altitude. Airport iata code is used as primary key
    """
    airports = {x["iata"]:x for x in fr_api.get_airports()}
    airports["N/A"] = None
    return airports


def extract_airlines() -> Dict:
    """
    Extract a snapshot of all the airlines identified by Flightradar24

    parameters:
    ---------
    None

    return:
    -------

    airlines: Dict
      A json-like formated data containing airlines name and icao code
      the icao code is used as the primary key
    """
    airlines = {x["ICAO"]:x["Name"] for x in fr_api.get_airlines()}
    airlines["N/A"] = None
    return airlines


def main():
    """
        
    """
    fr_api = FlightRadar24API()

    # List[Flight]
    # Contains all flight informations
    flights = fr_api.get_flights()





    
if __name__ == "__main__":
    while True:
        main()
        sleep(1)


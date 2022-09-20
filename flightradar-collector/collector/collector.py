from FlightRadar24.api import FlightRadar24API
from time import sleep

def write_file(api_call, filename):
    with open(f"/input/{filename}.log", "w") as f:
        f.write(str(api_call))

def main():
    """
    
    """
    fr_api = FlightRadar24API()

    airports = write_file(fr_api.get_airports(), "airports")
    airlines = write_file(fr_api.get_airlines(), "airlines")
    flights = write_file(fr_api.get_flights(), "flights")
    zones = write_file(fr_api.get_zones(), "zones")

if __name__ == "__main__":
    while True:
        main()
        sleep(1)


import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def fetch_heatlists(url, referer=None):
    headers = {'Referer': referer} if referer else {}

    # Set up retries
    retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('https://', adapter)
    session.mount('http://', adapter)

    try:
        response = session.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"Request Error: {err}")
    return None


def fetch_attendee_details(base_url, attendee_id):
    try:
        url = f"{base_url}&id={attendee_id}&type=Attendee"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"Request Error: {err}")
    return None


def process_entry(entry, base_url, event_participants_map):
    attendee_id = entry.get("ID")
    print("Processing ID:", attendee_id)

    # Fetch attendee details using the second URL
    attendee_details = fetch_attendee_details(base_url, attendee_id)

    # Process the attendee details and update the hashmap
    if attendee_details:
        result = attendee_details.get("Result")
        participants = result.get("Name")
        name = participants[0] + " " + participants[1]
        # print(name)
        entries = result.get("Entries", [])
        for entry in entries:
            events = entry.get("Events", [])
            for event in events:
                event_name = str(event.get("Event_ID")) + " " + event.get("Event_Name")
                # Update or create the entry in the hashmap
                if event_name in event_participants_map:
                    # Only extend if the participant is not already in the list

                    if name not in event_participants_map[event_name]:
                        # print(f"Adding {name} to Event [{event_name}]")
                        event_participants_map[event_name].append(name)
                else:
                    # print(f"Adding {name} to Event [{event_name}]")
                    event_participants_map[event_name] = [name]
    print()


def iterate_through_json(json_data, base_url):
    if json_data is None:
        print("Failed to fetch JSON data.")
        return

    result_entries = json_data.get("Result", [])

    # Create a hashmap to store Event_Name and Participants.Name
    event_participants_map = {}

    # Loop through entries without multithreading
    for entry in result_entries:
        process_entry(entry, base_url, event_participants_map)

    # Print the hashmap
    count_uncontested = 0
    count_contested = 0
    for event_name, participants in event_participants_map.items():
        if len(participants) < 3:
            count_uncontested = count_uncontested + 1
        else:
            count_contested = count_contested + 1

        print(f"\nEvent: {event_name}")
        print("Participants:", participants)

    print(len(event_participants_map))
    print(f"Uncontested: {count_uncontested}")
    print(f"Contested: {count_contested}")


if __name__ == "__main__":
    api_url = "https://ndcapremier.com/feed/heatlists/?cyi=1351"

    heatlists_data = fetch_heatlists(api_url)
    iterate_through_json(heatlists_data, api_url)

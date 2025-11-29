"""HK Conditions Monitor
"""

import time
import xml.etree.ElementTree as ET
from datetime import datetime
import requests

# Default starting selections and refresh timing
DEFAULTS = {
    "rain_district": "Central & Western",
    "aqhi_station": "Central/Western",
    "traffic_region": "Hong Kong Island",
}

# Menu options for rain districts (numbered list)
RAIN_CHOICES = [
    "Central & Western",
    "Eastern",
    "Southern",
    "Wan Chai",
    "Kowloon City",
    "Kwun Tong",
    "Wong Tai Sin",
    "Yau Tsim Mong",
    "Sha Tin",
    "Tai Po",
    "Tsuen Wan",
    "Tuen Mun",
    "Yuen Long",
]

# Menu options for AQHI stations
AQHI_CHOICES = [
    "Central/Western",
    "Eastern",
    "Kwun Tong",
    "Sham Shui Po",
    "Sha Tin",
    "Tsuen Wan",
    "Tuen Mun",
    "Yuen Long",
]

# Menu options for traffic regions
TRAFFIC_CHOICES = [
    "Hong Kong Island",
    "Kowloon",
    "New Territories",
    "Lantau Island",
    "Islands District",
]

URLS = {
    "warnings": "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=warnsum&lang=en",
    "rain": "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=rhrread&lang=en",
    "aqhi": "https://dashboard.data.gov.hk/api/aqhi-individual?format=json",
    "traffic": "https://www.td.gov.hk/en/special_news/trafficnews.xml",
}

HTTP_HEADERS = {"User-Agent": "HKConditionsMonitor/1.0 (+https://data.gov.hk)"}

# ----------------------------- MAIN METHOD (FORMAT AND CALL METHODS) --------------------------- ISA

def main(): #----************************************************************************
    # Entry point: loop forever until the user quits
    config = DEFAULTS.copy() #start with defaults

    print("HK Conditions Monitor (live data)")
    print("Commands: Enter=refresh, c=change locations, q=quit")
    print("Current choices are shown when changing locations.\n")

    while True:
        snapshot = collect_snapshot(config)
        print_snapshot(snapshot, config)

        choice = input("\nEnter=refresh | c=change locations | q=quit: ").strip().lower()
        if choice == "q":
            break
        if choice == "c":
            change_locations(config)
            continue
        time.sleep(10) #CAN EDIT SLEEP TIME HERE!! -------------

# ----------------------------- CALLS ALL FETCH METHODS AT ONCE --------------------------- ISA

def collect_snapshot(config): #----************************************************************************
    # Pull one snapshot from each live API
    return {
        "warnings": fetch_warning(config),
        "rain": fetch_rain(config),
        "aqhi": fetch_aqhi(config),
        "traffic": fetch_traffic(config),
    }

# ----------------------------- FETCH WARNING --------------------------- ZAHEER

def fetch_warning(config): #----************************************************************************
    # Ask the API for the current warning data
    data = get_data("warnings")

    # If the API didn't return anything, say there are no warnings
    if not data:
        return empty_warning()

    # Try to find the list of warning entries under a few possible keys
    details = data.get("details")
    if details is None:
        details = data.get("warning")
    if details is None:
        details = data.get("data")

    # If we still didn't find anything, treat it as "no warnings"
    if not details:
        return empty_warning()

    # Take the first entry as the "latest" warning
    ltst_warn = details[0]

    # Try several possible fields to figure out the warning level
    level = None
    levels = ["warningStatementCode", "warningMessageCode", "warningSignal", "warningType", "level"]

    for lvl in levels:
        value = ltst_warn.get(lvl)
        if value:
            level = value
            break

    if level is None:
        level = "Unknown"

    # Try several possible fields to figure out the warning message text
    message = None
    messages = ["warningMessage", "message", "description"]

    for mssg in messages:
        value = ltst_warn.get(mssg)
        if value:
            message = value
            break

    if message is None:
        message = "No description."

    # Use the entry timestamp if possible; otherwise, use the current time
    updated = ltst_warn.get("updateTime") or ltst_warn.get("issueTime")
    if updated is None:
        updated = get_time()

    return {
        "level": str(level),
        "message": str(message),
        "updated_at": str(updated),
    }

# ----------------------------- FETCH RAIN --------------------------- RAKHAT

def fetch_rain(config): #----************************************************************************
    # Ask the API for the current rain data
    data = get_data("rain")

    # The API usually puts the readings under ["rainfall"]["data"]
    # If anything is missing, just use an empty list

    rows = []

    if "rainfall" in data:
        rainfall = data["rainfall"]
        if "data" in rainfall:
            rows = rainfall["data"]

    # Keep only items that are dictionaries
    entries = []
    for row in rows:
        if isinstance(row, dict):
            entries.append(row)

    # Which district did the user pick?
    district = config["rain_district"]

    # Find exact match for the district name
    entry = None
    for row in entries:
        if row.get("place") == district:
            entry = row
            break

    # If that fails, try a normalized match (ignoring " District", case, etc.)
    if entry is None:
        for row in entries:
            if norm(row.get("place")) == norm(district):
                entry = row
                break

    # If we did not find anything, say "No data" for that district
    if entry is None:
        return {
            "district": district,
            "intensity": "No data",
            "updated_at": get_time(),
        }

    # If we did find something, try to read the rain amount from a few possible fields
    value = entry.get("max")
    if value is None:
        value = entry.get("value")
    if value is None:
        value = entry.get("mm")

    try:
        value = float(value)
    except (TypeError,ValueError):
        value = 0.0

    # Turn the number into a label like "Showers", "Red Rain", etc.
    category = categorize_rain(value)

    # Try to get a time for this reading
    updated = entry.get("recordTime")
    if updated is None:
        updated = entry.get("time")
    if updated is None:
        updated = get_time()

    return {
        "district": district,
        "intensity": f"{value:.1f} mm ({category})",
        "updated_at": str(updated),
    }

# ----------------------------- FETCH AQHI --------------------------- MENGQI

def fetch_aqhi(config): #----************************************************************************
    """Get AQHI (air quality health index) reading for the chosen station."""
    # Ask the API for AQHI data
    data = get_data("aqhi")

    # Build a simple list of station dictionaries from whatever the API gave us
    stations = []

    if isinstance(data, list):
        # Sometimes the API is already a list of stations
        for row in data:
            if isinstance(row, dict):
                stations.append(row)
    elif isinstance(data, dict):
        # Other times the stations are inside "aqhi" or "data"
        raw = data.get("aqhi")
        if raw is None:
            raw = data.get("data")

        if isinstance(raw, list):
            for row in raw:
                if isinstance(row, dict):
                    stations.append(row)

    # Which station did the user pick?
    target_station = config["aqhi_station"]

    # Try to find that station in the list
    entry = None
    for row in stations:
        if row.get("station") == target_station:
            entry = row
            break

    # If we did not find anything, return "No data" for that station
    if entry is None:
        return {
            "station": target_station,
            "category": "Unknown",
            "value": "No data",
            "updated_at": get_time(),
        }

    # Try to read the AQHI number from a few possible fields
    raw_value = entry.get("aqhi")
    if raw_value is None:
        raw_value = entry.get("value")
    if raw_value is None:
        raw_value = entry.get("index")

    try:
        value = float(raw_value)
    except (TypeError, ValueError):
        value = 0.0

    # Work out the risk category (e.g. "High", "Moderate", etc.)
    category = entry.get("health_risk")
    if category is None:
        category = entry.get("category")
    if category is None:
        category = categorize_aqhi(value)

    # Try to figure out when this reading was updated
    timestamp = entry.get("time")
    if timestamp is None:
        timestamp = entry.get("publish_date")
    if timestamp is None:
        timestamp = entry.get("updateTime")

    # If we still have no time, fall back to "now"
    if timestamp is None:
        timestamp = get_time()

    return {
        "station": target_station,
        "category": category,
        "value": value,
        "updated_at": str(timestamp),
    }

# ----------------------------- FETCH TRAFFIC --------------------------- BETO

def fetch_traffic(config): #----************************************************************************
    """Get traffic info for the chosen region."""
    # Ask the API for the traffic data
    data = get_data("traffic")

    # Turn the raw data into a simple list of incident dictionaries
    incidents = extract_traffic_entries(data)

    # Try to pick one incident that matches the chosen region
    target_region = config["traffic_region"]
    entry = pick_traffic_entry(incidents, target_region)

    # If we did not find any incident, return a simple "no data" message
    if entry is None:
        return {
            "severity": "Info",
            "description": "No traffic data.",
            "updated_at": get_time(),
        }

    # Work out the severity (e.g. "Info", "Serious", etc.)
    severity = entry.get("severity")
    if severity is None:
        severity = entry.get("category")
    if severity is None:
        severity = entry.get("status")
    if severity is None:
        severity = "Info"

    # Work out the description of what is happening
    description = entry.get("content")
    if description is None:
        description = entry.get("description")
    if description is None:
        description = entry.get("summary")
    if description is None:
        description = "Traffic update"

    # Try to figure out when this incident was last updated
    updated = entry.get("update_time")
    if updated is None:
        updated = entry.get("updateTime")

    # If we still have no time, fall back to "now"
    if updated is None:
        updated = get_time()

    return {
        "severity": str(severity).title(),
        "description": str(description).strip(),
        "updated_at": str(updated)
    }

# ----------------------------- API REQUEST --------------------------- ISA

def get_data(which): #----************************************************************************
    """Fetch data from one of the HK API endpoints.
    which: a string like 'warnings', 'rain', 'aqhi', or 'traffic'
    """
    # Pick the right URL based on the kind of data we want
    url = URLS[which]

    # Ask the server for data
    response = requests.get(url, timeout=10, headers=HTTP_HEADERS)

    # If the HTTP status is not OK (e.g. 404, 500), this will raise an error
    response.raise_for_status()

    # Traffic feed is XML, so parse it with our XML helper
    if which == "traffic":
        return parse_traffic_xml(response.text)

    # Everything else is JSON
    return response.json()

# ----------------------------- GENERAL HELPER FUNCTIONS --------------------------- EVERYONE

def empty_warning(): #----************************************************************************
    return {
        "level": "None",
        "message": "No weather warnings in force.",
        "updated_at": get_time(),
    }

def norm(text): #----************************************************************************
    """Make a place name easier to compare."""
    # If it's not a string, just return empty string
    if not isinstance(text, str):
        return ""

    # Remove spaces at the edges and make everything lowercase
    name = text.strip().lower()

    # If it ends with " district", remove that part
    if name.endswith(" district"):
        name = name[:-len(" district")]

    return name

def get_time(): #----************************************************************************
    """Return timestamp"""
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

# ---------------------------- TRAFFIC HELPER FUNCTIONS --------------------------- BETO

def parse_traffic_xml(text): #----**************************************************************** BETO
    """Convert the XML traffic feed into a dictionary with a list of incidents.

    The result will look like:
        {
            "trafficnews": [
                {
                    "region": ...,
                    "severity": ...,
                    "content": ...,
                    "update_time": ...,
                    "location": ...,
                    "direction": ...,
                    "description": ...,
                    "status": ...,
                },
                ...
            ]
        }
    """
    # Turn the XML string into an XML tree
    root = ET.fromstring(text)

    # This will hold one dictionary per traffic incident
    incidents = []

    # Go through every <message> element in the XML
    for message in root.findall(".//message"):
        # First, read all child tags under <message> into a simple dictionary.
        # Example: <district_en>Hong Kong Island</district_en>
        # becomes data["district_en"] = "Hong Kong Island"
        data = {}
        for child in message:
            tag_name = child.tag.lower()           # tag name as lowercase string
            text_value = (child.text or "").strip()  # text inside the tag (or "" if None)
            data[tag_name] = text_value

        # Now build a cleaner incident dictionary using the fields we care about.
        incident = {
            # Region name (e.g. "Hong Kong Island", "Kowloon", etc.)
            "region": data.get("district_en") or data.get("region"),

            # Severity / headline of the incident
            "severity": data.get("incident_heading_en") or data.get("severity"),

            # Main content / description
            "content": data.get("content_en") or data.get("incident_detail_en"),

            # When the announcement was made
            "update_time": data.get("announcement_date"),

            # Extra location information
            "location": data.get("location_en"),

            # Direction of traffic affected
            "direction": data.get("direction_en"),

            # Longer description of the incident
            "description": data.get("incident_detail_en"),

            # Status of the incident (e.g. “ongoing”, “cleared”)
            "status": data.get("incident_status_en"),
        }

        incidents.append(incident)

    # Wrap the list in a dict so extract_traffic_entries() can find "trafficnews"
    return {"trafficnews": incidents}


def extract_traffic_entries(data): #----**************************************************************** BETO
    """Turn the raw traffic data into a simple list of incident dictionaries."""
    incidents = []

    # Case 1: the data is already a list of dictionaries
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                incidents.append(item)
        return incidents

    # Case 2: the data is a dictionary and the list is inside it
    if isinstance(data, dict):
        # Try a few possible keys where the API might store the list
        possible_keys = ["trafficnews", "incidents", "messages", "data"]

        for key in possible_keys:
            raw = data.get(key)

            # If we find a list under this key, keep only the dict items
            if isinstance(raw, list):
                for item in raw:
                    if isinstance(item, dict):
                        incidents.append(item)
                return incidents

    # If we did not find anything usable, return an empty list
    return incidents


def pick_traffic_entry(incidents, target_region): #----********************************************** BETO
    """Choose one traffic incident that matches the chosen region."""
    # If there are no incidents at all, we cannot pick anything
    if not incidents:
        return None

    # Turn the region we are looking for into lowercase text
    if target_region is None:
        target_region = ""
    target = target_region.strip().lower()

    # If the user did not really choose a region, just return the first incident
    if target == "":
        return incidents[0]

    # Go through each incident and see if it mentions the region
    for entry in incidents:
        # Collect different text fields from the incident
        parts = []

        for field in ["region", "location", "direction", "content", "description"]:
            value = entry.get(field)
            if value:
                parts.append(str(value))

        # Join everything into one big lowercase string
        joined = " ".join(parts).lower()

        # If our target text appears anywhere inside this incident text, pick it
        if target in joined:
            return entry

    # If nothing matched, just fall back to the first incident
    return incidents[0]


# -------------------------------- CATEGORIZING FUNCTIONS ------------------------------------- RAKHAT

def categorize_rain(value): #----************************************************************************
    if value >= 30:
        return "Black Rain"
    if value >= 15:
        return "Red Rain"
    if value >= 5:
        return "Amber Rain"
    if value >= 1:
        return "Showers"
    return "Dry"


def categorize_aqhi(value): #----************************************************************************
    if value >= 10:
        return "Serious"
    if value >= 7:
        return "Very High"
    if value >= 4:
        return "High"
    if value >= 3:
        return "Moderate"
    return "Low"

# USER INTEFACE ------------------ COMMAND LINE FORMATTING FUNCTIONS ---------------------- BENNETT

def print_snapshot(snapshot, config): #----************************************************************************
    print("\n============================================================")
    print("District:", config["rain_district"],
          "| AQHI:", config["aqhi_station"],
          "| Traffic:", config["traffic_region"])
    print("------------------------------------------------------------")

    print("\nWarnings")
    print("--------")
    print_warning(snapshot["warnings"])

    print("\nRain")
    print("----")
    print_rain(snapshot["rain"])

    print("\nAQHI")
    print("----")
    print_aqhi(snapshot["aqhi"])

    print("\nTraffic")
    print("-------")
    print_traffic(snapshot["traffic"])

    print("============================================================")

def print_warning(row): #----************************************************************************
    print("Level:", row["level"])
    print("Message:", row["message"])
    print("Updated:", row["updated_at"])


def print_rain(row): #----************************************************************************
    print("District:", row["district"])
    print("Intensity:", row["intensity"])
    print("Updated:", row["updated_at"])



def print_aqhi(row): #----************************************************************************
    print("Station:", row["station"])
    print("Category:", row["category"])
    print("Value:", row["value"])
    print("Updated:", row["updated_at"])


def print_traffic(row): #----************************************************************************
    print("Severity:", row["severity"])
    print(row["description"])
    print("Updated:", row["updated_at"])


#-------------------------------------------------------- ISA

def select_from_list(title, options, current): #----************************************************* ISA
    """Show a numbered menu and let the user pick an option.

    - Press Enter to keep the current value.
    - Type a number to choose a new option.
    """
    # Show the menu title
    print("\n" + title + ":")

    # Print each option with a number (1, 2, 3, ...)
    number = 1
    for option in options:
        print(f"  {number}. {option}")
        number = number + 1

    # Ask the user what they want
    prompt = f"Choose 1-{len(options)} (current: {current}, Enter to keep): "
    choice = input(prompt).strip()

    # If they just press Enter, keep the current value
    if choice == "":
        return current

    # If they type something that is not digits, keep current
    if not choice.isdigit():
        return current

    # Turn their choice into a number
    choice_number = int(choice)

    # If the number is out of range, keep current
    if choice_number < 1 or choice_number > len(options):
        return current

    # Convert from 1-based (menu) to 0-based (list index)
    index = choice_number - 1

    # Return the selected option
    return options[index]



def change_locations(config): #----*********************************************************** ISA
    """Let the user change the selected district/station/region."""
    print("\nChange locations (press Enter to keep current)")

    # Current choices
    current_rain = config["rain_district"]
    current_aqhi = config["aqhi_station"]
    current_traffic = config["traffic_region"]

    # Ask for a new rain district
    new_rain = select_from_list(
        "Rain districts",
        RAIN_CHOICES,
        current_rain,
    )

    # Ask for a new AQHI station
    new_aqhi = select_from_list(
        "AQHI stations",
        AQHI_CHOICES,
        current_aqhi,
    )

    # Ask for a new traffic region
    new_traffic = select_from_list(
        "Traffic regions",
        TRAFFIC_CHOICES,
        current_traffic,
    )

    # Save the new values back into the config
    config["rain_district"] = new_rain
    config["aqhi_station"] = new_aqhi
    config["traffic_region"] = new_traffic

#---------------------- CALLING MAIN ----------------------------
if __name__ == "__main__": #----**************************************************************** ISA
    main()



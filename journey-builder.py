import os
import requests
import json

# Constants
URL_01_TEMPLATE = "https://journey-report.ddev.site/v1/problem/{}"
URL_02_TEMPLATE = "https://journey-report.ddev.site/v1/journey/{}"

def fetch_token():
    url = "https://journey-report.ddev.site/oauth/token"
    payload = 'grant_type=client_credentials&client_id=942F!jHOPHkB1l%23S%5EqnCSLzVsuE%25PRp%23&client_secret=ubND%2473*HoG4NCLOtx6HB!OmwZVD%26zgS&username=lydia&password=test&scope=rest'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    data = json.loads(response.text)
    return data['access_token']

def fetch_id_map(headers, problem_id):
    problem_url = URL_01_TEMPLATE.format(problem_id)
    print("Fetching problem ID map from:", problem_url)
    response = requests.get(problem_url, headers=headers)
    response.raise_for_status()
    data = response.json()
    print(f"Retrieved {len(data)} ID mappings.")
    return data

def fetch_and_save_journeys(id_map, headers, problem_id):
    # Get the folder name from the first key
    folder_name = problem_id
    os.makedirs(folder_name, exist_ok=True)
    print(f"Saving journey files to folder: {folder_name}/")
    # Save to file
    filename = os.path.join(folder_name, f"index.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(id_map, f, indent=2)
    print(f"Saved: {filename}")

    for key, value in id_map.items():
        if  key == "title":
            continue #skip the title
        if key == "uuid":
            continue #skip the uuid
        if key == "customer":
            continue
        if key == "ai_search_query":
            continue
        if key == "ai_journey":
            index = 1
            for uuid, data in value.items():
                try:
                    print(f"Processing journey {index}: {data[0]['website']['title']}")
                except Exception as err:
                    print(f"Processing journey {index}: {uuid} - {err}")
                journey_url = URL_02_TEMPLATE.format(uuid)
                index += 1

                try:
                    response = requests.get(journey_url, headers=headers)
                    response.raise_for_status()
                    journey_data = response.json()

                    # Save to file
                    filename = os.path.join(folder_name, f"{uuid}.json")
                    with open(filename, "w", encoding="utf-8") as f:
                        json.dump(journey_data, f, indent=2)
                    #print(f"Saved: {filename}")

                except requests.HTTPError as http_err:
                    print(f"HTTP error fetching journey {uuid}: {http_err}")
                except Exception as err:
                    print(f"Error processing journey {uuid}: {err}")

def main():
    try:
        token = fetch_token()
        headers = {
            'Authorization': f"Bearer {token}",
            'Content-Type': 'application/json'
        }
        problem_id = '7da6a7d9-4f0f-4195-9c27-94e8bc39aee1'
        id_map = fetch_id_map(headers, problem_id)
        fetch_and_save_journeys(id_map, headers, problem_id)
        print("✅ All journeys processed.")
    except Exception as e:
        print("❌ Failed to complete processing:", e)

if __name__ == "__main__":
    main()

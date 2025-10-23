import csv
import requests

def updatesetlist(url='https://victorianrailphotos.com/api/trainsets.csv'):
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open('datalists/trainsets.csv', 'w', newline='') as file:
            file.write(response.text)
        print("Trainsets updated successfully.")
    except requests.RequestException as e:
        print(f"Error fetching trainsets: {e}")

def setNumber(input_str):      
    all_sets = []
    with open('datalists/trainsets.csv', mode='r', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            all_sets.append(row)
    
    for set_str in all_sets:
        temp = set_str[0].split('-')
        if input_str in temp:
            return set_str[0], set_str[6]
    return None

print(setNumber('633M'))
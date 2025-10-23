import csv
import requests

def updatesetlist(url='https://victorianrailphotos.com/api/trainsets.csv'):
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open('datalists/trainsets.csv', 'w', newline='', encoding='utf-8') as file:
            file.write(response.text)
        print("Trainsets updated successfully.")
    except requests.RequestException as e:
        print(f"Error fetching trainsets: {e}")

def updatesetlistTram(url='https://victorianrailphotos.com/api/tramsets.csv'):
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open('datalists/tramsets.csv', 'w', newline='', encoding='utf-8') as file:
            file.write(response.text)
        print("Tramsets updated successfully.")
    except requests.RequestException as e:
        print(f"Error fetching tramsets: {e}")

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
    return None, None

def setNumberTram(input_str):      
    all_sets = []
    with open('datalists/tramsets.csv', mode='r', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            all_sets.append(row)
    
    for set_str in all_sets:
        temp = set_str[0].split('.')
        if input_str in temp:
            set_type, number = set_str[0].split('.')
            if set_type == 'C2':
                set_type = 'C2 Class'
            else:
                set_type = set_type[:1] + ' Class'
            return number, set_type
    return None, None

print(setNumberTram('6050'))
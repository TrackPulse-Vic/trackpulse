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
    '''
    Determine the set number and type from the inputted carriage/loco number.
    '''
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
    '''
    Determine the set number and type from the inputted tram number.
    '''   
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

def sydneyTrainType(setNumber):
    """
    Basic way to find a nsw type, i should probably make it use apetures csv at some point
    """
    if setNumber.startswith('AM'):
        trainType = 'Alstom Metropolis'
    elif setNumber.startswith('A'):
        trainType = 'Waratah A set'
    elif setNumber.startswith('B'):
        trainType = 'Waratah B set'
    elif setNumber.startswith('H'):
        trainType = 'OSCar'
    elif setNumber.startswith('J'):
        trainType = 'Hunter'
    elif setNumber.startswith('K'):
        trainType = 'K Set'
    elif setNumber.startswith('M'):
        trainType = 'Millenium'
    elif setNumber.startswith('N'):
        trainType = 'Endeavour'
    elif setNumber.startswith('T'):
        trainType = 'Tangara'
    elif setNumber.startswith('V'):
        trainType = 'V Set'
    elif setNumber.startswith('XP'):
        trainType = 'XPT'    
    elif setNumber.startswith('P'):
        trainType = 'Xplorer'
    elif int(setNumber) >= 4801 and int(setNumber) <= 4863 or int(setNumber) >= 4865 and int(setNumber) <= 48165 or int(setNumber) >= 48208 and int(setNumber) <= 48209 or int(setNumber)== 48216:
        trainType = '48 Class'
    
    else:
        trainType = 'Unknown'
        
    return trainType

def trainInfo(number):
    """
    Get the train info from the number, returns a dict with the info
    """
    setN, trainType = setNumber(number)
    if setN is None:
        return None
    else:
        with open('datalists/trainsets.csv', mode='r', newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == setN:
                    return {
                        'setNumber': setN,
                        'trainType': trainType,
                        'livery': row[1],
                        'inService': row[2],
                        'status': row[3],
                        'notes': row[4],
                        'name': row[5],
                        'interior': row[7],
                        'gauge': row[8],
                        'operator': row[9]
                    }
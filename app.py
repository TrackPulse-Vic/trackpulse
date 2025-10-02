import os
import dotenv
from flask import Flask, redirect, render_template, request, url_for
from flask_discord import DiscordOAuth2Session


dotenv.load_dotenv()

app = Flask(__name__)
app.secret_key =os.getenv('FLASK_SECRET_KEY')

# Discord auth config
app.config["DISCORD_CLIENT_ID"] = os.getenv('DISCORD_CLIENT_ID')
app.config["DISCORD_CLIENT_SECRET"] = os.getenv('DISCORD_CLIENT_SECRET') 
app.config["DISCORD_REDIRECT_URI"] = os.getenv('DISCORD_REDIRECT_URI')
discord = DiscordOAuth2Session(app)

@app.route("/")
def mainPage():
    return 'hi'

@app.route('/dashboard')
def dashboardPage():
    return render_template('dashboard.html')

@app.route('/log')
def logPage():
    mode = request.args.get('mode')
    prettyMode = {
        'victrain': 'Victorian Train',
        'victram': 'Melbourne Tram',
        'vicbus': 'Victorian Bus',
        'nswtrain': 'New South Wales Train',
        'nswbus': 'New South Wales Bus',
        'nswferry': 'New South Wales Ferry',
        'nswlightrail': 'New South Wales Light Rail',
        'satrain': 'South Australian Train',
        'satram': 'South Australian Tram',
        "sabus": 'South Australian Bus',
        'watrain': 'Western Australian Train',
        'wabus': 'Western Australian Bus',
        'actlightrail': 'ACT Light Rail',
        'actbus': 'ACT Bus'
    }
    
    lineOptions = {
        'victrain': {
            'Metro': ["Alamein", "Belgrave", "Craigieburn", "Cranbourne", "Flemington Racecourse", "Frankston", "Glen Waverley", "Hurstbridge", "Lilydale", "Mernda", "Pakenham", "Sandringham", "Stony Point", "Sunbury", "Upfield", "Werribee", "Williamstown"],
            'V/Line': ["Albury", "Ararat", "Bairnsdale", "Ballarat", "Bendigo", "Echuca", "Geelong", "Maryborough", "Seymour", "Shepparton", "Swan Hill", "Traralgon", "Warrnambool"]
        },
        'victram': {
            'Tram Routes': ["1", "3", "5", "6", "11", "12", "16", "19", "30", "35", "48", "57", "58", "59", "64", "64a", "67", "70", "70", "72", "75", "78", "82", "86", "96", "109"]
        },

        'nswtrain': {
            'Sydney Trains': ["T1", "T2", "T3", "T4", "T5", "T6", 'T7', "T8", ],
            'Metro': ['M1'],
            'Intercity': ["Blue Mountains", "Central Coast & Newcastle", "South Coast", "Southern Highlands"],
            'NSW TrainLink': ["Casino XPT", "Brisbane XPT", "Canberra Xplorer", "Melbourne XPT", "Griffith Xplorer", "Dubbo XPT", 'Broken Hill Xplorer', "Moree/Armidale Xplorer"]
        },
        'nswferry': {
            'Ferry Routes': ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10"]
        },
        'nswlightrail': {
            'Light Rail': ["L1", "L2", "L3", "L4"]
        },
        'satrain': {
            'Adelaide Metro': ["Belair", "Gawler", "Grange", "Outer Harbor", "Port Dock", "Seaford", "Flinders"],
            "Journey Beyond": ["The Overland","The Ghan", "Indian Pacific", "Great Southern"]
        },
        'satram': {
            'Tram Routes': ["GLNELG", "BTANIC", "FESTVL", "ADLOOP"]
        },
        'watrain': {
            'Transperth': ["Fremantle", "Midland", "Armadale", "Yanchep", "Thornlie-Cockburn","Mandurah","Airport","Ellenbrook"],
            'Transwa': ["Australind", "AvonLink", "MerredinLink", "The Prospector"]
        },
        'actlightrail': {
            'Light Rail': ["R1"]
        },

    }

    displayName = prettyMode.get(mode, None)
    categorizedLines = lineOptions.get(mode, {})
    return render_template('log.html', mode=mode, displayName=displayName, lineOptions=categorizedLines)

if __name__ == "__main__":
    app.run(debug=True, port=5002)
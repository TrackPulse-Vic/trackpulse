import os
from urllib.parse import quote_plus, urlencode
import dotenv
from flask import Flask, jsonify, redirect, render_template, request, url_for
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for
import tempfile

import requests

from scripts.converter import convertLogs
from scripts.map.main import getVehiclePositions
from scripts.reader import getLogs

dotenv.load_dotenv()

app = Flask(__name__)
app.secret_key =os.getenv('APP_SECRET_KEY')

# auth0 oauth
oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=os.getenv("AUTH0_CLIENT_ID"),
    client_secret=os.getenv("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{os.getenv("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

# loging and callback
@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )
@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/dashboard")
@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://" + os.getenv("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("mainPage", _external=True),
                "client_id": os.getenv("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

@app.route("/")
def mainPage():
    if session.get("user"):
        return redirect('/dashboard')
    else:
        return render_template('landing.html')

@app.route('/dashboard')
def dashboardPage():
    return render_template('dashboard.html', session=session.get("user"))

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
    
    # stations list
    try:
        with open(f'datalists/stations/{mode}.txt', 'r') as file:
            stations = file.readlines()
    except FileNotFoundError:
        stations = []

    displayName = prettyMode.get(mode, None)
    categorizedLines = lineOptions.get(mode, {})
    return render_template('log.html', mode=mode, displayName=displayName, lineOptions=categorizedLines, stations=stations)

# view log page
@app.route('/view')
def viewLogPage():
    logs = getLogs(user=session.get('user')['userinfo']['sub'])
    return render_template('viewer.html', logs=logs)

# comvert page and api
@app.route('/convert')
def convertPage():
    return render_template('convert.html')
@app.route('/api/convert', methods=['POST'])
def convertAPI():
    data = request.form
    file = request.files.get('file')
    if file:
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, data['mode'] + "_" + file.filename)
        file.save(file_path)
    else:
        return "No file uploaded", 400

    convertLogs(file_path, data['mode'], session.get("user")['userinfo']['sub'])
    
    return render_template('convert.html', success="Conversion successful!")

# TRAIN SEARCH AND MAP PAGE
@app.route('/map/<mode>')
def mapPage(mode):
    return render_template('map.html', mode=mode)

@app.route('/api/locations/<mode>')
def apiLocations(mode):
    if not request.referrer or not request.referrer.startswith(request.host_url) or 'xm9g.net' in request.referrer:
        return jsonify({"error": "Access denied"}), 403
    return jsonify(getVehiclePositions(mode))
 

@app.route(f'/api/photo/<mode>')
def apiPhoto(mode):
    # if not request.referrer or not request.referrer.startswith(request.host_url):
    #     return jsonify({"error": "Access denied"}), 403
    number = request.args.get('number')
    if mode == 'train':
        if number.startswith('V') or number.startswith('S'):
            number = number[1:]
        images = requests.get(f'https://victorianrailphotos.com/api/photos/{number}')
        data = images.json()
        imgURL = data['photos'][0]['thumbnail']
        return redirect(imgURL)
    return jsonify({"error": "Invalid mode"}), 400


if __name__ == "__main__":
    app.run(debug=True, port=5002)
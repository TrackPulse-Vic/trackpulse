import datetime
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
from scripts.trainset import setNumber

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

global lineColors 
lineColors = {
        'victrain': {
            'Lilydale': '#00518b',
            'Belgrave': '#00518b',
            'Alamein': '#00518b',
            'Glen Waverley': '#00518b',
            'Pakenham': '#00a8e4',
            'Cranbourne': '#00a8e4',
            'Frankston': '#009646',
            'Stony Point': '#009646',
            'Sandringham': '#f07fb3',
            'Werribee': '#009646',
            'Williamstown': '#009646',
            'Sunbury': '#fcb919',
            'Upfield': '#fcb919',
            'Craigieburn': '#fcb919',
            'Hurstbridge': '#d0222f',
            'Mernda': '#d0222f',
            'Flemington Racecourse': '#929598',
            'Albury': '#7d4099',
            'Bairnsdale': '#7d4099',
            'Traralgon': '#7d4099',
            'Warrnambool': '#7d4099',
            'Geelong': '#7d4099',
            "Ararat": '#7d4099',
            "Ballarat": '#7d4099',
            'Maryborough': '#7d4099',
            'Swan Hill': '#7d4099',
            'Bendigo': '#7d4099',
            'Echuca': '#7d4099',
            'Seymour': '#7d4099',
            'Shepparton': '#7d4099',
        }
    }

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
    if not session.get("user"):
        return redirect('/login')
    return render_template('dashboard.html', session=session.get("user"))

@app.route('/log')
def logPage():
    if not session.get("user"):
        return redirect('/login')
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
    if not session.get("user"):
        return redirect('/login')
    
    line = request.args.get('line', None)
    mode = request.args.get('mode', None)
    start= request.args.get('start', None)
    end = request.args.get('end', None)
    number = request.args.get('number', None)
    vehicle = request.args.get('vehicle', None)
    
    logs = getLogs(user=session.get('user')['userinfo']['sub'], line=line, mode=mode, start=start, end=end, number=number, type=vehicle)
    return render_template('viewer.html', logs=logs, lineColors=lineColors)

# single log page
@app.route('/log/<int:id>')
def singleLogPage(id):
    try:
        log = getLogs(user=session.get('user')['userinfo']['sub'], id=id)
    except Exception as e:
        print(f'Error: {e}')
        return "error loading log", 500
    if not log or len(log) == 0:
        return "Log not found or not allowed to be seen!", 404
    return render_template('singlelog.html', log=log, lineColors=lineColors)

# log add api
@app.route('/api/addLog', methods=['POST'])
def addLogAPI():
    logInfo = request.form
    if not session.get("user"):
        return 'user not authenticated', 401
    
    if logInfo.get('date') == '':
        date = datetime.datetime.now().strftime('%Y-%m-%d')
    number, type = setNumber(logInfo.get('number'))    
    
    return(jsonify(logInfo, date, number, type, session.get("user")['userinfo']['sub']))

# convert page and api
@app.route('/convert')
def convertPage():
    if not session.get("user"):
        return redirect('/login')
    return render_template('convert.html')

@app.route('/api/convert', methods=['POST'])
def convertAPI():
    if not session.get("user"):
        return 'user not authenticated', 401
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
    if not request.referrer or not (request.referrer.startswith(request.host_url) or 'xm9g.net' in request.referrer):
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
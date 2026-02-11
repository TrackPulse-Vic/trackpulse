import datetime
import os
from typing import Counter
from urllib.parse import quote_plus, urlencode
import dotenv
from flask import Flask, jsonify, redirect, render_template, request, url_for
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for
from flask_limiter import Limiter
import tempfile

import requests

from scripts.apiKeyManager import checkKey
from scripts.converter import convertLogs
from scripts.log import getOperator, logTrip
from scripts.map.main import getVehiclePositions
from scripts.reader import deleteLog, getLogs
from scripts.trainset import setNumber, setNumberTram
from scripts.userDBmanager import addUser
from scripts.vrpApi import getTrainImage


dotenv.load_dotenv()

app = Flask(__name__)
app.secret_key =os.getenv('APP_SECRET_KEY')

# Flask-Limiter instance
limiter = Limiter(app)

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
            'Sunbury': '#00a8e4',
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

global MODES
MODES = ['All', 'victrain', 'victram', 'vicbus', 'nswtrain', 'nswbus', 'nswferry', 'nswlightrail', 'satrain', 'satram', 'watrain', 'wabus', 'actlightrail', 'actbus']

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
    addUser(session["user"]['userinfo']['sub'], session["user"]['userinfo']['name'], session["user"]['userinfo']['email']) # add user to database if not exists
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
    logCount = len(getLogs())
    
    if request.args.get('src') == 'nav':
        return render_template('landing.html', logCount=logCount, is_authenticated=session.get("user") is not None)
    if session.get("user"):
        return redirect('/dashboard')
    else:   
        return render_template('landing.html', logCount=logCount, is_authenticated=False)
@app.route('/tpv')
def tpvPage():
    return render_template('discordbot.html')

@app.route('/dashboard')
def dashboardPage():
    if not session.get("user"):
        return redirect('/login')
    return render_template('dashboard.html', session=session.get("user"))

@app.route('/stats')
def statsPage():
    if not session.get("user"):
        return redirect('/login')
    
    if not request.args.get('stat'):
        return render_template('statsselector.html', modes=MODES, selectedMode=request.args.get('mode', None))
        
    mode = request.args.get('mode', None)
    stat = request.args.get('stat', None)
    display = request.args.get('display', None)
    truncate = request.args.get('truncate', None)
    
    if mode == 'All':
        mode = None
        
    logs = getLogs(user=session.get('user')['userinfo']['sub'], mode=mode)
    
    collumMappings = {
        'line': 7,
        'start': 8,
        'end': 9,
        'number': 5,
        'type': 6,
        'date': 3,
        'operator': 4,
    }
    
    lines = []
    for log in logs:
        if stat =='station':
            lines.append(log[collumMappings['start']])
            lines.append(log[collumMappings['end']])
        else:
            lines.append(log[collumMappings[stat]])
    lineFrequency = Counter(lines)

    sorted_items = sorted(lineFrequency.items(), key=lambda x: x[1], reverse=True)
    fullLabels = [item[0] for item in sorted_items]
    fullValues = [item[1] for item in sorted_items]
    
    if truncate and truncate.isdigit():
        truncate = int(truncate)
        if truncate > 0:
            # Sort by frequency descending
            sorted_items = sorted(lineFrequency.items(), key=lambda x: x[1], reverse=True)
            top_items = sorted_items[:truncate]
            other_sum = sum(freq for _, freq in sorted_items[truncate:])
            truncatedLabels = [item[0] for item in top_items]
            truncatedValues = [item[1] for item in top_items]
            # if other_sum > 0:
            #     truncatedLabels.append('Other')
            #     truncatedValues.append(other_sum)
        else:
            truncatedLabels = fullLabels
            truncatedValues = fullValues
    else:
        truncatedLabels = fullLabels
        truncatedValues = fullValues

    return render_template('stats.html', full_labels=fullLabels, full_values=fullValues, truncated_labels=truncatedLabels, truncated_values=truncatedValues, stat=stat)

@app.route('/log')
def logPage():
    if not session.get("user"):
        return redirect('/login')
    mode = request.args.get('mode')
    message = request.args.get('message', None)
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
    
    automodes = ['victrain', 'victram']
    
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
    return render_template('log.html', mode=mode, displayName=displayName, lineOptions=categorizedLines, stations=stations, message=message, automodes=automodes)

# view log page
@app.route('/view')
def viewLogPage():
    if not session.get("user"):
        return redirect('/login')
    
    
    line = request.args.get('line', None)
    mode = request.args.get('mode', None)
    date = request.args.get('date', None)
    if mode == 'All':
        mode = None
    start= request.args.get('start', None)
    end = request.args.get('end', None)
    number = request.args.get('number', None)
    vehicle = request.args.get('vehicle', None)
    
    message = request.args.get('message', None)
    
    logs = getLogs(user=session.get('user')['userinfo']['sub'], line=line, mode=mode, start=start, end=end, number=number, type=vehicle, date=date)
    
    if request.args.get('table') == 'true':
        return render_template('logtable.html', logs=logs,lineColors=lineColors, modes=MODES, message=message)
    else:
        return render_template('viewer.html', logs=logs, lineColors=lineColors, modes=MODES, message=message)

# single log page
@app.route('/log/<int:id>')
def singleLogPage(id):
    try:
        log = getLogs(user=session.get('user')['userinfo']['sub'], id=id)
    except Exception as e:
        print(f'Error: {e}')
        return "error loading log", 500
    if not log or len(log) == 0:
        return render_template('custommessage.html', message="You do not have permission to view this trip!"), 404
    return render_template('singlelog.html', log=log, lineColors=lineColors)

# vehicle page
@app.route('/stats/<mode>/<vehicle>')
def trainPage(mode, vehicle):
    photoURL, photographer = getTrainImage(vehicle.split('-')[0], thumbnail=False)
    return render_template('trainpage.html',mode=mode, vehicle=vehicle, photoURL=photoURL, photographer=photographer)

# log add api
@app.route('/api/addLog', methods=['POST'])
def addLogAPI():
    '''
    internal api for adding logs from the web app
    '''
    try:
        # auth verification stuff
        logInfo = request.form
        if not session.get("user"):
            return 'user not authenticated', 401
        
        # date will be today if not provided
        if logInfo.get('date') == '':
            date = datetime.datetime.now().strftime('%Y-%m-%d')
        else:
            date = logInfo.get('date')
        
        # get type and number of the vehicle
        if logInfo.get('type') != "":
            # manual
            type = logInfo.get('type')
            number = logInfo.get('number')
        else:
            # auto detect
            if logInfo.get('mode') == 'victrain':
                number, type = setNumber(logInfo.get('number'))
            elif logInfo.get('mode') == 'victram':
                number, type = setNumberTram(logInfo.get('number'))
                
        logInfo = dict(logInfo)
        logInfo['date'] = date
        logInfo['number'] = number
        logInfo['type'] = type
        logInfo['user'] = session.get("user")['userinfo']['sub']
        logInfo['tags'] = None
        logInfo['operator'] = getOperator(logInfo.get('mode'), logInfo.get('type'))

        success = logTrip(
            user=session.get("user")['userinfo']['sub'],
            mode=logInfo.get('mode'),
            date=logInfo.get('date'),
            vehicleNumber=logInfo.get('number'),
            vehicleType=logInfo.get('type'),
            start=logInfo.get('start'),
            end=logInfo.get('end'),
            line=logInfo.get('line'),
            operator=logInfo.get('operator'),
            note=logInfo.get('notes'),
            tags=logInfo.get('tags'),
        )
        
        if not success:
            message = "Error adding trip to Database, please try again."
            print(f'error adding log: {logInfo}')
        else:
            message = "Trip logged!"
        
        return jsonify(logInfo), 200
    except Exception as e:
        print(f"Error in /api/addLog: {e}")
        message = "Internal Server Error, please try again later."
        
#Log delete API
@app.route('/api/deleteLog', methods=['POST'])
@limiter.limit("10 per minute")
def deleteLogAPI():
    try:
        print("Delete log request received")
        logID = request.get_json().get('id')
        if not session.get("user"):
            return 'user not authenticated', 401
        
        logs = getLogs(user=session.get('user')['userinfo']['sub'], id=logID)
        if not logs or len(logs) == 0:
            return "Log not found or not allowed to be deleted!", 404
        
        succsess = deleteLog(logID)
        
        if succsess:
            print(f"Log ID {logID} deleted successfully")
            return 'Log deleted successfully', 200
        else:
            print(f"Error deleting log ID {logID}")
            return 'Error deleting log', 500
    except Exception as e:
        print(f"Error in /api/deleteLog: {e}")
        return "Internal Server Error, please try again later.", 500

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

# user facing API
@app.route('/api')
def apiInfoPage():
    return render_template('apiinfo.html')

@app.route('/api/<key>/logs')
def apiUserLogs(key):
    mode = request.args.get('mode', None)
    if mode == 'All':
        mode = None
    # simple api key auth
    api_keys = {
        'your_api_key_here': 'oauth2|discord|780303451980038165',
    }
    if key not in api_keys:
        return jsonify({"error": "Invalid API key"}), 403
    user_id = api_keys[key]
    logs = getLogs(user=user_id, mode=mode)
    log_list = []
    for log in logs:
        log_data = {
            'id': log[0],
            'mode': log[2],
            'date': log[3],
            'operator': log[4],
            'number': log[5],
            'type': log[6],
            'line': log[7],
            'start': log[8],
            'end': log[9],
            'notes': log[10],
            'tags': log[11],
        }
        log_list.append(log_data)
    return jsonify(log_list)

@app.route('/api/<key>/logs.csv')
def apiUserLogsCSV(key):
    mode = request.args.get('mode', None)
    globalLogs = request.args.get('global', 'false').lower() == 'true'
    userid = request.args.get('userid', None)
    
    if mode == 'All':
        mode = None
    
    user_id, privileged = checkKey(key)
    if not user_id:
        return jsonify({"error": "Invalid API key"}), 403
    
    # get all logs if privileged and its in the args
    if privileged and globalLogs:
        user_id = None
    # get logs for specific userid if privileged
    elif privileged and userid:
        user_id = userid
        
    logs = getLogs(user=user_id, mode=mode)
    csv_data = "id,number,type,date,line,start,end,note,operator,mode,tag\n"
    for log in logs:
        csv_data += f'{log[0]},{log[5]},{log[6]},{log[3]},{log[7]},{log[8]},{log[9]},"{log[10]}",{log[4]},{log[2]},{log[11]}\n'
    return csv_data, 200, {'Content-Type': 'text/csv; charset=utf-8'}

# get single log by id user facing api
@app.route('/api/<key>/log/<int:id>')
def apiUserSingleLog(key, id):
    userid, privileged = checkKey(key)
    if not userid:
        return jsonify({"error": "Invalid API key"}), 403
    
    if privileged:
        userid = None
    
    logs = getLogs(user=userid, id=id)
    if not logs or len(logs) == 0:
        return jsonify({"error": "Log not found or not allowed to be viewed!"}), 404
    
    log = logs[0]
    log_data = {
        'user': log[1],
        'id': log[0],
        'mode': log[2],
        'date': log[3],
        'operator': log[4],
        'number': log[5],
        'type': log[6],
        'line': log[7],
        'start': log[8],
        'end': log[9],
        'notes': log[10],
        'tags': log[11],
    }
    return jsonify(log_data)

# csv via auth token
@app.route('/api/logs.csv')
def apiUserLogsCSVAuth():
    mode = request.args.get('mode', None)
    userid = session.get('user')['userinfo']['sub']
    
    if mode == 'All':
        mode = None
    
    if not userid:
        return jsonify({"error": "Invalid API key"}), 403
    
    logs = getLogs(user=userid, mode=mode)
    csv_data = "id,mode,date,operator,number,type,line,start,end,notes,tags\n"
    csv_data = "id,number,type,date,line,start,end,note,operator,mode,tag\n"
    for log in logs:
        csv_data += f'{log[0]},{log[5]},{log[6]},{log[3]},{log[7]},{log[8]},{log[9]},"{log[10]}",{log[4]},{log[2]},{log[11]}\n'
    filename = f"logs-{mode if mode else 'all'}.csv"
    headers = {
        'Content-Type': 'text/csv; charset=utf-8',
        'Content-Disposition': f'attachment; filename="{filename}"'
    }
    return csv_data, 200, headers

# user facing add log
@app.route('/api/<key>/addLog', methods=['POST'])
def apiAddLog(key):
    userid, privileged = checkKey(key)
    if not userid:
        return jsonify({"error": "Invalid API key"}), 403
    logInfo = request.form
        
    # thinh to make it so only tpv can add logs for other users
    if logInfo.get('userid') != userid:
        if privileged:
            userid = logInfo.get('userid')
        else:
            return jsonify({"error": "Not authorized to log for other users!"}), 403
    
    if logInfo.get('date') == None:
        date = datetime.datetime.now().strftime('%Y-%m-%d')
    else:
        date = logInfo.get('date')
    if logInfo.get('type') != None:
        type = logInfo.get('type')
        number = logInfo.get('number')
    else:
        if logInfo.get('mode') == 'victrain':
            number, type = setNumber(logInfo.get('number'))
            if number == None:
                number = logInfo.get('number')
            if type == None:
                type = logInfo.get('type')
                
        elif logInfo.get('mode') == 'victram':
            number, type = setNumberTram(logInfo.get('number'))
            if number == None:
                number = logInfo.get('number')
            if type == None:
                type = logInfo.get('type')
                
    # remove dashes
    if number.endswith('-'):
        number = number[:-1]
    
            
    # check date format
    try:
        datetime.datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid date format, should be YYYY-MM-DD"}), 400
    
    logInfo = dict(logInfo)
    logInfo['user'] = userid
    logInfo['date'] = date
    logInfo['number'] = number
    logInfo['type'] = type
    logInfo['user'] = userid
    logInfo['tags'] = None
    logInfo['operator'] = getOperator(logInfo.get('mode'), logInfo.get('type'))
    
    if logInfo.get('note') == None:
        logInfo['note'] = ''
    
    success = logTrip(
        user=logInfo.get('user'),
        mode=logInfo.get('mode'),
        date=logInfo.get('date'),
        vehicleNumber=logInfo.get('number'),
        vehicleType=logInfo.get('type'),
        start=logInfo.get('start'),
        end=logInfo.get('end'),
        line=logInfo.get('line'),
        operator=logInfo.get('operator'),
        note=logInfo.get('note'),
        tags=logInfo.get('tags'),
    )
    
    if not success:
        message = "Error adding trip to Database, please try again."
        print(f'error adding log: {logInfo}')
        return jsonify({"error": message}), 500
    else:
        message = jsonify({**logInfo, 'log_id': success})
        return message, 200
    
# user facing delete log via API key
@app.route('/api/<key>/deleteLog', methods=['POST'])
@limiter.limit("10 per minute")
def apiDeleteLog(key):
    userid, privileged = checkKey(key)
    if not userid:
        return jsonify({"error": "Invalid API key"}), 403

    data = request.get_json() or request.form
    logID = data.get('id')
    useridLogToDelete = data.get('userid', userid)

    # Only privileged keys can delete logs for other users
    if useridLogToDelete != userid:
        if privileged:
            userid = useridLogToDelete
        else:
            return jsonify({"error": "Not authorized to delete logs for other users!"}), 403

    logs = getLogs(user=userid, id=logID)
    if not logs or len(logs) == 0:
        return jsonify({"error": "Log not found or not allowed to be deleted!"}), 404

    success = deleteLog(logID)
    if success:
        return jsonify({"success": True, "message": "Log deleted successfully"}), 200
    else:
        return jsonify({"error": "Error deleting log"}), 500

# run ts
if __name__ == "__main__":
    app.run(debug=True, port=5002)
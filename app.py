# Main program entry

# import libraries
from flask import Flask, render_template, Response, session, request, redirect
from flask_session import Session
from tempfile import mkdtemp
import logging
from folium import plugins
import folium
from helper import login_required
import init
from init import drivers
import json
from random import *
import helper
from chatbot import chatbot_response
from datetime import date

# CONFIG
UPLOAD_FOLDER = './static/images'
ALLOWED_EXTENSIONS = {'txt', 'png', 'jpg', 'jpeg'}

# LOGGING CONFIG
logging.basicConfig(    
    level=logging.WARNING,
    filename='./log/{}-SERVERLOG.log'.format(str(date.today())),
    encoding='utf-8' 
    )

# FLASK CONFIG
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024 # 5MB MAX
app.config['TEMPLATES_AUTO_RELOAD'] = True

# FLASK SESSION CONFIG
app.config['SESSION_FILE_DIR'] = mkdtemp()
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Expires'] = 0
    response.headers['Pragma'] = 'no-cache'
    return response

# main index
@app.route('/', methods=['GET','POST'])
def index():

    # gets login details
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # auths user
        if auth_user(username, password):
            session['user_id'] = username
            return redirect('/map')
        else:
            session.clear()
        
    return render_template('index.html')


@app.route('/map', methods=['GET','POST'])
@login_required
def map():
    m = folium.Map(location=[1.3541, 103.8198], tiles="OpenStreetMap", zoom_start=12, control_scale=True)
    return render_template('map.html', map = m._repr_html_())

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":    
        username = request.form.get("username")
        pw = request.form.get("password")
        
        init.store.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, pw,))
        init.store.commit()
        
        # Redirect user to success
        return redirect('/')

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route('/api/getroute', methods=['POST'])
@login_required
def getroute():

    m = folium.Map(location=[1.3541, 103.8198], tiles="OpenStreetMap", zoom_start=12, control_scale=True)

    data = request.json
    start = data['start']
    end = data['end']
    pax = int(data['pax'])
    type = data['type']
    rt = data['routetype']

    startNode = helper.getNode(init.store,init.vt, start)
    endNode = helper.getNode(init.store, init.vt, end)
    driver = init.heuristicAlgo(startNode, pax, type)

    folium.Marker(
        location = init.vt[startNode],
        icon = plugins.BeautifyIcon(
            background_color='#00CDFF',
            number = 'PAX START'
        )
    ).add_to(m)

    folium.Marker(
        location = init.vt[endNode],
        icon = plugins.BeautifyIcon(
            background_color='#00CDFF',
            number = 'PAX END'
        )
    ).add_to(m)

    if type == 'pool':
        pax2Start = str(randint(0, 123))
        pax2End = pax2Start
        while pax2End == pax2Start:
            pax2End = str(randint(0, 123))
        res = init.sharedRoute(startNode, endNode, pax2Start, pax2End)
        res2 = init.graph1.getShortestPath(driver['loc'], startNode, init.edges1) #driver to pax

        folium.Marker(
            location = init.vt[pax2Start],
            icon = plugins.BeautifyIcon(
                background_color='#00CDFF',
                number = 'PAX 2 START'
            )
        ).add_to(m)

        folium.Marker(
            location = init.vt[pax2End],
            icon = plugins.BeautifyIcon(
                background_color='#00CDFF',
                number = 'PAX 2 END'
            )
        ).add_to(m)

        if res is not None:
            for i in res:
                plugins.AntPath(
                    locations = i['route']
                ).add_to(m)

            plugins.AntPath(
            locations = res2['route'], color = 'red',
        ).add_to(m)

            folium.Marker(
        location = res2['route'][0],
        icon = plugins.BeautifyIcon(
            background_color='#00CDFF',
            number = 'DRIVER'
        )
    ).add_to(m)

            m.fit_bounds([init.vt[endNode], res2['route'][0]], max_zoom=15)

            return Response(m._repr_html_())

    route1 = init.graph1.getShortestPath(startNode, endNode, init.edges1) # pax
    route2 = init.graph1.getShortestPath(driver['loc'], startNode, init.edges1) #driver to pax

    route3 = init.graph2.getShortestPath(startNode, endNode, init.edges2) # pax
    route4 = init.graph2.getShortestPath(driver['loc'], startNode, init.edges2) #driver to pax

    if rt == 'shortest' or rt == 'both':
        plugins.AntPath(
            locations = route1['route'], color = 'blue',
        ).add_to(m)

        plugins.AntPath(
            locations = route2['route'], color = 'red',
        ).add_to(m)
    if rt == 'fastest' or rt == 'both':
        plugins.AntPath(
            locations = route3['route'], color = 'blue',
        ).add_to(m)

        plugins.AntPath(
            locations = route4['route'], color = 'red',
        ).add_to(m)

    folium.Marker(
        location = route2['route'][0],
        icon = plugins.BeautifyIcon(
            background_color='#00CDFF',
            number = 'DRIVER'
        )
    ).add_to(m)

    m.fit_bounds([init.vt[endNode], route2['route'][0]], max_zoom=15)

    return Response(m._repr_html_())

@app.route('/api/getpoints', methods=['POST'])
@login_required
def getvertex():
    m = folium.Map(location=[1.3541, 103.8198], tiles="OpenStreetMap", zoom_start=12, control_scale=True)
    for k, v in init.vt.items():
        folium.Marker(
            location = v,
            icon = plugins.BeautifyIcon(
                background_color='#00FF66',
                number = k
            )
        ).add_to(m)
    for k, v in init.edges1.items():
        folium.PolyLine(
            locations = v['polyline']
        ).add_to(m)

    m.fit_bounds([init.vt['9'], init.vt['1']], max_zoom=15)

    return Response(m._repr_html_())

@app.route('/api/ai', methods=['POST'])
@login_required
def ai():
    ls = []
    for i in init.onroad:
        try:
            ret = {
                'id':i['id'],
                'loc':i['route']['route'][0],
            }
            del i['route']['route'][0]
            ls.append(ret)
        except:
            i['route'] = drivers.randomRoute(init.graph1, init.edges1, init.vt)
            ret = {
                'id': i['id'],
                'loc':i['route']['route'][0]
            }
            del i['route']['route'][0]
            ls.append(ret)
        
    msg = json.dumps(ls)
    return Response(msg)

@app.route('/drivers', methods=['GET', 'POST'])
@login_required
def driver():

    return render_template('driver.html')

@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect('/')

def auth_user(username, password):

    rows = init.store.execute("SELECT COUNT(id) FROM users WHERE username = ? AND password = ?", (username, password,)).fetchone()
    if rows[0] != 1:
        return False
    return True

@app.route('/chatbot')
@login_required
def chatbot():
    return render_template('chatbot.html')

@app.route('/get')
@login_required
def get_bot_response():
    userText = request.args.get('msg')
    print(userText)
    return chatbot_response(str(userText))

if __name__ == '__main__':
    app.run(debug=True, port=5001) 
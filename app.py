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
    level=logging.INFO,
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

# main index endpoint
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
    # renders the template
    return render_template('index.html')

# main map endpoint
@app.route('/map', methods=['GET','POST'])
@login_required
def map():
    # renders folium as base map
    m = folium.Map(location=[1.3541, 103.8198], tiles="OpenStreetMap", zoom_start=12, control_scale=True)
    return render_template('map.html', map = m._repr_html_())

# register endpoint
@app.route("/register", methods=["GET", "POST"])
def register():

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

# api endpoint to get route
@app.route('/api/getroute', methods=['POST'])
@login_required
def getroute():

    # renders folium map
    m = folium.Map(location=[1.3541, 103.8198], tiles="OpenStreetMap", zoom_start=12, control_scale=True)

    # get data from AJAX request
    data = request.json 
    start = data['start'] # start postal
    end = data['end'] # end postal
    pax = int(data['pax']) # number of pax in int
    type = data['type'] # type of ride: pool or standard
    rt = data['routetype'] # routetype: fastest, shortest, both

    # get nearest node from postal code
    startNode = helper.getNode(init.store,init.vt, start) # startNode
    endNode = helper.getNode(init.store, init.vt, end) # endNode

    # uses heuristic to deterine which driver to pick pax
    driver = init.heuristicAlgo(startNode, pax, type)

    # add marker for pax start
    folium.Marker(
        location = init.vt[startNode],
        icon = plugins.BeautifyIcon(
            background_color='#00CDFF',
            number = 'PAX START'
        )
    ).add_to(m)

    # add marker for pax end
    folium.Marker(
        location = init.vt[endNode],
        icon = plugins.BeautifyIcon(
            background_color='#00CDFF',
            number = 'PAX END'
        )
    ).add_to(m)

    # checks if the request is of pool type (shared ride)
    if type == 'pool':
        # randoms the start location of a 2nd passenger
        pax2Start = str(randint(0, 123))
        # randoms the end location of a 2nd passenger to make sure its not the same as its start
        pax2End = pax2Start
        while pax2End == pax2Start:
            pax2End = str(randint(0, 123))
        # run algorithm to get shared Route
        res = init.sharedRoute(startNode, endNode, pax2Start, pax2End)
        # get shortest path from driver to start node
        res2 = init.graph1.getShortestPath(driver['loc'], startNode, init.edges1) #driver to pax

        # draw marker for pax 2 start position
        folium.Marker(
            location = init.vt[pax2Start],
            icon = plugins.BeautifyIcon(
                background_color='#00CDFF',
                number = 'PAX 2 START'
            )
        ).add_to(m)

        # draw marker for pax 2 end position
        folium.Marker(
            location = init.vt[pax2End],
            icon = plugins.BeautifyIcon(
                background_color='#00CDFF',
                number = 'PAX 2 END'
            )
        ).add_to(m)

        # if return route from shareedroute function is not none
        if res is not None:
            # for each entry in return route
            for i in res:
                # draw path
                plugins.AntPath(
                    locations = i['route']
                ).add_to(m)

            # draw path for driver to startNode
            plugins.AntPath(
            locations = res2['route'], color = 'red',
        ).add_to(m)

            # draw marker for driver location
            folium.Marker(
        location = res2['route'][0],
        icon = plugins.BeautifyIcon(
            background_color='#00CDFF',
            number = 'DRIVER'
        )
    ).add_to(m)
            
            # zooms map to bounds
            m.fit_bounds([init.vt[endNode], res2['route'][0]], max_zoom=15)

            # returns html as response
            return Response(m._repr_html_())

    # gets routees for shortest path
    route1 = init.graph1.getShortestPath(startNode, endNode, init.edges1) # pax
    route2 = init.graph1.getShortestPath(driver['loc'], startNode, init.edges1) #driver to pax
    # gets routees for longest path
    route3 = init.graph2.getShortestPath(startNode, endNode, init.edges2) # pax
    route4 = init.graph2.getShortestPath(driver['loc'], startNode, init.edges2) #driver to pax

    # if routetype is shortest or both
    if rt == 'shortest' or rt == 'both':
        # draws antpath for shortest route for pax start to end
        plugins.AntPath(
            locations = route1['route'], color = 'blue',
        ).add_to(m)
        # draws antpath for shortest route for driver to pax start
        plugins.AntPath(
            locations = route2['route'], color = 'red',
        ).add_to(m)
    # if routetype is fastest or both
    if rt == 'fastest' or rt == 'both':
        # draws antpath for fastest for pax start to end
        plugins.AntPath(
            locations = route3['route'], color = 'blue',
        ).add_to(m)
        # draws antpath for shortest route for driver to pax start
        plugins.AntPath(
            locations = route4['route'], color = 'red',
        ).add_to(m)
    # draws marker for driver
    folium.Marker(
        location = route2['route'][0],
        icon = plugins.BeautifyIcon(
            background_color='#00CDFF',
            number = 'DRIVER'
        )
    ).add_to(m)
    # zooms map and fit to bbounds
    m.fit_bounds([init.vt[endNode], route2['route'][0]], max_zoom=15)

    # return response of folium m html
    return Response(m._repr_html_())

# api endpoint for user to get vertex and edges
@app.route('/api/getpoints', methods=['POST'])
@login_required
def getvertex():
    # init folium map object
    m = folium.Map(location=[1.3541, 103.8198], tiles="OpenStreetMap", zoom_start=12, control_scale=True)
    for k, v in init.vt.items():
        # draw marker to mark all the vertexes
        folium.Marker(
            location = v,
            icon = plugins.BeautifyIcon(
                background_color='#00FF66',
                number = k
            )
        ).add_to(m)
    # draw markers for edges 
    for k, v in init.edges1.items():
        folium.PolyLine(
            locations = v['polyline']
        ).add_to(m)
    # fit to bounds
    m.fit_bounds([init.vt['9'], init.vt['1']], max_zoom=15)
    # return response html for folium
    return Response(m._repr_html_())

# endpoint to show drivers moving
@app.route('/api/ai', methods=['POST'])
@login_required
def ai():
    ls = []
    for i in init.onroad:
        # append latest coordinates by using FIFO, index 0, and decrement the location after appending
        try:
            ret = {
                'id':i['id'],
                'loc':i['route']['route'][0],
            }
            del i['route']['route'][0]
            ls.append(ret)
        except:
            # generate new route if len of location < 0
            i['route'] = drivers.randomRoute(init.graph1, init.edges1, init.vt)
            ret = {
                'id': i['id'],
                'loc':i['route']['route'][0]
            }
            del i['route']['route'][0]
            ls.append(ret)
    
    # formats the output into json return
    msg = json.dumps(ls)
    # return response of json msg
    return Response(msg)

# endpoint to show drivers location
@app.route('/drivers', methods=['GET', 'POST'])
@login_required
def driver():
    # render driver template
    return render_template('driver.html')

# endpoint to log user out
@app.route('/logout')
@login_required
def logout():
    # clear session
    session.clear()
    # redirect to index
    return redirect('/')

# function to authenticate user 
def auth_user(username, password):
    # checks whether there is an entry with the given username and password
    rows = init.store.execute("SELECT COUNT(id) FROM users WHERE username = ? AND password = ?", (username, password,)).fetchone()
    if rows[0] != 1:
        return False
    return True

# endpoint for chatbot
@app.route('/chatbot')
@login_required
def chatbot():
    # return render chatbot
    return render_template('chatbot.html')

# endpoint for chatbot to get msg
@app.route('/get')
@login_required
def get_bot_response():
    # processes user inputs
    userText = request.args.get('msg')
    # return chatbot response
    return chatbot_response(str(userText))

# enntry to run the main program flask on port 5001
if __name__ == '__main__':
    app.run(debug=True, port=5001) 
# import libraries
from flask import redirect, session
from functools import wraps
from geopy.distance import geodesic

# define wraps for login routes
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function

# latlong in tuple
def getNearestNode(latlong, vt):
    min = 999999
    node = ''
    for vt, c in vt.items():
        dist = getDistance(latlong, c)
        if dist < min:
            min = dist
            node = vt
    return node

def getLatLong(db, postal):
    rows = db.execute("SELECT * FROM sg WHERE postal = ?", (postal,)).fetchone()
    if rows != None:
        return rows[3], rows[4]

# a and b in tuples
def getDistance(a, b):
    n1 = tuple(a)
    n2 = tuple(b)
    return geodesic(n1, n2).meters

def distToTime(meters):
    # conversion factor based on 50km/h speed average, not on expressways
    # returns in mins
    return meters/50000 * 60

def getNode(db, vt, postal):
    latlong = getLatLong(db, postal)
    return getNearestNode(latlong, vt)
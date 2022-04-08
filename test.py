import json
import time
import requests
from init import helper

f = open('./data/vt.json')
vt = json.load(f)
f.close()

f1 = open('./data/edges.json')
vt1 = json.load(f1)
f1.close()

out = []

for i in vt1:
    if i['dist'] == 0:
        print(i)

# for i in vt1:
#     if i['vFrom'] == '23' and i['vTo'] == '22':
#         print(i)

# ab = open('./data/outfile.json', 'w')
# json.dump(out, ab)
# ab.close()


# def getNearestNodes(latlong, vt):

#     d = []
#     for vt, c in vt.items():
#         dist = helper.getDistance(latlong, c)
#         d.append([dist, vt])
#     sorts = sorted(d, key=lambda tup: tup[0])
#     # print(d[0:10])
#     # print(sorts[1:10])

#     # return sorts[1:9]
#     return sorts[9:10]

# # getNearestNodes(('1.3774', '103.8487'), vt)
# # getNearestNodes(('1.373087', '103.828583'), vt)

# def details(st,ed):

#     pickup_lon = st[1]
#     pickup_lat = st[0]
#     dropoff_lon = ed[1]
#     dropoff_lat = ed[0]
#     loc = "{},{};{},{}".format(pickup_lon, pickup_lat, dropoff_lon, dropoff_lat)
#     url = "https://router.project-osrm.org/route/v1/driving/"
#     r = requests.get(url + loc) 
#     if r.status_code!= 200:
#         return {}
  
#     res = r.json()
#     # routes = polyline.decode(res['routes'][0]['geometry']) if wn use route coord
#     routes = res['routes'][0]['geometry']
#     start_point = [res['waypoints'][0]['location'][1], res['waypoints'][0]['location'][0]]
#     end_point = [res['waypoints'][1]['location'][1], res['waypoints'][1]['location'][0]]
#     distance = res['routes'][0]['distance']
    
#     out = {'start_point':start_point,
#            'end_point':end_point,
#            'route':routes,
#            'distance':distance
#           }

#     # print("startpoint: ", start_point)
#     # print("endpoint: ", end_point)
#     print("polyline encoded: ", routes)
#     print("distance: ", distance)
#     print()

#     return routes, distance


# a = open('./data/dataout.json', 'w')

# for v, c in vt.items():
#     gt = getNearestNodes(c, vt)
#     for i in gt:
#         dout = {}
#         dout['vFrom'] = v
#         dout['vFromLatLong'] = c
#         dout['vTo'] = i[1]
#         dout['vToLatLong'] = vt[i[1]]
#         dt = details(dout['vFromLatLong'], dout['vToLatLong'])
#         dout['polyline'] = dt[0]
#         dout['dist'] = dt[1]
#         vt1.append(dout)
#         time.sleep(1.05)

# json.dump(vt1, a)
# a.close()


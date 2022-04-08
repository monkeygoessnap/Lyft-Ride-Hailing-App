var customIcon = L.icon({
  iconUrl:'https://img.auto-che.com/logo/qim/bmw.png',
  iconSize: [30, 30]
});

// const json = require("../dataout.json");
// console.log(json)

var mymap = L.map('mapid').setView([1.3541, 103.8198], 13);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
	maxZoom: 19,
	attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(mymap);

// var polyline = L.polyline(latlngs, {
//   color: 'red'
// }).addTo(mymap);

function getRoute() {
    var start = document.getElementById('start').value;
    var end = document.getElementById('end').value;
    var pax = document.getElementById('pax').value;
    var type = document.getElementById('type').value;
    var routetype = document.getElementById('routetype').value;

    var tosend = {
        start:start,
        end:end,
        pax:pax,
        type:type,
        routetype:routetype
    }
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/api/getroute', true);
    xhr.setRequestHeader('Content-type', 'application/json');
    var cont = document.getElementById('main')
    xhr.onload = function(){
      cont.innerHTML = xhr.response;
    }
    xhr.send(JSON.stringify(tosend));
}

function getPoints() {
  var xhr = new XMLHttpRequest();
  xhr.open('POST', '/api/getpoints', true);
  xhr.setRequestHeader('Content-type', 'application/json');
  var cont = document.getElementById('main')
  xhr.onload = function(){
    cont.innerHTML = xhr.response;
  }
  xhr.send();
}


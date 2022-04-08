var customIcon = L.icon({
    iconUrl:'https://img.auto-che.com/logo/qim/bmw.png',
    iconSize: [30, 30]
  });

var mymap = L.map('mapid').setView([1.3541, 103.8198], 13);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
	maxZoom: 19,
	attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(mymap);

mapMarkers1 = []
mapMarkers2 = []
mapMarkers3 = []
mapMarkers4 = []

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve,ms));
  }

  async function getLoc(){
    while (true) {
      var xhr = new XMLHttpRequest();
      xhr.open('POST', '/api/ai', true);
      xhr.setRequestHeader('Content-type', 'application/json');
      xhr.onload = function(){
        console.log(xhr.response)
        var c = JSON.parse(xhr.response)
        for (var i = 0; i < c.length; i++) {
          if (c[i].id == '1111') {
            for (var j = 0; j < mapMarkers1.length; j++) {
              mymap.removeLayer(mapMarkers1[j]);
              mapMarkers1.pop();
            }
            var marker1 = L.marker(
              c[i].loc,
              {
                icon: customIcon,
              }
            ).addTo(mymap);
            mapMarkers1.push(marker1);
          }
          if (c[i].id == '2222') {
            for (var j = 0; j < mapMarkers2.length; j++) {
              mymap.removeLayer(mapMarkers2[j]);
              mapMarkers2.pop();
            }
            var marker2 = L.marker(
              c[i].loc,
              {
                icon: customIcon,
              }
            ).addTo(mymap);
            mapMarkers2.push(marker2);
          }
          if (c[i].name == '3333') {
            for (var j = 0; j < mapMarkers3.length; j++) {
              mymap.removeLayer(mapMarkers3[j]);
              mapMarkers3.pop();
            }
            var marker3 = L.marker(
              c[i].loc,
              {
                icon: customIcon,
              }
            ).addTo(mymap);
            mapMarkers3.push(marker3);
          }
        if (c[i].name == '4444') {
            for (var j = 0; j < mapMarkers4.length; j++) {
                mymap.removeLayer(mapMarkers4[j]);
                mapMarkers4.pop();
            }
            var marker4 = L.marker(
                c[i].loc,
                {
                icon: customIcon,
                }
            ).addTo(mymap);
            mapMarkers4.push(marker4);
          }
        }
      }
        xhr.send(JSON.stringify());
        await sleep(500)
    }
  }
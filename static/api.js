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


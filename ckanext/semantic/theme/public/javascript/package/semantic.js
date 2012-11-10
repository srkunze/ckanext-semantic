var map_element = document.getElementById('map');

var latitude = 180 * parseFloat(map_element.attributes['latitude'].value) / Math.PI;
var longitude = 180 * parseFloat(map_element.attributes['longitude'].value) / Math.PI;
var radius = parseFloat(map_element.attributes['radius'].value);

var map = L.map('map');
map.setView([latitude, longitude], 1);

L.tileLayer('http://{s}.tile.cloudmade.com/BC9A493B41014CAABB98F0471D759707/997/256/{z}/{x}/{y}.png', {
    attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://cloudmade.com">CloudMade</a>',
    maxZoom: 20
}).addTo(map);

var circle = L.circle([latitude, longitude], 1000.0 * radius, {
                color: 'red',
                fillColor: '#F03',
                fillOpacity: 0.5
            }).addTo(map);

var bounds = circle.getBounds();
var zoom = map.getBoundsZoom(bounds, inside=false);
map.setView([latitude, longitude], Math.max(0, zoom-1));


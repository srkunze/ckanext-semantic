var map_element = document.getElementById('map');

var latitude = 180 * parseFloat(map_element.attributes['latitude'].value) / Math.PI;
var longitude = 180 * parseFloat(map_element.attributes['longitude'].value) / Math.PI;
var radius = parseFloat(map_element.attributes['radius'].value);

var map = L.map('map');
map.setView([latitude, longitude], 1);

L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
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


$(function() {
    $.widget( "custom.catcomplete", $.ui.autocomplete, {
        _renderMenu: function( ul, items ) {
            var that = this;
            var currentCategory = "";
            ul.css('zIndex', 10000)
            $.each( items, function( index, item ) {
                if ( item.category != currentCategory ) {
                    ul.append( "<li class='ui-autocomplete-category'>" + 
                                      {'vocabulary': 'Vocabularies',
                                      'class': 'Classes',
                                      'property': 'Properties'}[item.category]
                                      
                               + "</li>" );
                    currentCategory = item.category;
                }
                that._renderItemData( ul, item );
            });
        }
    });


    $( "#topic_input" ).catcomplete({
        minLength: 3,
        position: { my : "left center", at: "right+69px top" },
        source: function(request, response){
            $.ajax({
                url: "api/action/uri_suggestions?query="+request.term,
                dataType: 'json',
                success: function( data ) {
                    response(data.result);
                }
            });
        },
        focus: function( event, ui ) {
            //$( "#topic_input" ).val( ui.item.uri );
            return false;
        },
        select: function( event, ui ) {
            $( "#topic_input" ).val( ui.item.uri );
            document.forms.topic_form.submit();
            return false;
        }
    })
    .data( "catcomplete" )._renderItem = function( ul, item ) {
        return $( "<li>" )
            .data( "item.autocomplete", item )
            .append( "<a><b>" + item.label + "</b><br>" + item.uri + "</a>" )
            .appendTo( ul );
    };
});


var latitude = document.forms.location.location_latitude;
var longitude =document.forms.location.location_longitude;
var radius = document.forms.location.location_radius;

var map = L.map('map');

map.setView([0, 0], 1);

L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 20
}).addTo(map);

var circle = null;

function onMapClick(event)
{
    latitude.value = event.latlng.lat;
    longitude.value = event.latlng.lng;
    
    update_circle(false);
}
map.on('click', onMapClick);

function update_circle(moveMap)
{
    var lat = parseFloat(latitude.value);
    var lng = parseFloat(longitude.value);
    var rad = parseFloat(radius.value);

    if(circle)
    {
        map.removeLayer(circle);
    }
    
    circle = L.circle([lat, lng], 1000.0 * rad, {
        color: 'red',
        fillColor: '#F03',
        fillOpacity: 0.5
    }).addTo(map);

    circle.on('click', onMapClick);

    if (moveMap)
    {
        var bounds = circle.getBounds();
        var zoom = map.getBoundsZoom(bounds, inside=false);
        map.setView([lat, lng], Math.max(0, zoom-2));
    }
}

latitude.addEventListener('change', function(){update_circle(true);});
longitude.addEventListener('change', function(){update_circle(true);});
radius.addEventListener('change', function(){update_circle(true);});

if(latitude.value)
{
    update_circle(true);
}



function result_maps()
{
    var map_elements = document.getElementsByClassName('map');
    
    for(var index = 0; index < map_elements.length; index += 1)
    {
        var map_element = map_elements[index];
        var latitude = 180 * parseFloat(map_element.attributes['latitude'].value) / Math.PI;
        var longitude = 180 * parseFloat(map_element.attributes['longitude'].value) / Math.PI;
        var radius = parseFloat(map_element.attributes['radius'].value);

        var map = L.map(map_element);
        map.setView([latitude, longitude], 1);

        L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
            attribution: 'Map data &copy; cf. sidebar',
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
    }
}

result_maps();


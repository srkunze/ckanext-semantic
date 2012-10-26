document.querySelector('#create_subscription').addEventListener('click', function(){
    json = {};

    if(document.querySelector('#topics .checkbox').checked)
    {
        json['topics'] = [];
        topic_names = document.querySelectorAll('#topics .topic .name');
        for (index = 0; index < topic_names.length; index += 1) 
        {
            json['topics'].push(topic_names[index].textContent);
        }
        
        if(json['topics'].length == 0)
        {
            delete json['topics']
        }
    }

    if(document.querySelector('#location .checkbox').checked)
    {
        json['location'] = {};
        json['location']['latitude'] = document.querySelector('#location .latitude').value;
        json['location']['longitude'] = document.querySelector('#location .longitude').value;
        json['location']['radius'] = document.querySelector('#location .radius').value;
        json['location']['geoname'] = document.querySelector('#location .geoname').value;
    }

    if(document.querySelector('#time .checkbox').checked)
    {
        json['time'] = {}
        if(document.querySelector('#time .time_type_span').checked)
        {
            json['time']['type'] = 'span'
            json['time']['min'] = document.querySelector('#time .min').value;
            json['time']['max'] = document.querySelector('#time .max').value;
        }
        if(document.querySelector('#time .time_type_point').checked)
        {
            json['time']['type'] = 'point'
            json['time']['point'] = document.querySelector('#time .point').value;
            json['time']['variance'] = document.querySelector('#time .variance').value;
        }
    }

    document.create_form.subscription_definition.value = JSON.stringify(json)
    document.create_form.submit()
})


document.querySelector('#topics .add').addEventListener('click', function(){
    topic_template_node = document.querySelector('#topics .topic_template')
    topic_node = topic_template_node.cloneNode(true)
    topic_node.removeAttribute('style')
    topic_node.setAttribute('class', 'topic')
    topic_node.querySelector('.name').textContent = document.querySelector('#topics .input_uri').value
    topic_node.querySelector('.delete').addEventListener('click', function(){
        topic_node = this.parentNode
        topic_node.parentNode.removeChild(topic_node)
    })
    
    topic_template_node.parentNode.insertBefore(topic_node, topic_template_node)
})


topicRemoveButtons = document.querySelectorAll('#topics .topic .delete')
for(index = 0; index < topicRemoveButtons.length; index += 1)
{
    topicRemoveButtons[index].addEventListener('click', function(){
        topic_node = this.parentNode
        topic_node.parentNode.removeChild(topic_node)
    })
}


document.querySelector('#topics .checkbox').addEventListener('click', function(){
    document.querySelector('#topics .hideable').style['display'] = this.checked ? '' : 'none'
})
document.querySelector('#location .checkbox').addEventListener('click', function(){
    document.querySelector('#location .hideable').style['display'] = this.checked ? '' : 'none'
})
document.querySelector('#time .checkbox').addEventListener('click', function(){
    document.querySelector('#time .hideable').style['display'] = this.checked ? '' : 'none'
})




var cache = {};

$.ajax(
{
    url: "/vocabulary",
    dataType: "json",
    success: function( data )
    {
        for(index = 0; index < data.length; index += 1)
        {
            data[index].value = data[index].title + data[index].prefix
            data[index].id = data[index].vocabulary
        }
        
        $('#topics .input').autocomplete(
        {
            source: data,
            minLength: 0,
            focus: function( event, ui ) {
                $( "#project" ).val( ui.item.title );
                
                return false;
            },
            select: function( event, ui )
            {
                $('#topics .input').val(ui.item.title)
                $('#topics .input_uri').val(ui.item.vocabulary)
                
                return false;
            }
        }).data( "autocomplete" )._renderItem = function( ul, item )
        {
            return $( "<li>" )
                .data( "item.autocomplete", item )
                .append( '<a><b>' + item.title + '</b><br /><b>Prefix:</b> ' + item.prefix + '<br /><b>URI:</b> ' + item.vocabulary + '</a>' )
                .appendTo( ul );
        }
    }
});


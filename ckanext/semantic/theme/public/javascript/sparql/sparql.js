var editor = CodeMirror.fromTextArea(document.getElementById('sparql-textarea'), {
    mode: 'application/x-sparql-query',
    tabMode: 'indent',
    matchBrackets: true,
    indentUnit: 4,
    lineNumbers: true
});

$(function() {
    $.widget( "custom.catcomplete", $.ui.autocomplete, {
        _renderMenu: function( ul, items ) {
            var that = this,
                currentCategory = "";
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


    $( "#uri-suggestion" ).catcomplete({
        minLength: 3,
        position: { my : "left top", at: "left+27px bottom" },
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
            $( "#uri-suggestion" ).val( ui.item.uri );
            return false;
        },
        select: function( event, ui ) {
            $( "#uri-suggestion" ).val( ui.item.uri );
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


var editor = CodeMirror.fromTextArea(document.getElementById('sparql-textarea'), {
    mode: 'application/x-sparql-query',
    tabMode: 'indent',
    matchBrackets: true,
    indentUnit: 4,
    lineNumbers: true
});


var cache = {};
$.ajax(
{
    url: "/vocabulary",
    dataType: "json",
    success: function( data )
    {
        x = []
        for(index = 0; index < data.length; index += 1)
        {
            x.push(data[index].vocabulary);
        }
        
        
        $('#vocabulary_suggestions').typeahead({ source: x });
    }
});

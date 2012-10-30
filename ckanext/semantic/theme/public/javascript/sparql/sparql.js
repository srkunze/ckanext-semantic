var editor = CodeMirror.fromTextArea(document.getElementById('sparql-textarea'), {
    mode: 'application/x-sparql-query',
    tabMode: 'indent',
    matchBrackets: true,
    indentUnit: 4,
    lineNumbers: true
});


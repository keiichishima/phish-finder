var N_MAX_TABLE_ROWS = 100

var uri = 'ws://127.0.0.1:5678/';
var webSocket = null;

function wsInit() {
    if (webSocket == null) {
	webSocket = new WebSocket(uri);
	webSocket.onopen = wsOnOpen;
	webSocket.onmessage = wsOnMessage;
	webSocket.onclose = wsOnClose;
	webSocket.onerror = wsOnError;
    }
}

function wsOnOpen(event) {
    console.info('ws opened.');
}

function wsOnMessage(event) {
    _data = JSON.parse(event.data);
    for (var _d in _data) {
	console.log(_data[_d])
	var _time = _data[_d][0];
	var _url = _data[_d][1].slice(0,60);
	var _score = _data[_d][2];
	var _row = $('<tr/>');
	$('<td/>', {text: _time}).appendTo(_row);
	$('<td/>', {text: _url}).appendTo(_row);
	var _sctd = $('<td/>', {text: _score})
	if (_score > 0) {
	    _sctd.attr({class: 'suspicious'});
	} else {
	    _sctd.attr({class: 'benign'});
	}
	_sctd.appendTo(_row);
	_row.hide().prependTo('#table_body').show('slow');
    }
    var _count = $('#table_body tr').length;
    if (_count - N_MAX_TABLE_ROWS > 0) {
	for (var _i = 0; _i < _count - N_MAX_TABLE_ROWS; _i = _i + 1) {
	    $('#table_body tr').last().remove();
	}
    }
}

function wsOnClose(event) {
    console.info('ws closed.');
}

function wsOnError(event) {
    console.info('ws error.');
}

$(document).ready(function() {
    wsInit();
})

var N_MAX_TABLE_ROWS = 100

var uri = 'ws://127.0.0.1:5678/';
var webSocket = null;

function formatTimestamp(_timestamp) {
    var _d = new Date(_timestamp * 1000);
    return (('0000' + _d.getFullYear()).substr(-4)
	    + '-' + ('00' + (Number(_d.getMonth()) + 1)).substr(-2)
	    + '-' + ('00' + _d.getDate()).substr(-2)
	    + 'T' + ('00' + _d.getHours()).substr(-2)
	    + ':' + ('00' + _d.getMinutes()).substr(-2)
	    + ':' + ('00' + _d.getSeconds()).substr(-2)
	    + '.' + ('000' + _d.getMilliseconds()).substr(-3))
}

function wsInit() {
    if (webSocket == null) {
	webSocket = new WebSocket(uri);
	webSocket.onopen = wsOnOpen;
	webSocket.onmessage = wsOnMessage;
	webSocket.onclose = wsOnClose;
	webSocket.onerror = wsOnError;
    }
}

function wsOnOpen(_event) {
    console.info('ws opened.');
}

function wsOnMessage(_event) {
    _data = JSON.parse(_event.data);
    for (var _i = 0; _i < _data.length; _i = _i + 1) {
	var _time = formatTimestamp(_data[_i].time);
	var _url = _data[_i].url
	var _url_short = _url.slice(0,80);
	var _score = (Math.tanh(_data[_i].score) + 1) * 0.5
	if (_score < 0.1) {
	    continue
	}
	var _row = $('<tr/>');
	$('<td/>', {text: _time}).appendTo(_row);
	$('<td/>', {html: '<a href="http://' + _url + '">' + 'http://' + _url_short + '</a>'}).appendTo(_row);
	var _sctd = $('<td/>', {text: (_score * 100).toFixed() + '%'});
	_red_value = (_score * 255).toFixed();
	_blue_value = ((1 - _score) * 255).toFixed();
	_sctd.attr({style: 'color: white; background-color: rgb('
		    + _red_value + ',0,' + _blue_value + ')'})
	_sctd.appendTo(_row);
	_row.hide().prependTo('#table_body').show('fast');
    }
    var _count = $('#table_body tr').length;
    if (_count - N_MAX_TABLE_ROWS > 0) {
	for (var _i = 0; _i < _count - N_MAX_TABLE_ROWS; _i = _i + 1) {
	    $('#table_body tr').last().remove();
	}
    }
}

function wsOnClose(_event) {
    console.info('ws closed.');
}

function wsOnError(_event) {
    console.info('ws error.');
}

$(document).ready(function() {
    wsInit();
})

function moreInfo() {
    $('#smalltitle').hide('fast');
    $('#bigtitle').show('slow');
}

function lessInfo() {
    $('#smalltitle').show('fast');
    $('#bigtitle').hide('slow');
}

var N_MAX_ALERTS_TABLE_ROWS = 1000
var N_MAX_LIVE_TABLE_ROWS = 50

var uri = 'ws://127.0.0.1:5678/';
var webSocket = null;

function moreInfo() {
    $('#smalltitle').slideUp();
    $('#bigtitle').slideDown();
}

function lessInfo() {
    $('#smalltitle').slideDown();
    $('#bigtitle').slideUp();
}

function formatTimestamp(_timestamp) {
    var _d = new Date(_timestamp * 1000);
    return (('0000' + _d.getFullYear()).substr(-4)
	    + '-' + ('00' + (Number(_d.getMonth()) + 1)).substr(-2)
	    + '-' + ('00' + _d.getDate()).substr(-2)
	    + 'T'
	    + ('00' + _d.getHours()).substr(-2)
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

function trimTableRows(_table_id, _limit) {
    var _count = $(_table_id + ' tr').length;
    if (_count - _limit > 0) {
	for (var _i = 0; _i < _count - _limit; _i = _i + 1) {
	    $(_table_id + ' tr').last().remove();
	}
    }
}

function wsOnMessage(_event) {
    _data = JSON.parse(_event.data);
    for (var _i = 0; _i < _data.length; _i = _i + 1) {
	var _time = formatTimestamp(_data[_i].time);
	var _url = _data[_i].url;
	var _url_short = _url;
	if (_url.length > 100) {
	    _url_short = _url.slice(0, 100) + '...';
	}
	var _src = _data[_i].src;
	var _dst = _data[_i].dst;
	var _prob = _data[_i].prob;
	var _row = $('<tr/>');
	$('<td/>', {html: _time}).appendTo(_row);
	$('<td/>', {html: '<a target="_blank" href="http://' + _url + '">'
		    + 'http://' + _url_short
		    + '</a>',
		    style: 'word-break: break-all;'}).appendTo(_row);
	$('<td/>', {html: _src + '<br/>' + _dst}).appendTo(_row);
	var _sctd = $('<td/>', { text: (_prob * 100).toFixed() + '%'});
	_red_value = (_prob * 255).toFixed();
	_blue_value = ((1 - _prob) * 255).toFixed();
	_sctd.attr({style: 'color: white; background-color: rgb('
		    + _red_value + ',0,' + _blue_value + ')'})
	_sctd.appendTo(_row);
	if (_prob < 0.1) {
	    _row.hide().prependTo('#live-table-body').show('fast');
	} else {
	    _row.hide().prependTo('#alerts-table-body').show('fast');
	}
    }

    // remove old entries
    trimTableRows('#alerts-table-body', N_MAX_ALERTS_TABLE_ROWS)
    trimTableRows('#live-table-body', N_MAX_LIVE_TABLE_ROWS)
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

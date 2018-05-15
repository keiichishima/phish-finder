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
    var messages = document.getElementById('data_list');
    var message = document.createElement('li');
    message.appendChild(document.createTextNode(event.data));
    messages.appendChild(message)
}

function wsOnClose(event) {
    console.info('ws closed.');
}

function wsOnError(event) {
    console.info('ws error.');
}

wsInit();

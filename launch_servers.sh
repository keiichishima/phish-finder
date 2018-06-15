#!/bin/sh

# HTTP server port for the web interface
HTTP_PORT=8765

# Websocket server bind address
# The port is fixed to 5678
WS_ADDR=all

# The mirror port interface name
#
MIRROR_IFNAME=enp4s0f0

# syslog threshold
SYSLOG_THRESH=0.95

# Loghost
#
# Assuming that rsyslogd is configured to forward user.* messages to the
# Interop log servers
#
LOGHOST=127.0.0.1

echo "Launching WebSocket server"
tmux list-sessions | grep ws_pf
if [ $? -eq 1 ]; then
	tmux new-session -d -s ws_pf
else
	tmux send-keys -t ws_pf C-c
fi
tmux send -t ws_pf "cd /home/major/keiichi/phish-finder/server; python server.py -b ${WS_ADDR}
"
sleep 1

echo "Launching Sniffer"
tmux list-sessions | grep sniff_pf
if [ $? -eq 1 ]; then
	tmux new-session -d -s sniff_pf
else
	tmux send-keys -t sniff_pf C-c
fi
tmux send -t sniff_pf "cd /home/major/keiichi/phish-finder/server; sudo sh sniffer-interop.sh -i ${MIRROR_IFNAME} -l ${LOGHOST} -t ${SYSLOG_THRESH}
"
sleep 1

echo "Launching Web server"
tmux list-sessions | grep http_pf
if [ $? -eq 1 ]; then
	tmux new-session -d -s http_pf
else
	tmux send-keys -t http_pf C-c
fi
tmux send -t http_pf "cd /home/major/keiichi/phish-finder/html; python -m http.server ${HTTP_PORT}
"

echo "All services are started"

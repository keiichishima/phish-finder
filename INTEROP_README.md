Interop Tokyo 2018
==================

Start services
--------------

Just exec `launch_servers.sh` under the `/home/major/keiichi/phish-finder/` directory.

The above script launches a tmux screen and run necessary server programs in each scresn.


Stop services
-------------

To stop the phish-finder service, kill all the commands running in the following tmux screens.

- `http_pf`: Running the web interface server
- `ws_pf`: Running Websocket relay server
- `sniff_pf`: Running packet sniffer



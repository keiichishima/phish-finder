Interop Tokyo 2018
==================

Start services
--------------

Just exec `launch_servers.sh` under the `/home/major/keiichi/phish-finder/` directory.

The above script launches a tmux screen and run necessary server programs in each scresn.


Restart services
----------------

Services sometimes stop or hang.  To restart all the servers, just exec 'launch_servers.sh' again.  The script will send C-c to all the commands running in the tmux sessions and re-launch services.

If this doesn't work (e.g. the service didn't stop by C-c), stop all the services manually and restart all the services.


Stop services
-------------

To stop the phish-finder service, kill all the commands running in the following tmux screens.

- `http_pf`: Running the web interface server
- `ws_pf`: Running Websocket relay server
- `sniff_pf`: Running packet sniffer



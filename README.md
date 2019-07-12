Phish-Finder
============

This program is a PoC demonstration written for the ShowNet
contribution at Interop Tokyo 2018.

Prerequisites
-------------

Some Python packages must be installed before runnig the demo code.

    chainer            4.0.0
    numpy              1.13.3
    slackweb           1.0.5
    url2vec            https://github.com/keiichishima/url2vec
    websocket-client   0.47.0     
    websocket-server   0.4

You may need different version of the above packages or may need some more additional packages depending on your local environment.

Usage
-----

Run two servers under the `server` directory at the monitoring point. 

Websocket server:

    $ python server.py

Traffic sniffer:

    $ sudo python sniffer.py -urldumpport 9999

The `sinffer.py` program monitors the UDP port specified as `urldumpport` option switch.  The program expects that some kind of external program is going to send url information to taht port.  The format is as below.

    SRC_IP DST_IP URL

`SRC_IP` and `DST_IP` are the IP addresses of the HTTP communicaiton, and `URL` is the URL string.  You may be interested in the project [urlextractor](https://github.com/keiichishima/urlextractor) for URL capturing. `urlextractor` monitors a network interface and output source and destination addresses and URL string to standard output.  The easiest way to input the data is to use the netcat (`nc`) command.  For example, you can run the extractor as below.

    $ urlextractor -i eth0 | nc -u YOUR_SNIFFER_ADDRESS 9999

The URL is evaluated by the pre-trained neural network model.  The results are sent to the `server.py` program using websocket.

The monitoring and evaluation process can be shown using the html file located at the `html/index.html` directory.  So far, the `server.py` program listens to only `127.0.0.1:5678` address, the web client must be on the same host.  If you need to access the server over the Internet, please update the `server.py` program to listen another open address.


Docker
------

There is a project to package this project as a docker component.  Please check [docker-phish-finder](https://github.com/keiichishima/docker-phish-finder) if you are interested in.

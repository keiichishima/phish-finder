Phish-Finder
============

This program is a PoC demonstration written for the ShowNet
contribution at Interop Tokyo 2018.

Prerequisites
-------------

Some Python packages must be installed before runnig the demo code.

    chainer            4.0.0
    numpy              1.13.3
    scapy-http         1.8        
    scapy-python3      0.23
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

    $ sudo python sniffer.py -i en0

The `sinffer.py` program monitors the network interface and extract URL string from the packet.  Then these URLs are evaluated by the pre-trained neural network model.  The results are sent to the `server.py` program using websocket.

The monitoring and evaluation process can be shown using the html file located at the `html/index.html` directory.  So far, the `server.py` program listens to only `127.0.0.1:5678` address, the web client must be on the same host.  If you need to access the server over the Internet, please update the `server.py` program to listen another open address.

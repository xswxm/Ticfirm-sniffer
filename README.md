Ticfirm-sniffer
A tool for sniffing ticwatch firmwares.

### Demo
<img src="https://github.com/xswxm/Ticfirm-sniffer/blob/master/demo.png?raw=true" 
alt="Demo" width="655" height="415" border="10" />

### Modules
requests

### Setting Up
Install additional modules
```sh
sudo apt-get install python-pip
sudo pip install requests
```

### How to Use
```sh
# Check help documents
sudo python ticfirm-sniffer.py -h
# Check ticwatch's beta version numbers from 0 to 1000 with 200 threads.
sudo python ticfirm-sniffer.py -a ticwatch -c beta -v 0 1000 -t 200
```

### Windows Users with CMD
```sh
# Install python-requests
pip install requests
# Execute the script
py ticfirm-sniffer.py -a ticwatch -c beta -v 0 1000 -t 200
```

License
----
MIT

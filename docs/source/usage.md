

```bash 
    
    Documentation for gocart can be found here: http://gocart.readthedocs.org
    
    Usage:
        gocart init
        gocart [-p] echo <daysAgo> [-s <pathToSettingsFile>]
        gocart [-p] (listen|quit|restart|status) [-s <pathToSettingsFile>]
    
    
    Options:
        init                                   setup the gocart settings file for the first time
        echo <daysAgo>                         relisten to alerts from N <daysAgo> until now and then exit
        listen                                 reconnect to kafka stream and listen from where you left off (or from now on if connectiong for the first time).
    
        -h, --help                             show this help message
        -v, --version                          show version
        -p, --plugins                          execute plugins everytime an alert is read
        -s, --settings <pathToSettingsFile>    the settings file
        -t, --test                             test, only collect 1 map
    

```

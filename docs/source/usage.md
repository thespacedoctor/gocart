

```bash 
    
    Documentation for gocart can be found here: http://gocart.readthedocs.org
    
    Usage:
        gocart init
        gocart echo <daysAgo> [-s <pathToSettingsFile>]
        gocart listen [-s <pathToSettingsFile>]
    
    
    Options:
        init                                   setup the gocart settings file for the first time
        echo <daysAgo>                         relisten to alerts from N <daysAgo> until now and then exit
        listen                                 reconnect to kafka stream and listen from where you left off (or from now on if connectiong for the first time).
    
        -h, --help                             show this help message
        -v, --version                          show version
        -s, --settings <pathToSettingsFile>    the settings file
        -t, --test                             test, only collect 1 map
    

```

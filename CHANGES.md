
## Release Notes

**v0.2.1 - April 26, 2023**  

- **FIXED**: listen command was tripping up on mock-events

**v0.2.0 - April 26, 2023**  

- **FEATURE**: filtering of alerts is now possible via options in the settings file (see docs)  
- **ENHANCEMENT**: option added to write the original json alert to file  
- **ENHANCEMENT**: gocart *should* be robust enough to handle burst events (tested against a hand crafted burst alert packet as none exist in the LVK Public Alert Guide yet).  

**v0.1.10 - April 21, 2023**  

- **REFACTOR**: splitting mockevents from superevents   

**v0.1.9 - April 19, 2023**  

- **REFACTOR**: sun and moon footprints replace terminator  

**v0.1.8 - April 6, 2023**  

- **FIXED**: echo command now parses message to the end of the partition queue  
- **FIXED**: listen command remembers where it left off  
- **FIXED**: sun & moon coordinates ... they were not geocentric!  

**v0.1.7 - April 4, 2023**  

- **FIXED**: unit test fix  

**v0.1.6 - April 4, 2023**  
 
- **ENHANCEMENT**: added localisation type to aitoff maps  
- **FIXED**: first time listen command no longer starteds from time zero but listens from first connection  
- **FIXED**: doc builds  

**v0.1.5 - April 4, 2023**  

- **FEATURE**: listen command added  
- **FEATURE**: echo command added  
- **FEATURE**: maps converted to ascii format  
- **FEATURE**: maps rendered as aitoff plots  
- **FEATURE**: meta.yaml file written with alert, FITS header and extra useful content  

**v0.1.4 - March 16, 2023**  

- fixing docsting test  


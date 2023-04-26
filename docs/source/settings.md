# Settings

There are many options to configure to your liking within the settings file, and all settings are documented within the comments in the settings file. For example here  are the LVK stream settings:

```yaml
lvk:
    # DOWNLOAD MOCK EVENT ALERTS? USEFUL AS A HEARTBEAT MONITOR
    parse_mock_events: True
    # DOWNLOAD PRODUCTION EVENT ALERTS?
    parse_real_events: False
    # LOCATION TO DOWNLOAD EVENT ALERT AND MAPS TO
    download_dir: ~/lvk_events
    # CONVERT MAPS TO AITOFF PLOTS?
    aitoff:
        convert: True
        day_night: False
        sun_moon: False
        galactic_plane: True
    # CONVERT MAP TO ASCII FILE - ONE ROW PER HEALPIX PIXEL
    ascii_map:
        convert: True
        # THE SIZE OF HEALPIX PIXELS TO RESOLVE SKY TO. NSIDE = 64 IS ~0.84 deg2 PER PIXEL.
        nside: 64
    # WRITE ORIGINAL JSON ALERTS TO FILE?
    json: False

    # UP FRONT FILTERING OF ALERTS. ONLY IF AN ALERT PASSES 1 OR MORE OF THESE FILTERS WILL THE ALERT (AND ASSOCIATED ASSETS) GET WRITTEN TO FILE
    # AN ALERT MUST PASS ALL INDIVIDUAL CRITERIA WITHIN A FILTER TO PASS
    filters:
        - name: general
          alert_types: [initial, update, retraction]
          ns_lower: 0.9
          far_upper: 1.6e-08
          dist_upper: 500
          area90_upper: 2000
        - name: high significance
          alert_types: [initial, update, retraction]
          ns_lower: 0.99
          far_upper: 1.6e-10
          dist_upper: 250
          hasns_lower: 0.9
          hasremnant_lower: 0.5
```

## Alert Filtering

Within the settings file, you have the option to write 'filters'. An alert coming from the alert stream must pass one or more of the filters before its metadata and maps are written to file. Each filter must be given a descriptive name. Within the LVK module the filtering criteria available are as follows:

- `alert_types`: the alert type must be found within this list. Alerts types are *early_warning, preliminary, initial, update* and *retraction*.
- `ns_lower`: the lower limit of the `NS`+`BHNS` found in the event classification.
- `far_upper`: an upper limit for the False Alarm Rate
- `dist_upper`: an upper limit for `DISTMEAN` found in the alert map FITS header (Mpc).
- `area90_upper`: an upper limit to the sky-area containing the 90% credibility region of the event (square degrees).
- `hasns_lower`: a lower limit for the `HasNS` property.
- `hasremnant_lower`: a lower limit for the `HasRemnant` property.

When running gocart in listen or echo mode, the status of the alert's filter pass or fail state will be reported.

[![](https://live.staticflickr.com/65535/52848491113_7dac07cd30_z.png)](https://live.staticflickr.com/65535/52848491113_7dac07cd30_o.png)




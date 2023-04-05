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
```



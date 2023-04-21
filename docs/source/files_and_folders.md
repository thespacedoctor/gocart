## Event and Alert Directories and Files Explained

The location of where event-alert maps are written to file is set via the `download_dir` setting in the settings file. Under this top-level directory, one directory is created per LVK superevent; the name of the directory is the name of the event. Under each event directory, there is one directory for each alert sent for that event. [Alerts come in one of 5 types](https://emfollow.docs.ligo.org/userguide/analysis/index.html#alert-timeline):

- Early Warning
- Preliminary 
- Initial
- Update
- Retraction

The alert folders are named `<alertTimeStamp>_<alertType>`, where the `alertTimeStamp` is the time the alert was issued (not the time of the actual event). 

[![](https://live.staticflickr.com/65535/52792703968_c3bb03ea91_b.jpg)](https://live.staticflickr.com/65535/52792703968_c3bb03ea91_b.jpg)

The alert folder host various files:

1. The multi-order healpix skymap issued with the alert (e.g. `bayestar.multiorder.fits`)
2. `meta.yaml` a metadata file containing the contents of the actual alert, combined with info data from the map FITS header and some extra value-added content such as map sky-areas etc.
3. `skymap.csv` is an ascii representation of a single order healpix skymap, with one row per pixel and giving sky-coordinates, probability and distance for each pixel.
4. `skymap.png` is a aitoff rendering of the skymap, galactic plane, sun and moon position and some extra information useful for planning observations.

[![](https://live.staticflickr.com/65535/52834508061_1862682dba_b.jpg)](https://live.staticflickr.com/65535/52834508061_1862682dba_b.jpg)


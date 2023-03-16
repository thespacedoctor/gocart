# Initialisation 

Before using gocart you need to use the `init` command to generate a user settings file. Running the following creates a [yaml](https://learnxinyminutes.com/docs/yaml/) settings file in your home folder under `~/.config/gocart/gocart.yaml`:

```bash
gocart init
```

The file is initially populated with gocart's default settings which can be adjusted to your preference.

If at any point the user settings file becomes corrupted or you just want to start afresh, simply trash the `gocart.yaml` file and rerun `gocart init`.

<!-- xsphx-modify-settings-file -->

<!-- xsphx-basic-python-setup-via-fundamentals -->

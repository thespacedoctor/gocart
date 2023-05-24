# Listening to and Echoing an Alert Stream

Once your credentials have been added to the `gocart.yaml` file, you are ready to begin listening to a GCN Kafka stream (LVK only so far). To do so, activate the gocart conda environment and run the command:

```bash
gocart listen
```

That's it. The listener will run in daemon mode (running as a background task) and download new events and alerts as they are added to the Kafka stream in real-time. If you are parsing the test/mock events (see the `parse_mock_events` setting), you will collect a set of event alerts every ~1hr.

You can check on the status of the listener with `gocart status`. This will tell you if the listener is running or not.

To stop the listener run `gocart quit`, or to restart run `gocart restart`.

If you stop the listener or it falls over for some reason, once you reconnect it will download any event-alerts you missed in the interim. 

To relisten the event alerts from the last few days you can run the `echo` command. To request the last 3 days of alerts run the command:

```bash
gocart echo 3
```

Note, alerts only remain on the GCN-Kafka stream for a finite period of time and you may not be able to relisten to alerts older than a week or so.

# Listening to and Echoing an Alert Stream

Once your credentials have been added to the `gocart.yaml` file, you are ready to begin listening to a GCN Kafka stream (LVK only so far). To do so, activate the gocart conda environment and run the command:

```bash
gocart listen
```

That's it. The listener will remain open and download new events and alerts as they are added to the Kafka stream in real-time. If you are parsing the test/mock events (see the `parse_mock_events` setting), you will collect a set of event alerts every ~1hr.

If you stop the listener or it falls over for some reason, once you reconnect it will download any event-alerts you missed in the interim. 

To quit the listener use the keystroke `ctrl \`.

To relisten the event alerts from the last few days you can run the `echo` command. To request the last 3 days of alerts run the command:

```bash
gocart echo 3
```

Note, alerts only remain on the GCN-Kafka stream for a finite period of time and you may not be able to relisten to alerts older than a week or so.

# APRS Track Direct

**APRS Track Direct** is a suite of tools designed to facilitate the creation and operation of an APRS-based website. It supports data from sources like APRS-IS, CWOP-IS, OGN, and other systems adhering to the APRS specification.

The suite includes:
- **APRS Data Collector**: Gathers data from APRS-compatible sources.
- **WebSocket Server**: Facilitates real-time communication.
- **JavaScript Library**: A versatile library for client-side operations (includes WebSocket functionality and more).
- **Example Website**: A fully functional template for quick deployment or further customization.

---

## What is APRS?

The **Automatic Packet Reporting System (APRS)** is a digital communication protocol used by amateur radio operators worldwide to share real-time tactical information. 

Typical data shared via APRS includes:
- GPS coordinates, altitude, speed, and heading.
- Messages, alerts, and bulletins.
- Weather reports and telemetry data.

---

## Getting Started

Follow these steps to set up a local development environment or deploy a public APRS website. 

> **Note:** These instructions serve as general guidelines. Adjustments may be necessary based on your specific requirements. Review the code for deeper insights into its functionality.

### Prerequisites
Ensure you have **Docker** and the **Docker Compose plugin** installed. Follow the [official Docker installation guide](https://docs.docker.com/engine/install/).

### Configuration
Edit the following configuration files to suit your needs:
- `config/trackdirect.ini`
- `config/aprsc.conf`
- `config/postgresql.conf`

### Running the Application
```
docker compose up
```

If you want to run the container in daemon mode (background) add `-d` to the command and use `docker compose logs -f` to watch the output on demand. To stop the containers use `docker compose down`.

If everything is set up correctly, you should be able to open your browser and navigate to `http://127.0.0.1`.

---

## Development Notes

### Track Direct JavaScript Library

The **Track Direct JavaScript library** powers all map-related features, including:
- Rendering maps using **Google Maps API** or **Leaflet**.
- Communicating with the backend WebSocket server.
- Supporting other interactive functionalities.

If you make changes to the library (located in the `jslib` directory), rebuild it to apply updates to the `htdocs` directory by running:

```
pip3 install jsmin
~/trackdirect/jslib/build.sh
```

### Adapt the website (htdocs)
For setting up a copy on your local machine for development and testing purposes you do not need to do anything, but for any other purposes I really recommend you to adapt the UI.

First thing to do is probably to select which map provider to use, look for stuff related to map provider in "index.php". Note that the map providers used in the demo website may not be suitable if you plan to have a public website (read their terms of use).

### Increase database performance
To enhance database performance, particularly when processing large data sets, consider adjusting the PostgreSQL configuration. Prioritize speed but weigh the risks of reduced data durability.

Recommended settings in config/postgresql.conf:
```
shared_buffers = 2048MB              # I recommend 25% of total RAM
synchronous_commit=off               # Avoid writing to disk for every commit
commit_delay=`100000`                # Will result in a 0.1s commit delay
```

However, the database initialized via Docker is already preconfigured with these settings.

---

## Contribution
Contributions are welcome. Create a fork and make a pull request. Thank you!

## Disclaimer
These software tools are provided "as is" and "with all it's faults". We do not make any commitments or guarantees of any kind regarding security, suitability, errors or other harmful components of this source code. You are solely responsible for ensuring that data collected and published using these tools complies with all data protection regulations. You are also solely responsible for the protection of your equipment and the backup of your data, and we will not be liable for any damages that you may suffer in connection with the use, modification or distribution of these software tools.

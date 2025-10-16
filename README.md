# Bluetooth Scanning Tool with GPS Integration

![Sample Output](docs/images/sample_output.png)

## Overview
This Python-based tool runs on a Raspberry Pi and continuously scans for nearby Bluetooth devices. It can also capture GPS coordinates using a u-blox NEO-6M GPS module and logs the detected devices with their location in MGRS format. Additionally, the tool can send the logged data to a Telegram chat.

## Features
- Bluetooth Classic and BLE scanning
- GPS integration with MGRS format logging
- CLI for easy control and interaction
- Periodic and manual Telegram reporting

!!!! be advised, GPS logging is implemented but not tested. !!!!

## Getting Started

### Hardware Setup
Connect the u-blox NEO-6M GPS module to the Raspberry Pi as shown below:

![Hardware Setup](docs/images/hardware_setup.png)

### Installation
Follow the [installation guide](docs/installation.md) to set up the necessary software and dependencies on your Raspberry Pi.

### Usage
Learn how to use the tool with various commands in the [usage guide](docs/usage.md).

### Troubleshooting
Having issues? Check out the [troubleshooting guide](docs/troubleshooting.md) for common problems and solutions.

## License
This project is licensed under the MIT License.

## Contact
For questions or issues, please  contact me :)

## Known issues
currently the telegram API only allows 50 MAC-Adresses, and currently there is no function to renew the logs.log file.
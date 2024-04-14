Here's the updated README with the new device discovery section:

# Govee Screen Sync

Govee Screen Sync is a Python project that synchronizes Govee LED lights with your computer screen, creating an immersive lighting experience. The lights will change colors based on the content displayed on your screen.

## Prerequisites

Before getting started, ensure that you have the following:

- Python 3.7 or higher installed on your system
- Poetry package manager installed (see installation instructions [here](https://python-poetry.org/docs/#installation))
- Govee LED lights compatible with the Govee API

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/govee-screen-sync.git
cd govee-screen-sync
```

2. Install the required dependencies using Poetry:

```bash
poetry install
```

## Device Discovery

To discover your Govee devices and identify their IP addresses, you can run the device discovery script:

1. Activate the Poetry virtual environment:

```bash
poetry shell
```

2. Run the device discovery script:

```bash
python discover_devices.py
```

The script will attempt to discover your Govee devices automatically. If successful, it will light up each device with a different color of the rainbow and display the corresponding IP address in the console output.

Press Enter to power off the devices.

Use the discovered IP addresses to update the `devices.json` file accordingly.

## Configuration

1. Locate the `devices_template.json` file in the project directory.

2. Make a copy of the `devices_template.json` file and rename it to `devices.json`.

3. Open the `devices.json` file in a text editor.

4. Replace the placeholder IP addresses (`192.168.0.xxx` and `192.168.0.yyy`) with the actual IP addresses of your Govee devices.

5. Customize the device names and screen positions according to your setup. The `screen_positions` array should contain the indices of the screen sections you want the device to be mapped to.

6. Save the `devices.json` file.

7. Customize screen positions (optional):

   The `screen_positions` array in the `devices.json` file allows you to specify which parts of the screen should be mapped to each device. You can customize the values to select specific areas of the screen for each device.

## Usage

1. Activate the Poetry virtual environment:

```bash
poetry shell
```

2. Run the script:

```bash
python main.py
```

The script will start capturing your screen, processing the colors, and sending commands to your Govee devices to synchronize the lighting with your screen content.

## Troubleshooting

- If the script fails to discover your devices automatically, make sure your devices are powered on and connected to the same network as your computer.

- If the colors don't match your expectations, you can adjust the color processing parameters in the `capture_screen_and_process_colors()` function in the `screen_capture.py` file.

- If the script displays an error message about the `devices.json` file not being found, make sure you have created the file by following the configuration steps above.

## Contributing

Feel free to submit issues and pull requests to improve the project. Contributions are always welcome!

## License

This project is licensed under the [MIT License](LICENSE).
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

## Mapping Devices to Screen Sections
Using the `devices.json` file, you can map each Govee device to specific sections of your computer screen. This mapping allows you to sonchronize the lighting effects with different parts of the screen content.


### Moniter Grid
```
         0   1   2   3   4   5   6   7   8   9
       -----------------------------------------
    0  | x   x   x   x   x   x   x   x   x   x |
    1  | x   x   x   x   x   x   x   x   x   x |
    2  | x   x   x   x   x   x   x   x   x   x |
    3  | x   x   x   x   x   x   x   x   x   x |
    4  | x   x   x   x   x   x   x   x   x   x |
    5  | x   x   x   x   x   x   x   x   x   x |
    6  | x   x   x   x   x   x   x   x   x   x |
    7  | x   x   x   x   x   x   x   x   x   x |
    8  | x   x   x   x   x   x   x   x   x   x |
    9  | x   x   x   x   x   x   x   x   x   x |
       -----------------------------------------
                    ||||||||||||||
                    ||||||||||||||
                ______________________
```

For example, suppose you have two verticle light devices.
You want to map them to the left and right sides of the screen.

```
- Map the left device (0) to the left side of the screen
- Map the right device (1) to the right side of the screen.


Govee device 0                                                  govee device 1
     ___                                                               ___     
    [ 9 ]                                                             [ 9 ]    
    [ 9 ]                                                             [ 9 ]    
    [ 8 ]                                                             [ 8 ]    
    [ 8 ]                                                             [ 8 ]    
    [ 7 ]                                                             [ 7 ]    
    [ 7 ]            0   1   2   3   4   5   6   7   8   9            [ 7 ]    
    [ 6 ]          -----------------------------------------          [ 6 ]    
    [ 6 ]       0  | 0   0   0   x   x   x   x   1   1   1 |          [ 6 ]    
    [ 5 ]       1  | 0   0   0   x   x   x   x   1   1   1 |          [ 5 ]    
    [ 5 ]       2  | 0   0   0   x   x   x   x   1   1   1 |          [ 5 ]    
    [ 4 ]       3  | 0   0   0   x   x   x   x   1   1   1 |          [ 4 ]    
    [ 4 ]       4  | 0   0   0   x   x   x   x   1   1   1 |          [ 4 ]    
    [ 3 ]       5  | 0   0   0   x   x   x   x   1   1   1 |          [ 3 ]    
    [ 3 ]       6  | 0   0   0   x   x   x   x   1   1   1 |          [ 3 ]    
    [ 2 ]       7  | 0   0   0   x   x   x   x   1   1   1 |          [ 2 ]    
    [ 2 ]       8  | 0   0   0   x   x   x   x   1   1   1 |          [ 2 ]    
    [ 1 ]       9  | 0   0   0   x   x   x   x   1   1   1 |          [ 1 ]    
    [ 1 ]          -----------------------------------------          [ 1 ]    
    [ 0 ]                       ||||||||||||||                        [ 0 ]    
    [ 0 ]                       ||||||||||||||                        [ 0 ]           _
(   _____   )               ______________________                (   _____   )
```

**The order of the device locations is likely 0-9 from closest to power source to the tip of the device, but I'm just guessing this.**

We will use a "mask" of the screen to map the devices. The mask will be a 2D array that represents the screen. The value (0-9) in a location indicates that the device should be mapped to that position, while -1 indicates that it should not be used by the device.

Device 0 Mapping
```
screen_map = [
    [9, 9, 9, -1, -1, -1, -1, -1, -1, -1],
    [8, 8, 8, -1, -1, -1, -1, -1, -1, -1],
    [7, 7, 7, -1, -1, -1, -1, -1, -1, -1],
    [6, 6, 6, -1, -1, -1, -1, -1, -1, -1],
    [5, 5, 5, -1, -1, -1, -1, -1, -1, -1],
    [4, 4, 4, -1, -1, -1, -1, -1, -1, -1],
    [3, 3, 3, -1, -1, -1, -1, -1, -1, -1],
    [2, 2, 2, -1, -1, -1, -1, -1, -1, -1],
    [1, 1, 1, -1, -1, -1, -1, -1, -1, -1],
    [0, 0, 0, -1, -1, -1, -1, -1, -1, -1],
]
```


We can formalize this within our JSON object. You can provide either the screen positions or the screen mask. The screen mask is a 2D array that represents the screen. The value of 1 indicates that the device should be mapped to that position, while 0 indicates that it should not. 
```json
[
    {
        "ip": "192.168.0.xxx",
        "name": "device_0",
        "screen_map": [
            [9, 9, 9, -1, -1, -1, -1, -1, -1, -1],
            [8, 8, 8, -1, -1, -1, -1, -1, -1, -1],
            [7, 7, 7, -1, -1, -1, -1, -1, -1, -1],
            [6, 6, 6, -1, -1, -1, -1, -1, -1, -1],
            [5, 5, 5, -1, -1, -1, -1, -1, -1, -1],
            [4, 4, 4, -1, -1, -1, -1, -1, -1, -1],
            [3, 3, 3, -1, -1, -1, -1, -1, -1, -1],
            [2, 2, 2, -1, -1, -1, -1, -1, -1, -1],
            [1, 1, 1, -1, -1, -1, -1, -1, -1, -1],
            [0, 0, 0, -1, -1, -1, -1, -1, -1, -1]
        ]
    }
]
```


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
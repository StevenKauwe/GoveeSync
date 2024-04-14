import json
import signal

from src.govee_screen_sync.game_sync import game_loop
from src.govee_screen_sync.light_device import GoveeLightDevice, get_device_location_indices


def get_my_devices() -> list[GoveeLightDevice]:
    try:
        with open("devices.json", "r") as file:
            devices_data = json.load(file)
    except FileNotFoundError:
        print("devices.json not found.")
        print(
            "Please make a copy of devices_template.json, rename it to devices.json, and configure your devices."
        )
        return []

    devices = []
    for device_data in devices_data:
        ip = device_data["ip"]
        name = device_data["name"]
        screen_positions = get_device_location_indices(device_data["screen_positions"])
        device = GoveeLightDevice(ip, name, screen_positions)
        devices.append(device)

    print(f"Devices: {[device.name for device in devices]}")
    return devices


def run():
    devices = get_my_devices()

    def power_off_devices_and_exit():
        for device in devices:
            device.power_off()
        exit()

    print("Starting Govee Light Controller...")
    signal.signal(signal.SIGTERM, lambda signum, frame: power_off_devices_and_exit())
    signal.signal(signal.SIGINT, lambda signum, frame: power_off_devices_and_exit())
    game_loop(devices=devices)


if __name__ == "__main__":
    run()

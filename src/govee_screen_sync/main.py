import signal

from govee_screen_sync.game_sync import game_loop
from govee_screen_sync.light_device import GoveeLightDevice, get_device_location_indices
from govee_screen_sync.utils import color_device_by_ip, discover_devices


def get_my_devices() -> list[GoveeLightDevice] | None:
    """Returns a list of GoveeLightDevice objects that represent the devices in the room.
    This function should be implemented by the user.

    If you don't know the IP addresses of your devices, return an empty list
    """
    left_column_device = GoveeLightDevice(
        "192.168.0.248", "Govee Light Right", get_device_location_indices([7, 8, 9])
    )
    right_column_device = GoveeLightDevice(
        "192.168.0.108",
        "Govee Light Left",
        get_device_location_indices([0, 1, 2]),
    )

    my_devices = [left_column_device, right_column_device]
    print(f"Devices: {[my_devices.name for my_devices in my_devices]}")

    return my_devices
    # return []


def run():
    devices = get_my_devices()
    if not devices:
        color_device_by_ip()
        return
    discover_devices(expected_devices=devices)

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

import base64
import socket
import time
from enum import Enum

from PIL import ImageGrab
from pydantic import BaseModel, Field, validator

# Configuration
# DEVICE_IP: list[str] = ["10.1.1.54", "10.1.1.43"]  # Example IPs for two devices
DEVICE_IP: list[str] = ["192.168.0.108", "192.168.0.248"]
UDP_PORT: int = 4003  # Default UDP port
NUM_COLORS: int = 20  # Number of color samples per device


class PowerState(Enum):
    OFF = 0
    ON = 1


class Color(BaseModel):
    r: int = Field(..., ge=0, le=255)
    g: int = Field(..., ge=0, le=255)
    b: int = Field(..., ge=0, le=255)


class Command(BaseModel):
    msg: dict


class PowerCommand(Command):
    msg: dict = {"cmd": "turn", "data": {"value": PowerState.OFF.value}}

    @validator("msg", pre=True)
    def set_power_state(cls, value, values):
        value["data"]["value"] = values.get("power_state", PowerState.OFF).value
        return value


class BrightnessCommand(Command):
    msg: dict = {"cmd": "brightness", "data": {"value": 100}}

    @validator("msg", pre=True)
    def set_brightness(cls, value, values):
        value["data"]["value"] = values.get("brightness", 100)
        return value


class ColorCommand(Command):
    msg: dict = {
        "cmd": "colorwc",
        "data": {"color": {"r": 255, "g": 255, "b": 255}, "colorTemInKelvin": 0},
    }

    @validator("msg", pre=True)
    def set_color(cls, value, values):
        color = values.get("color", Color(r=255, g=255, b=255))
        value["data"]["color"] = color.dict()
        return value


class SegmentCommand(Command):
    msg: dict = {"cmd": "razer", "data": {"pt": "uwABsQEK"}}

    @validator("msg", pre=True)
    def set_segment(cls, value, values):
        value["data"]["pt"] = values.get("segment", "uwABsQEK")
        return value


class FormatAndSendColorsCommand(Command):
    msg: dict = {"cmd": "razer", "data": {"pt": ""}}

    @validator("msg", pre=True)
    def set_colors(cls, value, values):
        colors = values.get("colors", [])
        byteArray: list[int] = [187, 0, 32, 176, 1, NUM_COLORS] + [
            c for color in colors for c in color
        ]
        checksum: int = sum(byteArray) % 256
        byteArray.append(checksum)
        encoded_data: str = base64.b64encode(bytes(byteArray)).decode()
        value["data"]["pt"] = encoded_data
        return value


def send_command(udp_ip: str, command: Command) -> None:
    """Send command data to a specific IP using UDP."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.sendto(command.json().encode(), (udp_ip, UDP_PORT))
    print(f"Command sent to {udp_ip}")


def capture_screen_and_process_colors(
    num_devices: int,
) -> list[list[tuple[int, int, int]]]:
    """Capture screen, compute average colors for specified points, and return them."""
    screen_image = ImageGrab.grab()  # Capture the entire screen
    screen_width, screen_height = screen_image.size

    # Define sample positions on the screen
    vertical_positions: list[int] = [
        int(screen_height * i / NUM_COLORS) for i in range(NUM_COLORS)
    ]

    # Calculate horizontal sections for each device
    horizontal_sections: list[int] = [
        int(screen_width * (i + 1) / (num_devices + 1)) for i in range(num_devices)
    ]

    device_colors: list[list[tuple[int, int, int]]] = []
    for x in horizontal_sections:
        section_colors: list[tuple[int, int, int]] = [
            screen_image.getpixel((x, y)) for y in vertical_positions
        ]
        device_colors.append(section_colors)

    return device_colors


def game_loop() -> None:
    """Main game loop to handle screen capture, color processing, and device control."""
    try:
        for ip in DEVICE_IP:
            send_command(
                ip, PowerCommand(power_state=PowerState.ON)
            )  # Turn on the devices
            send_command(
                ip, BrightnessCommand(brightness=100)
            )  # Set brightness to 100%
            send_command(ip, SegmentCommand(segment="uwABsQEK"))  # Initialize segments
        time.sleep(2)

        while True:
            color_data: list[list[tuple[int, int, int]]] = (
                capture_screen_and_process_colors(len(DEVICE_IP))
            )
            for ip, colors in zip(DEVICE_IP, color_data):
                send_command(ip, FormatAndSendColorsCommand(colors=colors))
            time.sleep(1)  # Update interval

    except KeyboardInterrupt:
        print("Operation stopped by user.")
    finally:
        for ip in DEVICE_IP:
            send_command(
                ip, ColorCommand(color=Color(r=255, g=165, b=0))
            )  # Set light sunset color (orange)
            print("Setting light to orange...")
        time.sleep(1)
        for ip in DEVICE_IP:
            print("Turning off devices...")
            send_command(ip, SegmentCommand(segment="uwABsQAL"))  # Terminate segments
            send_command(
                ip, PowerCommand(power_state=PowerState.OFF)
            )  # Turn off the devices


def main() -> None:
    """Main function to handle the overall operation."""
    print("Press Ctrl+C to quit.")
    game_loop()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        for ip in DEVICE_IP:
            print("Turning off devices...")
            send_command(ip, SegmentCommand(segment="uwABsQAL"))  # Terminate segments
            send_command(
                ip, PowerCommand(power_state=PowerState.OFF)
            )  # Turn off the devices

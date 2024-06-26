import base64
import socket
import time

from govee_screen_sync.config import DEBUG, MAX_LED_COLOR_GRADIENT, UDP_PORT
from govee_screen_sync.models import (
    BrightnessCommand,
    BrightnessData,
    Color,
    ColorCommand,
    ColorData,
    Command,
    Message,
    NetworkedGoveeDevice,
    PowerCommand,
    PowerData,
    PowerState,
    SegmentCommand,
    SegmentData,
)


class GoveeLightDevice:
    def __init__(self, device: NetworkedGoveeDevice):
        self.ip = device.ip
        self.name = device.name
        self.screen_map = device.screen_map

    def _send_command(self, command: Command, sleep_time=0.1):
        message = Message(msg=command).model_dump_json()

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(message.encode(), (self.ip, UDP_PORT))
        if DEBUG:
            print(f"Command sent to {self.ip}: {message}")
        time.sleep(sleep_time)

    def power_on(self):
        power_on_command = PowerCommand(data=PowerData(value=PowerState.ON))
        self._send_command(power_on_command)

    def power_off(self):
        power_off_command = PowerCommand(data=PowerData(value=PowerState.OFF))
        self._send_command(power_off_command)

    def set_color(self, color: Color):
        color_command = ColorCommand(data=ColorData(color=color))
        self._send_command(color_command)

    def set_brightness(self, brightness: int):
        brightness_command = BrightnessCommand(data=BrightnessData(value=brightness))
        self._send_command(brightness_command)

    def initialize_segment(self):
        """Initializes a segment to be set with set_segment_colors."""
        segment_command = SegmentCommand(data=SegmentData(pt="uwABsQEK"))
        self._send_command(segment_command)

    def terminate_segment(self):
        """Returns the color to the state before the segment was initialized."""
        segment_command = SegmentCommand(data=SegmentData(pt="uwABsQAL"))
        self._send_command(segment_command)

    def set_segment_colors(self, list_of_colors: list[Color], gradient=True):
        """Sets the colors of the segment to the given list of colors.
        color list of size (min 2, max 10)

        probably move "intrepolation" and "resolution" to some other place.

        colors ordering goes from bottom to top for a lamp.
        not sure about a strip.
        but probably power source to the end of the strip.
        """

        assert (
            2 <= len(list_of_colors) <= MAX_LED_COLOR_GRADIENT
        ), f"Color list must be between 1 and 10, got {len(list_of_colors)}"

        segment_color_data = self._get_segment_color_data(list_of_colors, gradient)
        segment_command = SegmentCommand(data=segment_color_data)
        self._send_command(segment_command, sleep_time=0)

    def _get_segment_color_data(self, list_of_colors: list[Color], gradient=True) -> SegmentData:
        """Returns the SegmentData object for the given list of colors.

        The segment data is a base64 encoded string that represents the colors to be set.
        I have no idea what the values for the first 4 bytes are.
        I assume the 6th byte is the number of colors.
        """
        gradient_flag = 1 if gradient else 0
        byte_array = [187, 0, 32, 176, gradient_flag, len(list_of_colors)]

        for color in list_of_colors:
            byte_array.extend(color.rgb)

        num2 = 0
        for byte in byte_array:
            num2 ^= byte
        byte_array.append(num2)
        final_send_value = base64.b64encode(bytes(byte_array)).decode()
        return SegmentData(pt=final_send_value)

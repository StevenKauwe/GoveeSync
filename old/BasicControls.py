from controller import LightController
from models import Color, ColorCommand, ColorData, PowerCommand, PowerData, PowerState

DeviceIP = ["192.168.0.108", "192.168.0.248"]


def main():
    controller = LightController(["192.168.0.108", "192.168.0.248"])
    # Example usage of the PowerCommand model
    power_on_command = PowerCommand(data=PowerData(value=PowerState.ON))
    controller.send_command(power_on_command)

    # Example usage of the ColorCommand model
    color_command = ColorCommand(data=ColorData(color=Color(r=255, g=124, b=0)))
    controller.send_command(color_command)

    power_on_command = PowerCommand(data=PowerData(value=PowerState.OFF))
    controller.send_command(power_on_command)


if __name__ == "__main__":
    main()

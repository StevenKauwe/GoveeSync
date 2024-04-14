import socket
import struct
import time

from src.govee_screen_sync.light_device import GoveeLightDevice
from src.govee_screen_sync.models import Color, DeviceScanMessage


def discover_devices(
    send_group: str = "239.255.255.250",
    send_port: int = 4001,
    receive_port: int = 4002,
    message: DeviceScanMessage = DeviceScanMessage(),
    timeout: int = 1,
    expected_devices: list[GoveeLightDevice] = None,
):
    # Set up the sending socket with TTL for multicast
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    ttl = struct.pack("b", 1)  # Time-to-live of the multicast message
    send_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    # Set up the receiving socket
    recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    recv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    recv_sock.bind(("", receive_port))

    # Join multicast group
    mreq = struct.pack("4sl", socket.inet_aton(send_group), socket.INADDR_ANY)
    recv_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    # Send the multicast message
    json_message = message.model_dump_json()
    print(f"Sending: {json_message}")
    send_sock.sendto(bytes(json_message, "utf-8"), (send_group, send_port))
    send_sock.close()

    # Listen for responses
    recv_sock.settimeout(timeout)
    device_ips = []
    ti = time.time()
    try:
        while True:
            data, addr = recv_sock.recvfrom(10240)
            print(f"Received response from {addr}: {data} in {time.time() - ti} seconds.")
            device_ips.append(addr[0])

            # Check if all expected devices have responded
            if expected_devices and all(device.ip in device_ips for device in expected_devices):
                print("All expected devices have responded.")
                break
    except socket.timeout:
        print("Listening timeout reached. No more responses.")
    finally:
        recv_sock.close()
    return device_ips


def color_device_by_ip():
    # For each discovered device, create a GoveeLightDevice object
    devices = [
        GoveeLightDevice(ip, f"Govee Light {i}", []) for i, ip in enumerate(discover_devices())
    ]

    rainbow_rgb = {
        "red": (255, 0, 0),
        "orange": (255, 165, 0),
        "yellow": (255, 255, 0),
        "green": (0, 128, 0),
        "blue": (0, 0, 255),
        "indigo": (75, 0, 130),
        "violet": (238, 130, 238),
    }

    # Light up the devices to indicate they have been discovered
    device_count_location = 0
    for i, device in enumerate(devices):
        device.power_on()
        device.set_brightness(100)
        device.initialize_segment()

        color_index = i % len(rainbow_rgb)
        if i % 2 != 0:
            color_index = len(rainbow_rgb) - color_index - 1
        color_name = list(rainbow_rgb.keys())[color_index]
        color_rgb = rainbow_rgb[color_name]

        segment_colors = [Color.from_rgb(color_rgb) for _ in range(10)]
        if i % len(rainbow_rgb) == 0 and i != 0:
            device_count_location += 1

        segment_colors[device_count_location] = Color.from_rgb((5, 5, 5))
        device.set_segment_colors(segment_colors, gradient=False)

        print(
            f"Device at ip {device.ip} as color {color_name} in location {device_count_location}"
        )

    _ = input("Press enter to power off devices...")

    for device in devices:
        device.terminate_segment()
        device.power_off()

    return devices


if __name__ == "__main__":
    color_device_by_ip()

import json
import socket
import struct


def discover_devices(send_group, send_port, receive_port, message, timeout=5):
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
    json_message = json.dumps(message)
    print(f"Sending: {json_message}")
    send_sock.sendto(bytes(json_message, "utf-8"), (send_group, send_port))
    send_sock.close()

    # Listen for responses
    recv_sock.settimeout(timeout)
    devices = []
    try:
        while True:
            data, addr = recv_sock.recvfrom(10240)
            print(f"Received response from {addr}: {data}")
            devices.append(addr[0])
    except socket.timeout:
        print("Listening timeout reached. No more responses.")
    finally:
        recv_sock.close()

    return devices


if __name__ == "__main__":
    send_group = "239.255.255.250"
    send_port = 4001
    receive_port = 4002
    message = {
        "msg": {
            "cmd": "scan",
            "data": {
                "account_topic": "reserve",
            },
        }
    }
    devices = discover_devices(send_group, send_port, receive_port, message)
    print("Discovered devices:", devices)

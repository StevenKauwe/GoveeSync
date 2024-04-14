import socket
from typing import List

from models import Command, Message

UDP_PORT = 4003


# Controller Class
class LightController:
    def __init__(self, ips: List[str]):
        self.ips = ips

    def send_command(self, command: Command):
        message = Message(msg=command).model_dump_json()

        for ip in self.ips:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.sendto(message.encode(), (ip, UDP_PORT))
            print(f"Command sent to {ip}: {message}")


"""
this is the model.
Message(msg=PowerCommand(cmd='turn', data=PowerData(value=<PowerState.ON: 1>)))

after model_dump_json() I get this...
'{"msg":{"cmd":"turn","data":{}}}'

"""

from enum import Enum
from typing import Union

from pydantic import BaseModel, Field


class PowerState(Enum):
    OFF = 0
    ON = 1


class Color(BaseModel):
    r: int = Field(default=145, ge=0, le=255)
    g: int = Field(default=125, ge=0, le=255)
    b: int = Field(default=0, ge=0, le=255)

    @property
    def rgb(self):
        return (self.r, self.g, self.b)

    @classmethod
    def from_rgb(cls, rgb: tuple[int, int, int]):
        return cls(r=rgb[0], g=rgb[1], b=rgb[2])


class PowerData(BaseModel):
    value: PowerState


class BrightnessData(BaseModel):
    value: int


class ColorData(BaseModel):
    color: Color
    colorTemInKelvin: int = 0


class SegmentData(BaseModel):
    pt: str


class DeviceScanData(BaseModel):
    account_topic: str = "reserve"


class Command(BaseModel):
    cmd: str
    data: Union[PowerData, BrightnessData, ColorData, SegmentData]


class Message(BaseModel):
    msg: Command


class PowerCommand(Command):
    cmd: str = "turn"
    data: PowerData


class BrightnessCommand(Command):
    cmd: str = "brightness"
    data: BrightnessData


class ColorCommand(Command):
    cmd: str = "colorwc"
    data: ColorData


class SegmentCommand(Command):
    cmd: str = "razer"
    data: SegmentData


class DeviceScanCommand(Command):
    cmd: str = "scan"
    data: DeviceScanData = DeviceScanData()


class DeviceScanMessage(Message):
    msg: DeviceScanCommand = DeviceScanCommand()

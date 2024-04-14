import time

import numpy as np

from govee_screen_sync.light_device import GoveeLightDevice
from govee_screen_sync.models import Color
from govee_screen_sync.screen_capture import capture_screen_and_process_colors


class FrameCounter:
    def __init__(self):
        self.last_100_fps = []
        self.start_time = time.time()
        self.previous_time = time.time()

    def update_and_print(self):
        elapsed_time = time.time() - self.previous_time
        self.previous_time = time.time()
        time_since_start = time.time() - self.start_time
        fps = 1 / elapsed_time
        self.last_100_fps = self.last_100_fps[-99:]
        self.last_100_fps.append(fps)
        average_fps = sum(self.last_100_fps) / len(self.last_100_fps) if self.last_100_fps else 0
        print(
            f"\rFPS: {fps:.1f} - Average FPS {average_fps:.1f} - Total Time:{time_since_start:.1f}",
            end="",
        )

        return fps

    def reset(self):
        self.frame_count = 0
        self.start_time = time.time()


def game_loop(devices: list[GoveeLightDevice]):
    frame_counter = FrameCounter()
    try:
        for device in devices:
            device.power_on()
            device.set_brightness(100)

        for device in devices:
            device.initialize_segment()

        while True:
            screen_colors = capture_screen_and_process_colors()
            for device in devices:
                color_data = [
                    Color.from_rgb(
                        screen_colors[(np.array(device.screen_map)) == i].mean(axis=0).astype(int)
                    )
                    for i in range(10)
                ]
                device.set_segment_colors(color_data)
            frame_counter.update_and_print()

    except KeyboardInterrupt:
        print("Operation stopped by user.")
    finally:
        for device in devices:
            device.terminate_segment()
            device.set_color(Color())
            device.power_off()

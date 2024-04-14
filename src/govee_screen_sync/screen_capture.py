import numpy as np
from PIL import Image, ImageEnhance, ImageGrab

from govee_screen_sync.config import DEBUG, MAX_LED_COLOR_GRADIENT


def capture_screen_and_process_colors() -> np.ndarray:
    # Capture the entire screen
    screen_image = ImageGrab.grab()
    resize_factor = 10

    # Resize image to a manageable size that maintains the aspect ratio of 10x10 blocks
    resized_image = screen_image.resize(
        (MAX_LED_COLOR_GRADIENT * resize_factor, MAX_LED_COLOR_GRADIENT * resize_factor)
    )

    # Increase the saturation by 1.5 times
    converter = ImageEnhance.Color(resized_image)
    saturated_image = converter.enhance(2.5)

    # Convert image to numpy array for processing
    color_matrix = np.array(saturated_image)

    # Reshape the array to (10, 10, 10, 10, 3) where each 10x10 block's pixels are separately accessible
    color_matrix = color_matrix.reshape(
        (
            MAX_LED_COLOR_GRADIENT,
            resize_factor,
            MAX_LED_COLOR_GRADIENT,
            resize_factor,
            3,
        )
    )

    # I favor red > green > blue for the most "colorful pixel". Let's scale the colors accordingly
    biased_color_matrix = color_matrix.copy()
    biased_color_matrix[..., 0] *= 2
    biased_color_matrix[..., 1] *= 1
    biased_color_matrix[..., 2] *= 1

    # Compute variance across each pixel to find the most "colorful" pixel
    pixel_variances = np.var(biased_color_matrix, axis=4)

    # Transpose the array so that the 10x10 blocks are along the last two axes
    pixel_variances_transposed = pixel_variances.transpose(0, 2, 1, 3)

    # Flatten the last two dimensions
    pixel_variances_flattened = pixel_variances_transposed.reshape(
        MAX_LED_COLOR_GRADIENT, MAX_LED_COLOR_GRADIENT, -1
    )

    # Compute argmax over the flattened dimension
    max_colorful_indices = np.unravel_index(
        pixel_variances_flattened.argmax(axis=2), (resize_factor, resize_factor)
    )

    # For each block, get the most colorful pixel
    most_colorful_pixels = color_matrix[
        np.arange(MAX_LED_COLOR_GRADIENT)[:, None],
        max_colorful_indices[0],
        np.arange(MAX_LED_COLOR_GRADIENT),
        max_colorful_indices[1],
    ]

    most_colorful_pixels = most_colorful_pixels.reshape(
        MAX_LED_COLOR_GRADIENT, MAX_LED_COLOR_GRADIENT, 3
    )

    if DEBUG:
        saturated_image.save("debug_saturated_image.png")
        most_colorful_pixels_image = Image.fromarray(most_colorful_pixels.astype(np.uint8), "RGB")
        most_colorful_pixels_image.save("debug_preview.png")
        # raise an exception to stop the program and show the image
        raise Exception("Debug mode enabled. Stopping program to show image.")

    return most_colorful_pixels

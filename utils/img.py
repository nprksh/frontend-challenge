from PIL import Image, ImageDraw, ImageFont
import numpy as np
from datetime import datetime
import random

font_size = 200

image_size = 1000

corner_square_size = 10
crosshair_length = 50
crosshair_thickness = 6

shape_size = 25


def get_random_position(image_size, shape_size):
    """
    Generates random coordinates for placing a shape within the image boundaries.

    Parameters:
    - image_size: The size of the image (assumes square image).
    - shape_size: The size of the shape (width/height for rectangle, diameter for circle).

    Returns:
    - x_position, y_position: The top-left coordinates for the shape.
    """
    x_position = np.random.randint(0, image_size - shape_size)
    y_position = np.random.randint(0, image_size - shape_size)
    return x_position, y_position


def draw_rectangle(image, draw, color, x_position, y_position, shape_size):
    """
    Draws a rectangle on the image at a specified position.

    Parameters:
    - image: The PIL.Image object.
        The image on which the rectangle will be drawn.
    - draw: The PIL.ImageDraw.Draw object.
        Used to draw on the image.
    - color: The fill color for the rectangle.
        The color in which the rectangle will be drawn.
    - x_position, y_position: The top-left coordinates for the rectangle.
    - shape_size: The size of the rectangle (width and height).

    Returns:
    - image: The updated image with the rectangle drawn.
    """
    # Draw the rectangle
    draw.rectangle(
        [x_position, y_position, x_position + shape_size, y_position + shape_size],
        fill=color,
    )
    return image


def draw_circle(image, draw, color, x_position, y_position, shape_size):
    """
    Draws a circle on the image at a specified position.

    Parameters:
    - image: The PIL.Image object.
        The image on which the circle will be drawn.
    - draw: The PIL.ImageDraw.Draw object.
        Used to draw on the image.
    - color: The fill color for the circle.
        The color in which the circle will be drawn.
    - x_position, y_position: The top-left coordinates for the bounding box of the circle.
    - shape_size: The diameter of the circle.

    Returns:
    - image: The updated image with the circle drawn.
    """
    # Draw the circle
    draw.ellipse(
        [x_position, y_position, x_position + shape_size, y_position + shape_size],
        fill=color,
    )
    return image


def generate_mock_image():
    # Create a blank white canvas
    image = Image.new("RGB", (image_size, image_size), "white")

    draw = ImageDraw.Draw(image)

    color_choices = ["red", "blue", "green", "black"]
    shape_choices = ["rectangle", "circle"]
    num_shapes = random.choice([1, 2, 3])

    print(f"Num Shape: {num_shapes}")
    for i in range(num_shapes):
        x_position, y_position = get_random_position(image_size, shape_size)
        color = random.choice(color_choices)
        shape = random.choice(shape_choices)

        if shape == "rectangle":
            image = draw_rectangle(
                image, draw, color, x_position, y_position, shape_size
            )
        elif shape == "circle":
            image = draw_circle(image, draw, color, x_position, y_position, shape_size)

    # Draw boxes at corners
    draw.rectangle(
        [0, 0, corner_square_size, corner_square_size], fill="black"
    )  # Top-left
    draw.rectangle(
        [image_size - corner_square_size, 0, image_size, corner_square_size],
        fill="black",
    )  # Top-right
    draw.rectangle(
        [0, image_size - corner_square_size, corner_square_size, image_size],
        fill="black",
    )  # Bottom-left
    draw.rectangle(
        [
            image_size - corner_square_size,
            image_size - corner_square_size,
            image_size,
            image_size,
        ],
        fill="black",
    )  # Bottom-right

    # Draw a red crosshair at the center with increased thickness
    center_x, center_y = image_size // 2, image_size // 2
    draw.line(
        [
            (center_x - crosshair_length, center_y),
            (center_x + crosshair_length, center_y),
        ],
        fill="red",
        width=crosshair_thickness,
    )
    draw.line(
        [
            (center_x, center_y - crosshair_length),
            (center_x, center_y + crosshair_length),
        ],
        fill="red",
        width=crosshair_thickness,
    )

    # Add the UTC date and time at the top center with a font size of 300
    utc_now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    try:
        # Attempt to load a default PIL font
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        # Fallback if font is unavailable
        font = ImageFont.load_default()

    text_width, text_height = draw.textbbox((0, 0), utc_now, font=font)[2:]
    text_position = ((image_size - text_width) // 2, 20)  # Top-center position
    draw.text(text_position, utc_now, fill="black", font=font)

    return image

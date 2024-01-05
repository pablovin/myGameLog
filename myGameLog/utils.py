from PIL import Image, ImageDraw


def remove_last_empty_row(csv_directory):
    with open(csv_directory, "r+") as f:
        f.seek(0, 2)
        size = f.tell()
        f.truncate(size - 1)


def merge_logo_with_qr_code(qr_code_path, logo_path, output_path):
    # Load images
    qr_code = Image.open(qr_code_path)
    logo = Image.open(logo_path)

    # Create a new image with a white background
    new_width = 288
    new_height = logo.height + 10 + qr_code.height
    new_image = Image.new("RGB", (new_width, new_height), "white")

    # Calculate the position to center the logo
    logo_position = ((new_width - logo.width) // 2, 0)

    # Paste logo at the centered position
    new_image.paste(logo, logo_position)

    # Draw a white space below the logo
    draw = ImageDraw.Draw(new_image)
    draw.rectangle([(0, logo.height), (new_width, logo.height + 10)], fill="white")

    # Calculate the position to center the QR code
    qr_code_position = ((new_width - qr_code.width) // 2, logo.height + 10)

    # Paste qr_code at the centered position
    new_image.paste(qr_code, qr_code_position)

    # Add a black border
    border_size = 5
    bordered_image = Image.new(
        "RGB", (new_width + 2 * border_size, new_height + 2 * border_size), "black"
    )
    bordered_image.paste(new_image, (border_size, border_size))

    # Save the final image
    bordered_image.save(output_path)

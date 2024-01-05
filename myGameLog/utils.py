from PIL import Image, ImageDraw, ImageFont
import PIL


def remove_last_empty_row(csv_directory):
    with open(csv_directory, "r+") as f:
        f.seek(0, 2)
        size = f.tell()
        f.truncate(size - 1)


def add_white_background(image):
    # Create a new image with a white background
    new_image = Image.new("RGB", image.size, "white")
    new_image.paste(image, (0, 0), image)
    return new_image


def merge_logo_with_qr_code(qr_code_path, logo_path, output_path):
    logo = Image.open(logo_path).resize((300, 180))
    qr_code = Image.open(qr_code_path).resize((205, 205))
    text_below_qr = "Powered by Retroserver"

    # Now let's use these placeholders to generate the final image
    # Create a new image with white background
    final_img = Image.new("RGB", (360, 500), color="white")

    # Calculate the position for the logo and QR code to be centered
    logo_position = (
        (final_img.width - logo.width) // 2,
        (final_img.height - logo.height - qr_code.height) // 3,
    )
    qr_code_position = (
        (final_img.width - qr_code.width) // 2,
        logo_position[1] + logo.height + 20,
    )

    # Paste the logo and QR code onto the final image
    final_img.paste(logo, logo_position)
    final_img.paste(qr_code, qr_code_position)

    # Create a draw object to add the border and dotted line
    draw = ImageDraw.Draw(final_img)

    # Define the border width
    border_width = 10

    # Draw the border
    for i in range(border_width):
        draw.rectangle(
            [(i, i), (final_img.width - i - 1, final_img.height - i - 1)],
            outline="black",
        )

    # Draw the dotted line
    line_start = (border_width, logo_position[1] + logo.height + 10)
    for x in range(line_start[0], final_img.width - border_width, 10):
        if (x // 10) % 2 == 0:  # Dots with space of 10 pixels
            draw.line([(x, line_start[1]), (x + 5, line_start[1])], fill="black")

    # Add the text below the QR code using a simple font (since Verdana is not available)
    font = ImageFont.load_default(size=22)

    # # Calculate text position (centered below QR code)
    # text_width = draw.textlength(text_below_qr, font=font)

    text_position = (
        qr_code_position[0] - 10,
        qr_code_position[1] + qr_code.height + 10,
    )

    # Apply the text onto the image
    draw.text(text_position, text_below_qr, font=font, fill="black")

    # Save the final image
    final_img.save(output_path)

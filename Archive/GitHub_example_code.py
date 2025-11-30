import fitz  # PyMuPDF
from deep_translator import GoogleTranslator
from tkinter import Tk, filedialog, messagebox
from colorama import init, Fore
import os
from collections import Counter
import requests
import string

# Initialize colorama
init(autoreset=True)

# Dictionary to store registered fonts
registered_fonts = {}

def detect_language(text):
    """
    Detects the language of the provided text.
    """
    from langdetect import detect
    try:
        language = detect(text)
        return language
    except Exception as e:
        print(Fore.RED + f"Error detecting language: {e}")
        return 'unknown'

def download_font_from_google(font_family_name, style):
    """
    Attempts to download a font from Google Fonts.
    """
    base_url = "https://github.com/google/fonts/raw/main/ofl/{}/{}"
    font_family = font_family_name.lower().replace(' ', '')
    style_suffix = ''
    if style == 'Bold':
        style_suffix = '-Bold'
    elif style == 'Italic':
        style_suffix = '-Italic'
    elif style == 'BoldItalic':
        style_suffix = '-BoldItalic'
    else:
        style_suffix = '-Regular'
    font_file_name = font_family.capitalize() + f"{style_suffix}.ttf"
    url = base_url.format(font_family, font_file_name)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(Fore.GREEN + f"Font '{font_file_name}' successfully downloaded from Google Fonts.")
            return response.content  # Return bytes
        else:
            print(Fore.YELLOW + f"Could not download font '{font_file_name}' from Google Fonts. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(Fore.YELLOW + f"Error attempting to download font '{font_file_name}' from Google Fonts: {e}")
        return None

def get_font(font_full_name, bold, italic, page):
    """
    Retrieves the name of the inserted font on the page, downloading it if necessary.
    """
    # Split the font name and style
    if '-' in font_full_name:
        font_family_name, _ = font_full_name.split('-', 1)
    else:
        font_family_name = font_full_name

    style = ''
    if bold and italic:
        style = 'BoldItalic'
    elif bold:
        style = 'Bold'
    elif italic:
        style = 'Italic'
    else:
        style = 'Regular'

    font_key = f"{font_family_name}-{style}"

    if font_key in registered_fonts:
        return registered_fonts[font_key]

    fonts_dir = os.path.join(os.getcwd(), 'fonts')
    if not os.path.exists(fonts_dir):
        os.makedirs(fonts_dir)

    # Define 'style_suffix' based on 'style'
    style_suffix = ''
    if style == 'Bold':
        style_suffix = '-Bold'
    elif style == 'Italic':
        style_suffix = '-Italic'
    elif style == 'BoldItalic':
        style_suffix = '-BoldItalic'
    else:
        style_suffix = '-Regular'

    font_filename = font_family_name.capitalize() + f"{style_suffix}.ttf"
    font_filepath = os.path.join(fonts_dir, font_filename)

    # Check if the font already exists in the 'fonts' directory
    if os.path.isfile(font_filepath):
        print(Fore.GREEN + f"Font '{font_filename}' found in the 'fonts' directory.")
    else:
        # Attempt to download the font
        font_data = download_font_from_google(font_family_name, style)
        if font_data:
            # Save the font to the 'fonts' directory
            with open(font_filepath, 'wb') as f:
                f.write(font_data)
            print(Fore.GREEN + f"Font '{font_filename}' saved in the 'fonts' directory.")
        else:
            print(Fore.YELLOW + f"Could not obtain font '{font_filename}'. Using fallback font.")
            return None  # Could not obtain the font

    # Insert the font into the page with a clean font name
    try:
        # Create a unique font name without invalid characters
        valid_chars = string.ascii_letters + string.digits + '_'
        fontname_clean = ''.join(c if c in valid_chars else '_' for c in font_key.replace(' ', '_').replace('-', '_'))
        # Insert the font with the clean name and specify encoding
        page.insert_font(fontname=fontname_clean, fontfile=font_filepath, encoding=0)
        # Register the clean font name
        registered_fonts[font_key] = fontname_clean
        # Verify that the font has been inserted correctly
        fonts_in_page = page.get_fonts()
        print(Fore.CYAN + f"Fonts on the page after insertion: {fonts_in_page}")
        return fontname_clean
    except Exception as e:
        print(Fore.RED + f"Error inserting font into the page: {e}")
        return None

def translate_pdf(target_lang='es'):
    # Configure Tkinter
    root = Tk()
    root.withdraw()

    # Select the PDF file
    input_path = filedialog.askopenfilename(
        title="Select the PDF file to translate",
        filetypes=[("PDF Files", "*.pdf")]
    )
    if not input_path:
        messagebox.showwarning("Warning", "No file was selected.")
        return

    # Select the save destination
    output_path = filedialog.asksaveasfilename(
        title="Save the translated PDF as",
        defaultextension=".pdf",
        filetypes=[("PDF Files", "*.pdf")]
    )
    if not output_path:
        messagebox.showwarning("Warning", "No save location was selected.")
        return

    try:
        # Open the original PDF
        doc = fitz.open(input_path)
        print(Fore.CYAN + f"Document loaded with {len(doc)} page(s).")

        # Detect the language of the document
        full_text = ""
        for page in doc:
            full_text += page.get_text()
        primary_language = detect_language(full_text)
        if primary_language.startswith('es'):
            target_lang = 'en'
            print(Fore.MAGENTA + "Detected language: Spanish. Translating to English.")
        elif primary_language.startswith('en'):
            target_lang = 'es'
            print(Fore.MAGENTA + "Detected language: English. Translating to Persian.")
        else:
            target_lang = None
            print(Fore.RED + "Could not clearly detect the document's language.")

        if not target_lang:
            messagebox.showerror("Error", "Could not detect the document's language.")
            return

        # Initialize the translator
        translator = GoogleTranslator(source='auto', target=target_lang)

        # Count initial characters
        initial_char_count = len(full_text)
        print(Fore.YELLOW + f"Initial character count: {initial_char_count}")

        # Process each page
        total_translated_chars = 0
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            print(Fore.CYAN + f"\nProcessing page {page_num + 1}/{len(doc)}...")

            # Ensure the page content is well-structured
            page.wrap_contents()

            # Extract text blocks
            blocks = page.get_text("dict")["blocks"]

            # List to store text blocks
            page_blocks = []
            for block_num, block in enumerate(blocks, start=1):
                if "lines" in block:
                    block_text = ""
                    block_bbox = None
                    fonts_in_block = []
                    font_sizes_in_block = []
                    font_colors_in_block = []
                    font_flags_in_block = []

                    for line in block["lines"]:
                        for span in line["spans"]:
                            if span["text"].strip():
                                text = span["text"]
                                bbox = span["bbox"]
                                font_name = span["font"]
                                font_size = span["size"]
                                font_color = span["color"]
                                font_flags = span["flags"]

                                # Accumulate text
                                block_text += text + " "

                                # Accumulate font properties
                                fonts_in_block.append(font_name)
                                font_sizes_in_block.append(font_size)
                                font_colors_in_block.append(font_color)
                                font_flags_in_block.append(font_flags)

                                # Calculate the bounding box of the block
                                if isinstance(bbox, (list, tuple)) and len(bbox) == 4:
                                    bbox = [float(coord) for coord in bbox]
                                    if block_bbox is None:
                                        block_bbox = bbox
                                    else:
                                        block_bbox[0] = min(block_bbox[0], bbox[0])
                                        block_bbox[1] = min(block_bbox[1], bbox[1])
                                        block_bbox[2] = max(block_bbox[2], bbox[2])
                                        block_bbox[3] = max(block_bbox[3], bbox[3])

                    if block_text.strip():
                        # Calculate average properties of the block
                        avg_font_size = sum(font_sizes_in_block) / len(font_sizes_in_block)
                        avg_font_color = font_colors_in_block[0]  # Use the first color
                        # Use the most common font
                        font_counts = Counter(fonts_in_block)
                        font_name = font_counts.most_common(1)[0][0]
                        # Determine font style
                        font_flags = font_flags_in_block[0]
                        bold = bool(font_flags & 2)
                        italic = bool(font_flags & 1)

                        page_blocks.append({
                            "block_num": block_num,
                            "text": block_text.strip(),
                            "bbox": block_bbox,
                            "font_name": font_name,
                            "font_size": avg_font_size,
                            "font_color": avg_font_color,
                            "bold": bold,
                            "italic": italic
                        })

            # Log the number of text blocks detected
            print(Fore.BLUE + f"Detected {len(page_blocks)} text block(s) on page {page_num + 1}.")

            # Draw bounding boxes for debugging (optional)
            # Uncomment the following lines to visualize bounding boxes
            # for block in page_blocks:
            #     rect = fitz.Rect(block["bbox"])
            #     page.draw_rect(rect, color=(1, 0, 0), width=1)

            # Remove the original text from the page using redactions
            for block in page_blocks:
                rect = fitz.Rect(block["bbox"])
                # Add a redaction annotation
                page.add_redact_annot(rect, fill=(1, 1, 1))
            # Apply the redactions
            page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)

            # Insert the translated text
            for block in page_blocks:
                original_text = block["text"]
                bbox = block["bbox"]
                font_name = block["font_name"]
                font_size = block["font_size"]
                font_color = block["font_color"]
                bold = block["bold"]
                italic = block["italic"]
                block_num = block["block_num"]

                # Translate the text
                try:
                    translated_text = translator.translate(original_text)
                    translated_text_length = len(translated_text)
                    print(Fore.BLUE + f"Block {block_num}: Translated text length: {translated_text_length}")
                    print(Fore.BLUE + f"Block {block_num}: Original text: {original_text[:50]}...")
                    print(Fore.BLUE + f"Block {block_num}: Translated text: {translated_text[:50]}...")
                except Exception as e:
                    print(Fore.RED + f"Block {block_num}: Error translating text: {e}")
                    translated_text = original_text
                    translated_text_length = len(translated_text)

                # Validate translated text
                if not translated_text.strip():
                    print(Fore.YELLOW + f"Block {block_num}: Translated text is empty. Skipping insertion.")
                    continue  # Skip inserting empty text

                # Convert color from int to RGB
                r = (font_color >> 16) & 255
                g = (font_color >> 8) & 255
                b = font_color & 255

                # Get the inserted font name
                fontname = get_font(font_name, bold, italic, page)
                if fontname:
                    print(Fore.GREEN + f"Block {block_num}: Using font '{fontname}' for the text.")
                else:
                    fontname = "helv"  # Fallback font
                    print(Fore.YELLOW + f"Block {block_num}: Using fallback font 'helv'.")
                    font_size = float(font_size)  # Ensure it's a float

                # Create a rectangle for the text
                rect = fitz.Rect(bbox)

                # Insert the translated text using insert_textbox with text wrapping and dynamic font size
                try:
                    # Log details about the insertion
                    print(Fore.MAGENTA + f"Block {block_num}: Inserting text into bbox {rect}")
                    print(Fore.MAGENTA + f"Block {block_num}: Font size: {font_size}, Font: {fontname}, Color: RGB({r}, {g}, {b})")

                    # Define text wrapping parameters
                    max_font_size = font_size
                    min_font_size = 6.0  # Define a minimum font size
                    wrapped_text = translated_text
                    current_font_size = font_size

                    # Estimate if text fits, adjust font size if necessary
                    # Since PyMuPDF doesn't provide text measurement, use heuristic based on character count
                    # Adjust based on length and original font size
                    # Note: This is a simplification; for precise measurement, integrate with Pillow or similar
                    # For now, reduce font size if translated text length exceeds a threshold
                    text_length = len(translated_text)
                    bbox_width = rect.width
                    bbox_height = rect.height

                    # Simple heuristic: Assume average character width based on font size
                    avg_char_width = current_font_size * 0.5  # Approximation
                    estimated_text_width = text_length * avg_char_width

                    while estimated_text_width > bbox_width and current_font_size > min_font_size:
                        current_font_size -= 0.5
                        estimated_text_width = text_length * (current_font_size * 0.5)
                        print(Fore.YELLOW + f"Block {block_num}: Adjusting font size to {current_font_size} to fit text.")

                    # Optionally, implement text wrapping by splitting into lines
                    # For simplicity, proceed with adjusted font size

                    # Insert the text
                    page.insert_textbox(
                        rect,
                        wrapped_text,
                        fontname=fontname,
                        fontsize=current_font_size,
                        color=(r/255, g/255, b/255),
                        align=0,  # Left alignment
                        encoding=0  # Ensure Latin encoding
                    )
                    print(Fore.GREEN + f"Block {block_num}: Translated text inserted in bbox {rect}.")
                    total_translated_chars += translated_text_length
                except Exception as e:
                    print(Fore.RED + f"Block {block_num}: Error inserting text in bbox {rect}: {e}")

        # Count characters in the translated PDF
        final_text = ""
        for page in doc:
            final_text += page.get_text()
        final_char_count = len(final_text)
        print(Fore.YELLOW + f"\nFinal character count: {final_char_count}")
        print(Fore.YELLOW + f"Total translated characters inserted: {total_translated_chars}")

        # Save the translated PDF
        doc.save(output_path)
        print(Fore.GREEN + f"\nTranslation completed. File saved at: {output_path}")

    except Exception as e:
        print(Fore.RED + f"An error occurred: {e}")
        messagebox.showerror("Error", f"An error occurred: {e}")

if __name__ == "__main__":
    translate_pdf()
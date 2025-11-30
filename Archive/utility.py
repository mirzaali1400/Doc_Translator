from colorama import init, Fore
import os
import requests
import string
import arabic_reshaper
from bidi.algorithm import get_display

# Dictionary to store registered fonts
registered_fonts = {}

def fix_rtl(text):
    reshaped = arabic_reshaper.reshape(text)  
    return get_display(reshaped)  

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

def get_persian_font(page):
    font_path = "fonts/BNazanin.ttf"  # Make sure it exists
    page.insert_font(fontname="BNazanin", fontfile=font_path)
    return "BNazanin"

def get_times_font(page):
    font_path = "fonts/koodak-bold.ttf"  # Make sure it exists
    page.insert_font(fontname="koodak-bold", fontfile=font_path)
    return "kookdak-bold"

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
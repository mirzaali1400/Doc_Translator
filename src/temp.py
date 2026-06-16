import os
import pathlib

# This is the exact string you provided
file_name = "lator'; & 'dTranslator.venvScriptspython.exe' 'cUsersA2M.vscodeextensionsms-python.debugpy-2025.18.0-win32-x64bundledlibsdebugpylauncher' '12263' '--' 'DTranslatorsrcTranslator.py'"

try:
    # Use pathlib to handle the pathing safely
    path = pathlib.Path(file_name)
    
    if path.exists():
        os.remove(path)
        print(f"Successfully removed: {file_name}")
    else:
        # If standard lookup fails, list the directory to find the actual match
        print("File not found via direct path. Looking for partial matches...")
        for f in pathlib.Path('.').iterdir():
            if "lator" in f.name:
                print(f"Found potential match: {f.name}")
                # os.remove(f) # Uncomment this line to force remove if identified
except Exception as e:
    print(f"Error: {e}")

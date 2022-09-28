from PIL import Image
import os
from flask import current_app

def add_profil_pict(picture, id):
    filename = picture.filename
    # Grab extension type .jpg or .png
    ext_type = filename.split('.')[-1]
    storage_filename = str(id) + '.' +ext_type
    
    filepath = os.path.join(current_app.root_path, 'static/profile_pic', storage_filename)

    # Play Around with this size.
    output_size = (200, 200)

    # Open the picture and save it
    pic = Image.open(picture)
    pic.thumbnail(output_size)
    pic.save(filepath)

    return storage_filename
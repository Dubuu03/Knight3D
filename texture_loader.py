from OpenGL.GL import *
from PIL import Image
import os

def load_texture(base_path):
    """Load texture with .png/.jpg/.jpeg extension fallback"""
    folder = "texture"
    base_name = os.path.splitext(os.path.basename(base_path))[0]
    extensions = [".png", ".jpg", ".jpeg"]

    for ext in extensions:
        tex_path = os.path.join(folder, base_name + ext)
        if os.path.exists(tex_path):
            image = Image.open(tex_path).convert("RGBA")
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
            img_data = image.tobytes()
            width, height = image.size

            texture_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texture_id)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            print(f"Loaded: {tex_path}")
            return texture_id

    print(f"⚠️ Texture not found for: {base_name} (tried .png/.jpg/.jpeg)")
    return 0  # return 0 if not found

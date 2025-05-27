import glm

# Window configuration
DISPLAY_WIDTH = 1000
DISPLAY_HEIGHT = 850
WINDOW_TITLE = "Knight Model Viewer"
BACKGROUND_COLOR = (0.05, 0.05, 0.1, 1.0) 

# Camera settings
FOV = 40.0  # Field of view in degrees
NEAR_PLANE = 0.1
FAR_PLANE = 100.0
CAMERA_POS = glm.vec3(0, 2, 6)
CAMERA_TARGET = glm.vec3(0, 1, 0)
CAMERA_UP = glm.vec3(0, 1, 0)

# Texture unit bindings
TEXTURE_UNITS = {
    "BaseColor": 0,
    "Normal": 1,
    "Roughness": 2,
    "Alpha": 3,
    "Metallic": 4,
    "Emissive": 5
}

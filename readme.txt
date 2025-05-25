Knight & Demon 3D Model Viewer
==============================

A real-time OpenGL-based viewer for animated 3D models of a knight and a demon, featuring smooth camera transitions, preset camera angles, and interactive controls.

--------------------------------------------------------------------------------
FEATURES
--------------------------------------------------------------------------------
- View two detailed 3D models (knight and demon) with textures and animations.
- Smooth camera transitions between preset angles (no teleporting!).
- Multiple camera presets for both characters (full view, close-ups, etc.).
- Animated model parts (e.g., cloak, roses) for a lively scene.
- Toggle between viewing both models, only the knight, or only the demon.
- Manual camera rotation and zoom for custom exploration.
- Emissive glow effects on certain model parts (e.g., eyes, sword).
- Real-time lighting and basic shading.
- Easy extensibility for new models, textures, or camera presets.

--------------------------------------------------------------------------------
CONTROLS
--------------------------------------------------------------------------------
Keyboard:
  - LEFT/RIGHT Arrow: Cycle through camera presets for the current view mode.
  - TAB: Switch view mode (both → knight → demon → both).
  - SPACE: Toggle free camera rotation (manual control).
  - R: Reset camera and view mode to default.
  - P: Print current camera parameters to the console.
  - ESC: Quit the application.

Mouse:
  - Left Click + Drag: Rotate camera (when in free camera mode).
  - Scroll Wheel: Zoom in/out.

--------------------------------------------------------------------------------
SETUP INSTRUCTIONS
--------------------------------------------------------------------------------
1. **Requirements**
   - Python 3.8+
   - pip (Python package manager)
   - A GPU and drivers supporting OpenGL 3.3 or higher

2. **Install Dependencies**
   Open a terminal in the project directory and run:
   ```
   pip install pygame PyOpenGL PyOpenGL_accelerate numpy glm
   ```

3. **Project Structure**
   - `main.py`           : Main application entry point.
   - `config.py`         : Configuration for window, camera, and texture units.
   - `shader.py`         : OpenGL shader code and program creation.
   - `loader/`           : Model, texture, and animation loading modules.
   - `data/`             : Camera presets and animation data (JSON).
   - `knight/`, `demon/` : Model part definitions (as .txt files).
   - `texture/`          : All required textures for the models.
   - `background.mp4`    : (Optional) Background video or asset.

4. **Running the Viewer**
   ```
   python main.py
   ```
   The window will open with both models visible and the default camera angle.

5. **Adding/Editing Camera Presets**
   - Edit `data/camera_presets.json` to add or modify camera angles.
   - Each preset can specify: name, rot_x, rot_y, zoom, focus_y, focus, and description.

6. **Customizing Animations**
   - Edit `data/animation_data.json` to tweak or add new part animations.

7. **Adding New Models or Textures**
   - Place new model part `.txt` files in `knight/parts/` or `demon/parts/`.
   - Add new textures to the `texture/` folder and reference them in the model part files.

--------------------------------------------------------------------------------
NOTES & TROUBLESHOOTING
--------------------------------------------------------------------------------
- If you see a blank window or errors about OpenGL, ensure your GPU drivers are up to date and support OpenGL 3.3+.
- All model part files must be in the correct format (see existing files in `knight/parts/` for reference).
- Textures must be standard image formats (PNG, JPEG).
- For best performance, close other GPU-intensive applications while running the viewer.

--------------------------------------------------------------------------------
CREDITS
--------------------------------------------------------------------------------
- Developed by Dustin Drix M. Narciso
- Uses Pygame, PyOpenGL, numpy, and glm for Python

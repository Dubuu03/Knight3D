import pygame
from pygame.locals import *
from OpenGL.GL import *
import glm
import math
import random
import os

import config
from loader.model_loader import load_model_from_txt
from loader.texture_loader import load_texture
from shader import create_shader_program
from loader.animation_loader import initialize_animations, update_animations, load_camera_presets

def draw_ground():
    glBegin(GL_QUADS)
    glColor3f(0.3, 0.3, 0.3)
    glVertex3f(-50, 0, -50)
    glVertex3f(50, 0, -50)
    glVertex3f(50, 0, 50)
    glVertex3f(-50, 0, 50)
    glEnd()



def main():
    pygame.init()
    display = (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption(config.WINDOW_TITLE)
    pygame.mouse.set_visible(True)
    pygame.event.set_grab(False)
    glClearColor(*config.BACKGROUND_COLOR)
    glEnable(GL_DEPTH_TEST)

    shader_program = create_shader_program()
    glUseProgram(shader_program)

    objects = load_model_from_txt("knight/parts", load_texture)
    animation_data = initialize_animations(objects)

    projection = glm.perspective(glm.radians(config.FOV), display[0] / display[1], config.NEAR_PLANE, config.FAR_PLANE)
    proj_loc = glGetUniformLocation(shader_program, "projection")
    view_loc = glGetUniformLocation(shader_program, "view")
    model_loc = glGetUniformLocation(shader_program, "model")
    light_loc = glGetUniformLocation(shader_program, "lightPos")
    view_pos_loc = glGetUniformLocation(shader_program, "viewPos")
    emissive_loc = glGetUniformLocation(shader_program, "emissiveColor")

    glUniformMatrix4fv(proj_loc, 1, GL_FALSE, glm.value_ptr(projection))

    clock = pygame.time.Clock()
    rotating = False
    last_mouse_pos = pygame.mouse.get_pos()
    rot_x, rot_y = 0.0, 0.0
    zoom = 6.0
    idle_angle = 0.0
    elapsed_time = 0.0
    auto_rotate = True  # Start with auto-rotation enabled
    is_preset_view = False  # Start with free rotation mode enabled
    
    # Load camera presets from JSON file
    camera_presets = load_camera_presets()
    current_camera_preset = 0
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        elapsed_time += dt

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_RIGHT:
                    # Switch to the next camera preset
                    current_camera_preset = (current_camera_preset + 1) % len(camera_presets)
                    preset = camera_presets[current_camera_preset]
                    rot_x = preset["rot_x"]
                    rot_y = preset["rot_y"]
                    zoom = preset["zoom"]
                    idle_angle = 0.0  # Reset idle angle when changing camera view
                    rotating = False  # Stop rotation when changing camera view
                    auto_rotate = False  # Turn off auto-rotation when switching camera
                    # Store that this is a preset camera view
                    is_preset_view = True
                    print(f"Camera: {preset['name']}")
                elif event.key == K_LEFT:
                    # Switch to the previous camera preset
                    current_camera_preset = (current_camera_preset - 1) % len(camera_presets)
                    preset = camera_presets[current_camera_preset]
                    rot_x = preset["rot_x"]
                    rot_y = preset["rot_y"]
                    zoom = preset["zoom"]
                    idle_angle = 0.0  # Reset idle angle when changing camera view
                    rotating = False  # Stop rotation when changing camera view
                    auto_rotate = False  # Turn off auto-rotation when switching camera
                    # Store that this is a preset camera view
                    is_preset_view = True
                    print(f"Camera: {preset['name']}")
                elif event.key == K_SPACE:
                    # Toggle auto-rotation with spacebar
                    auto_rotate = not auto_rotate
                    is_preset_view = False
                    if auto_rotate:
                        print("Auto-rotation enabled")
                    else:
                        print("Auto-rotation disabled")
                elif event.key == K_p:
                    # Print current camera position and rotation
                    print(f"Current Camera: rot_x={rot_x:.1f}, rot_y={rot_y:.1f}, zoom={zoom:.1f}, focus_y={focus_y:.1f}")
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    rotating = True
                    last_mouse_pos = pygame.mouse.get_pos()
                elif event.button == 4:
                    zoom = max(2.0, zoom - 0.5)
                elif event.button == 5:
                    zoom += 0.5
            elif event.type == MOUSEBUTTONUP and event.button == 1:
                rotating = False
            elif event.type == MOUSEMOTION and rotating:
                x, y = pygame.mouse.get_pos()
                dx = x - last_mouse_pos[0]
                dy = y - last_mouse_pos[1]
                rot_y += dx * 0.3
                rot_x += dy * 0.3
                last_mouse_pos = (x, y)

        if not rotating:
            if auto_rotate:
                idle_angle += 15 * dt

        update_animations(objects, dt, elapsed_time)
        
        # Get focus height from current preset or default to 1.0
        focus_y = camera_presets[current_camera_preset].get('focus_y', 1.0)
        camera_pos = glm.vec3(0, 2.5, zoom)
        view = glm.lookAt(camera_pos, glm.vec3(0, focus_y, 0), glm.vec3(0, 1, 0))
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, glm.value_ptr(view))
        
        light_position = glm.vec3(0.0, 10.0, 3.0)
        glUniform3fv(light_loc, 1, glm.value_ptr(light_position))
        glUniform3fv(view_pos_loc, 1, glm.value_ptr(camera_pos))
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUniform3fv(emissive_loc, 1, glm.value_ptr(glm.vec3(0.0)))
        draw_ground()

        base_model = glm.mat4(1.0)
        base_model = glm.translate(base_model, glm.vec3(0, 0.0, 0))
        base_model = glm.rotate(base_model, glm.radians(rot_x), glm.vec3(1, 0, 0))
        base_model = glm.rotate(base_model, glm.radians(rot_y + idle_angle), glm.vec3(0, 1, 0))

        glow_strength = (math.sin(pygame.time.get_ticks() * 0.002) + 1.0) * 0.5
        glow_color = glm.vec3(1.0, 0.2, 0.6) * glow_strength
        zero_color = glm.vec3(0.0, 0.0, 0.0)

        # First, draw all non-glowing objects
        for obj in objects:
            name = getattr(obj, 'name', '').lower()
            if 'eye' not in name and 'sword' not in name:
                model = obj.get_model_matrix(base_model)
                glUniform3fv(emissive_loc, 1, glm.value_ptr(zero_color))
                obj.draw(shader_program, config.TEXTURE_UNITS, model_loc, model)
        
        # Then draw all glowing objects
        for obj in objects:
            name = getattr(obj, 'name', '').lower()
            if 'eye' in name or 'sword' in name:
                model = obj.get_model_matrix(base_model)
                
                # Custom glow colors based on part
                if 'eye' in name:
                    part_glow = glm.vec3(1.0, 0.2, 0.6) * glow_strength  # Pink/purple glow for eyes
                elif 'sword' in name:
                    part_glow = glm.vec3(0.2, 0.8, 1.0) * glow_strength  # Blue glow for sword
                
                glUniform3fv(emissive_loc, 1, glm.value_ptr(part_glow))
                obj.draw(shader_program, config.TEXTURE_UNITS, model_loc, model)

        pygame.display.flip()

    for obj in objects:
        obj.cleanup()

    glUseProgram(0)
    glDeleteProgram(shader_program)
    glDisable(GL_DEPTH_TEST)
    pygame.quit()

if __name__ == "__main__":
    main()

import pygame
from pygame.locals import *
from OpenGL.GL import *
import glm
import math
import random
import json
import os

import config
from model_loader import load_model_from_txt
from texture_loader import load_texture
from shader import create_shader_program

def load_animation_data():
    """Load animation data from JSON file"""
    try:
        with open('animation_data.json', 'r') as f:
            data = json.load(f)
        print("Animation data loaded from animation_data.json")
        return data
    except Exception as e:
        print(f"Error loading animation data: {e}")
        return {}

def draw_ground():
    glBegin(GL_QUADS)
    glColor3f(0.3, 0.3, 0.3)
    glVertex3f(-50, 0, -50)
    glVertex3f(50, 0, -50)
    glVertex3f(50, 0, 50)
    glVertex3f(-50, 0, 50)
    glEnd()

def initialize_animations(objects):
    animation_json = load_animation_data()
    for obj in objects:
        name = getattr(obj, 'name', '').lower()
        obj.animation_data['offset'] = glm.vec3(0.0)
        obj.animation_data['rotation'] = glm.vec3(0.0)
        obj.animation_data['scale'] = glm.vec3(1.0)

        if name in animation_json:
            obj.animation_data['custom'] = animation_json[name]
    return animation_json

def update_animations(objects, dt, time):
    for obj in objects:
        obj.update_animation(dt)
        name = getattr(obj, 'name', '').lower()

        if 'rose' in name and 'custom' in obj.animation_data:
            custom = obj.animation_data['custom']
            bob_y = custom['bob_amplitude'] * math.sin(time * custom['bob_frequency'] + custom['bob_phase'])
            obj.animation_data['offset'].y = bob_y
            obj.animation_data['rotation'].y = math.sin(time * 0.5) * 0.02

        elif 'cloak' in name and 'custom' in obj.animation_data:
            custom = obj.animation_data['custom']
            
            # Time with slight random offset for natural difference
            time_offset = time + custom.get('random_offset', 0)
            
            # Gentle vertical sway
            wave_y = custom['primary_amplitude'] * math.sin(time_offset * custom['primary_frequency'])
            
            # Gentle lateral motion with phase shift
            wave_x = custom['secondary_amplitude'] * math.sin(time_offset * custom['secondary_frequency'] + math.pi / 2)
            
            # Small Z depth flutter (trailing)
            wave_z = (custom['secondary_amplitude'] * 0.5) * math.sin(time_offset * custom['secondary_frequency'] * 0.6)
            
            min_y = -0.03  # Adjust this to control how low it can go
            clamped_y = max(wave_y * 0.3, min_y)
            
            # Apply soft translation offsets
            obj.animation_data['offset'].x = wave_x * 0.2
            obj.animation_data['offset'].y = clamped_y
            obj.animation_data['offset'].z = wave_z * 0.1
            
            # Apply natural smooth rotations (like the cloak tilting back and forth)
            obj.animation_data['rotation'].x = wave_y * 0.1
            obj.animation_data['rotation'].y = wave_z * 0.08
            obj.animation_data['rotation'].z = wave_x * 0.1

            # Subtle breathing/puffing scaling (less intense)
            flutter = custom['flutter'] * math.sin(time_offset * 1.5)
            obj.animation_data['scale'].x = 1.0 + flutter * 0.2
            obj.animation_data['scale'].y = 1.0 + flutter * 0.3
            obj.animation_data['scale'].z = 1.0 - flutter * 0.1



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

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        elapsed_time += dt

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                running = False
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
            idle_angle += 15 * dt

        update_animations(objects, dt, elapsed_time)

        camera_pos = glm.vec3(0, 2.5, zoom)
        view = glm.lookAt(camera_pos, glm.vec3(0, 1.0, 0), glm.vec3(0, 1, 0))
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

        for obj in objects:
            name = getattr(obj, 'name', '').lower()
            model = obj.get_model_matrix(base_model)

            if 'eye' in name or 'sword' in name:
                glUniform3fv(emissive_loc, 1, glm.value_ptr(glow_color))
            else:
                glUniform3fv(emissive_loc, 1, glm.value_ptr(glm.vec3(0.0)))

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

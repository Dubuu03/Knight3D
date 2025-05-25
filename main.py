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

    knight_objects = load_model_from_txt("knight/parts", load_texture)
    demon_objects = load_model_from_txt("demon/parts", load_texture)
    initialize_animations(knight_objects)
    initialize_animations(demon_objects)

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

    # Load camera presets from JSON file
    camera_presets = load_camera_presets()
    
    def get_presets_for_mode(mode):
        if mode == "knight":
            return [p for p in camera_presets if p.get("focus", "knight") == "knight"]
        elif mode == "demon":
            return [p for p in camera_presets if p.get("focus", "demon") == "demon"]
        else:
            return [p for p in camera_presets if p.get("focus", "both") == "both" or p.get("focus") not in ("knight", "demon")]

    view_mode = "both"
    current_presets = get_presets_for_mode(view_mode)
    current_camera_preset = 0 if current_presets else -1
    if current_presets:
        preset = current_presets[current_camera_preset]
        rot_x = preset["rot_x"]
        rot_y = preset["rot_y"]
        zoom = preset["zoom"]
        focus_y = preset.get("focus_y", 1.0)
    else:
        rot_x, rot_y, zoom, focus_y = -3.6, 2.1, 10.0, 1.0
    idle_angle = 0.0
    elapsed_time = 0.0
    is_preset_view = True
    print(f"Initial Camera: {view_mode} mode, preset: {preset['name'] if current_presets else 'Custom Start View (manual)'}")

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        elapsed_time += dt

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                running = False

            elif event.type == KEYDOWN:
                if event.key == K_RIGHT:
                    current_presets = get_presets_for_mode(view_mode)
                    if current_presets:
                        current_camera_preset = (current_camera_preset + 1) % len(current_presets)
                        preset = current_presets[current_camera_preset]
                        rot_x = preset["rot_x"]
                        rot_y = preset["rot_y"]
                        zoom = preset["zoom"]
                        focus_y = preset.get("focus_y", 1.0)
                        idle_angle = 0.0
                        rotating = False
                        is_preset_view = True
                        print(f"Camera: {preset['name']}")
                elif event.key == K_LEFT:
                    current_presets = get_presets_for_mode(view_mode)
                    if current_presets:
                        current_camera_preset = (current_camera_preset - 1) % len(current_presets)
                        preset = current_presets[current_camera_preset]
                        rot_x = preset["rot_x"]
                        rot_y = preset["rot_y"]
                        zoom = preset["zoom"]
                        focus_y = preset.get("focus_y", 1.0)
                        idle_angle = 0.0
                        rotating = False
                        is_preset_view = True
                        print(f"Camera: {preset['name']}")
                elif event.key == K_SPACE:
                    is_preset_view = not is_preset_view
                    print("Free camera rotation enabled" if not is_preset_view else "Free camera rotation disabled – back to preset mode")
                elif event.key == K_p:
                    print(f"Current Camera: rot_x={rot_x:.1f}, rot_y={rot_y:.1f}, zoom={zoom:.1f}, focus_y={focus_y:.1f}")
                elif event.key == K_r:
                    view_mode = "both"
                    current_presets = get_presets_for_mode(view_mode)
                    current_camera_preset = -1
                    rot_x = -3.6
                    rot_y = 2.1
                    zoom = 10.0
                    focus_y = 1.0
                    idle_angle = 0.0
                    rotating = False
                    is_preset_view = True
                    print("Camera and view mode reset to custom start view")
                elif event.key == K_TAB:
                    if view_mode == "both":
                        view_mode = "knight"
                    elif view_mode == "knight":
                        view_mode = "demon"
                    else:
                        view_mode = "both"
                    current_presets = get_presets_for_mode(view_mode)
                    current_camera_preset = 0 if current_presets else -1
                    if current_presets:
                        preset = current_presets[current_camera_preset]
                        rot_x = preset["rot_x"]
                        rot_y = preset["rot_y"]
                        zoom = preset["zoom"]
                        focus_y = preset.get("focus_y", 1.0)
                        idle_angle = 0.0
                        rotating = False
                        is_preset_view = True
                        print(f"Switched view mode to: {view_mode}, Camera: {preset['name']}")
                    else:
                        print(f"Switched view mode to: {view_mode}, no presets available.")

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

        if not rotating and not is_preset_view:
            idle_angle -= 15 * dt

        update_animations(knight_objects, dt, elapsed_time)
        update_animations(demon_objects, dt, elapsed_time)

        focus_y = current_presets[current_camera_preset]["focus_y"] if current_camera_preset >= 0 and current_presets else focus_y
        camera_pos = glm.vec3(0, 2.5, zoom)

        # Use view_mode to determine what to focus on
        if view_mode == "both":
            view_target = glm.vec3(0, focus_y, 0)
        elif view_mode == "knight":
            view_target = glm.vec3(-1.5, focus_y, 0)
        elif view_mode == "demon":
            view_target = glm.vec3(1.5, focus_y, 0)
        else:
            view_target = glm.vec3(0, focus_y, 0)

        view = glm.lookAt(camera_pos, view_target, glm.vec3(0, 1, 0))
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, glm.value_ptr(view))

        light_position = glm.vec3(0.0, 10.0, 3.0)
        glUniform3fv(light_loc, 1, glm.value_ptr(light_position))
        glUniform3fv(view_pos_loc, 1, glm.value_ptr(camera_pos))

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUniform3fv(emissive_loc, 1, glm.value_ptr(glm.vec3(0.0)))

        # Draw ground with fixed color, not affected by shader
        glUseProgram(0)
        glDisable(GL_TEXTURE_2D)
        draw_ground()
        glUseProgram(shader_program)

        # Knight render
        knight_model = glm.mat4(1.0)
        knight_model = glm.translate(knight_model, glm.vec3(-1.5, 0.0, 0))
        knight_model = glm.rotate(knight_model, glm.radians(rot_x), glm.vec3(1, 0, 0))
        knight_model = glm.rotate(knight_model, glm.radians(90), glm.vec3(0, 1, 0))
        knight_model = glm.rotate(knight_model, glm.radians(rot_y + idle_angle), glm.vec3(0, 1, 0))

        glow_strength = (math.sin(pygame.time.get_ticks() * 0.002) + 1.0) * 0.5
        zero_color = glm.vec3(0.0, 0.0, 0.0)

        for obj in knight_objects:
            name = getattr(obj, 'name', '').lower()
            if 'eye' not in name and 'sword' not in name:
                model = obj.get_model_matrix(knight_model)
                glUniform3fv(emissive_loc, 1, glm.value_ptr(zero_color))
                obj.draw(shader_program, config.TEXTURE_UNITS, model_loc, model)

        for obj in knight_objects:
            name = getattr(obj, 'name', '').lower()
            if 'eye' in name or 'sword' in name:
                model = obj.get_model_matrix(knight_model)
                if 'eye' in name:
                    part_glow = glm.vec3(1.0, 0.0, 0.0) * glow_strength
                elif 'sword' in name:
                    part_glow = glm.vec3(1.0, 0.0, 0.0) * glow_strength
                glUniform3fv(emissive_loc, 1, glm.value_ptr(part_glow))
                obj.draw(shader_program, config.TEXTURE_UNITS, model_loc, model)

        # Demon render
        demon_model = glm.mat4(1.0)
        demon_model = glm.translate(demon_model, glm.vec3(1.5, 0.0, 0))
        demon_model = glm.rotate(demon_model, glm.radians(rot_x), glm.vec3(1, 0, 0))
        demon_model = glm.rotate(demon_model, glm.radians(180), glm.vec3(0, 1, 0))
        demon_model = glm.rotate(demon_model, glm.radians(-(rot_y + idle_angle)), glm.vec3(0, 1, 0))

        for obj in demon_objects:
            model = obj.get_model_matrix(demon_model)
            glUniform3fv(emissive_loc, 1, glm.value_ptr(zero_color))
            obj.draw(shader_program, config.TEXTURE_UNITS, model_loc, model)

        pygame.display.flip()

    for obj in knight_objects:
        obj.cleanup()
    for obj in demon_objects:
        obj.cleanup()

    glUseProgram(0)
    glDeleteProgram(shader_program)
    glDisable(GL_DEPTH_TEST)
    pygame.quit()


if __name__ == "__main__":
    main()
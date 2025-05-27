import pygame
from pygame.locals import *
from OpenGL.GL import *
import glm
import math
import config
from loader.model_loader import load_model_from_txt
from loader.texture_loader import load_texture
from shader import create_shader_program
from loader.animation_loader import initialize_animations, update_animations, load_camera_presets
from loader.background_loader import create_bg_shader_program, create_bg_quad, init_video_texture, update_video_texture
import cv2

def main():
    pygame.init()
    pygame.mixer.init()
    display = (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption(config.WINDOW_TITLE)
    pygame.mouse.set_visible(True)
    pygame.event.set_grab(False)
    glClearColor(*config.BACKGROUND_COLOR)
    glEnable(GL_DEPTH_TEST)

    shader_program = create_shader_program()
    glUseProgram(shader_program)
    cap = cv2.VideoCapture("mata.mp4")
    video_texture = init_video_texture()
    bg_shader = create_bg_shader_program()
    bg_VAO, bg_VBO = create_bg_quad()

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

    camera_presets = load_camera_presets()

    def get_presets_for_mode(mode):
        if mode == "knight":
            return [p for p in camera_presets if p.get("focus", "knight") == "knight"]
        elif mode == "demon":
            return [p for p in camera_presets if p.get("focus", "demon") == "demon"]
        else:
            return [p for p in camera_presets if p.get("focus", "both") == "both" or p.get("focus") not in ("knight", "demon")]

    # Start with custom manual view (same as reset)
    view_mode = "both"
    current_presets = get_presets_for_mode(view_mode)
    current_camera_preset = -1
    rot_x = -3.6
    rot_y = 2.1
    zoom = 10.0
    focus_y = 1.0
    idle_angle = 0.0
    elapsed_time = 0.0
    is_preset_view = True
    print("Initial Camera: Custom Start View (manual)")

    # Camera animation state
    animating_camera = False
    anim_time = 0.0
    anim_duration = 0.5  # seconds for transition
    cam_start = {"rot_x": rot_x, "rot_y": rot_y, "zoom": zoom, "focus_y": focus_y}
    cam_target = {"rot_x": rot_x, "rot_y": rot_y, "zoom": zoom, "focus_y": focus_y}

    def start_camera_animation(new_rot_x, new_rot_y, new_zoom, new_focus_y):
        nonlocal animating_camera, anim_time, cam_start, cam_target
        animating_camera = True
        anim_time = 0.0
        cam_start = {"rot_x": rot_x, "rot_y": rot_y, "zoom": zoom, "focus_y": focus_y}
        cam_target = {"rot_x": new_rot_x, "rot_y": new_rot_y, "zoom": new_zoom, "focus_y": new_focus_y}
    
    # add music
    pygame.mixer.music.load("mata.mp3")
    pygame.mixer.music.play(-1)
    
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
                        start_camera_animation(
                            preset["rot_x"],
                            preset["rot_y"],
                            preset["zoom"],
                            preset.get("focus_y", 1.0)
                        )
                        idle_angle = 0.0
                        rotating = False
                        is_preset_view = True
                        print(f"Camera: {preset['name']}")

                elif event.key == K_LEFT:
                    current_presets = get_presets_for_mode(view_mode)
                    if current_presets:
                        current_camera_preset = (current_camera_preset - 1) % len(current_presets)
                        preset = current_presets[current_camera_preset]
                        start_camera_animation(
                            preset["rot_x"],
                            preset["rot_y"],
                            preset["zoom"],
                            preset.get("focus_y", 1.0)
                        )
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
                    start_camera_animation(-3.6, 2.1, 10.0, 1.0)
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
                        start_camera_animation(
                            preset["rot_x"],
                            preset["rot_y"],
                            preset["zoom"],
                            preset.get("focus_y", 1.0)
                        )
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

        # Camera animation update
        if animating_camera:
            anim_time += dt
            t = min(anim_time / anim_duration, 1.0)
            t_smooth = t * t * (3 - 2 * t)  # smoothstep
            rot_x = cam_start["rot_x"] + (cam_target["rot_x"] - cam_start["rot_x"]) * t_smooth
            rot_y = cam_start["rot_y"] + (cam_target["rot_y"] - cam_start["rot_y"]) * t_smooth
            zoom = cam_start["zoom"] + (cam_target["zoom"] - cam_start["zoom"]) * t_smooth
            focus_y = cam_start["focus_y"] + (cam_target["focus_y"] - cam_start["focus_y"]) * t_smooth
            if t >= 1.0:
                animating_camera = False

        focus_y = current_presets[current_camera_preset]["focus_y"] if current_camera_preset >= 0 and current_presets else focus_y
        camera_pos = glm.vec3(0, 2.5, zoom)

        view_target = glm.vec3(
            -1.5 if view_mode == "knight" else 1.5 if view_mode == "demon" else 0,
            focus_y,
            0
        )

        view = glm.lookAt(camera_pos, view_target, glm.vec3(0, 1, 0))
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, glm.value_ptr(view))

        light_position = glm.vec3(0.0, 10.0, 3.0)
        glUniform3fv(light_loc, 1, glm.value_ptr(light_position))
        glUniform3fv(view_pos_loc, 1, glm.value_ptr(camera_pos))
        
        # 🎥 Draw video background first
        glClear(GL_COLOR_BUFFER_BIT)
        glDisable(GL_DEPTH_TEST)

        update_video_texture(cap, video_texture)

        glUseProgram(bg_shader)
        glBindVertexArray(bg_VAO)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, video_texture)
        bg_tex_loc = glGetUniformLocation(bg_shader, "backgroundTexture")
        glUniform1i(bg_tex_loc, 0)
        glDrawArrays(GL_TRIANGLES, 0, 6)
        glBindVertexArray(0)

        # ✅ Switch back to 3D shader for the scene
        glEnable(GL_DEPTH_TEST)
        glClear(GL_DEPTH_BUFFER_BIT)
        glUseProgram(shader_program)

        # ✅ Now safe to set uniforms like emissive
        glUniform3fv(emissive_loc, 1, glm.value_ptr(glm.vec3(0.0)))

        knight_model = glm.mat4(1.0)
        apply_knight_offset = (
            view_mode == "knight"
            and current_camera_preset >= 0
            and "full view" in current_presets[current_camera_preset]["name"].lower()
        )
        knight_offset_y = -0.3 if apply_knight_offset else 0.0
        knight_model = glm.translate(knight_model, glm.vec3(-1.5, knight_offset_y, 0))
        knight_model = glm.rotate(knight_model, glm.radians(rot_x), glm.vec3(1, 0, 0))
        knight_model = glm.rotate(knight_model, glm.radians(90), glm.vec3(0, 1, 0))
        knight_model = glm.rotate(knight_model, glm.radians(rot_y + idle_angle), glm.vec3(0, 1, 0))

        glow_strength = (math.sin(pygame.time.get_ticks() * 0.002) + 1.0) * 0.5
        zero_color = glm.vec3(0.0, 0.0, 0.0)

        for obj in knight_objects:
            name = getattr(obj, 'name', '').lower()
            model = obj.get_model_matrix(knight_model)
            glow = glm.vec3(1.0, 0.0, 0.0) * glow_strength if 'eye' in name or 'sword' in name else zero_color
            glUniform3fv(emissive_loc, 1, glm.value_ptr(glow))
            obj.draw(shader_program, config.TEXTURE_UNITS, model_loc, model)

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

    for obj in knight_objects + demon_objects:
        obj.cleanup()

    glUseProgram(0)
    glDeleteProgram(shader_program)
    glDisable(GL_DEPTH_TEST)
    pygame.quit()

if __name__ == "__main__":
    main()

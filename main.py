import pygame
from pygame.locals import *
from OpenGL.GL import *
import glm
import math

import config
from model_loader import load_model_from_txt
from texture_loader import load_texture
from shader import create_shader_program

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

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
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

        camera_pos = glm.vec3(0, 2.5, zoom)
        view = glm.lookAt(camera_pos, glm.vec3(0, 1.0, 0), glm.vec3(0, 1, 0))
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, glm.value_ptr(view))


        light_position = glm.vec3(0.0, 10.0, 3.0)
        glUniform3fv(light_loc, 1, glm.value_ptr(light_position))
        glUniform3fv(view_pos_loc, 1, glm.value_ptr(camera_pos))

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUniform3fv(emissive_loc, 1, glm.value_ptr(glm.vec3(0.0)))
        draw_ground()

        model = glm.mat4(1.0)
        model = glm.translate(model, glm.vec3(0, 0.0, 0))
        model = glm.rotate(model, glm.radians(rot_x), glm.vec3(1, 0, 0))
        model = glm.rotate(model, glm.radians(rot_y + idle_angle), glm.vec3(0, 1, 0))
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, glm.value_ptr(model))

        glow_strength = (math.sin(pygame.time.get_ticks() * 0.002) + 1.0) * 0.5
        glow_color = glm.vec3(1.0, 0.2, 0.6) * glow_strength

        for obj in objects:
            name = getattr(obj, 'name', '').lower()
            if 'eye' in name or 'sword' in name:
                glUniform3fv(emissive_loc, 1, glm.value_ptr(glow_color))
            else:
                glUniform3fv(emissive_loc, 1, glm.value_ptr(glm.vec3(0.0)))
            obj.draw(shader_program, config.TEXTURE_UNITS)

        pygame.display.flip()
        
        #Cleanup

    pygame.quit()

if __name__ == "__main__":
    main()

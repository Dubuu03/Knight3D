import pygame
from pygame.locals import *
from OpenGL.GL import *
import glm

import config
from model_loader import load_model_from_txt
from texture_loader import load_texture
from shader import create_shader_program

def main():
    pygame.init()
    display = (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption(config.WINDOW_TITLE)

    glEnable(GL_DEPTH_TEST)

    shader_program = create_shader_program()
    glUseProgram(shader_program)

    objects = load_model_from_txt("parts", load_texture)

    projection = glm.perspective(glm.radians(config.FOV), display[0] / display[1], config.NEAR_PLANE, config.FAR_PLANE)
    view = glm.lookAt(config.CAMERA_POS, config.CAMERA_TARGET, config.CAMERA_UP)
    model = glm.mat4(1.0)

    proj_loc = glGetUniformLocation(shader_program, "projection")
    view_loc = glGetUniformLocation(shader_program, "view")
    model_loc = glGetUniformLocation(shader_program, "model")

    glUniformMatrix4fv(proj_loc, 1, GL_FALSE, glm.value_ptr(projection))
    glUniformMatrix4fv(view_loc, 1, GL_FALSE, glm.value_ptr(view))

    clock = pygame.time.Clock()
    angle = 0.0
    running = True
    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        angle += 0.5
        rot_model = glm.rotate(model, glm.radians(angle), glm.vec3(0, 1, 0))
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, glm.value_ptr(rot_model))

        for obj in objects:
            obj.draw(shader_program, config.TEXTURE_UNITS)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()

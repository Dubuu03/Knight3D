from OpenGL.GL import *
import pygame
import numpy as np
import ctypes

# Background quad shaders
bg_vertex_shader = """
#version 330 core
layout(location = 0) in vec2 position;
layout(location = 1) in vec2 texCoord;
out vec2 TexCoord;
void main() {
    gl_Position = vec4(position, 0.0, 1.0);
    TexCoord = texCoord;
}
"""

bg_fragment_shader = """
#version 330 core
in vec2 TexCoord;
out vec4 FragColor;
uniform sampler2D backgroundTexture;
void main() {
    FragColor = texture(backgroundTexture, TexCoord);
}
"""

def create_bg_shader_program():
    vs = glCreateShader(GL_VERTEX_SHADER)
    fs = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(vs, bg_vertex_shader)
    glShaderSource(fs, bg_fragment_shader)
    glCompileShader(vs)
    glCompileShader(fs)

    for shader, name in [(vs, "VERTEX"), (fs, "FRAGMENT")]:
        success = glGetShaderiv(shader, GL_COMPILE_STATUS)
        if not success:
            print(f"{name} SHADER ERROR:", glGetShaderInfoLog(shader).decode())

    program = glCreateProgram()
    glAttachShader(program, vs)
    glAttachShader(program, fs)
    glLinkProgram(program)
    glDeleteShader(vs)
    glDeleteShader(fs)
    return program

def create_bg_quad():
    quad_vertices = np.array([
        -1.0,  1.0,  0.0, 1.0,
        -1.0, -1.0,  0.0, 0.0,
         1.0, -1.0,  1.0, 0.0,
        -1.0,  1.0,  0.0, 1.0,
         1.0, -1.0,  1.0, 0.0,
         1.0,  1.0,  1.0, 1.0,
    ], dtype=np.float32)

    VAO = glGenVertexArrays(1)
    VBO = glGenBuffers(1)
    glBindVertexArray(VAO)

    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, quad_vertices.nbytes, quad_vertices, GL_STATIC_DRAW)

    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 4 * quad_vertices.itemsize, ctypes.c_void_p(0))
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 4 * quad_vertices.itemsize, ctypes.c_void_p(2 * quad_vertices.itemsize))

    glBindVertexArray(0)
    return VAO, VBO

def load_bg_texture(path):
    surface = pygame.image.load(path).convert()
    img_data = pygame.image.tostring(surface, "RGB", True)
    width, height = surface.get_size()

    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glBindTexture(GL_TEXTURE_2D, 0)
    return tex_id

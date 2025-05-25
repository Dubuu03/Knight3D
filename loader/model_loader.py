import os
import numpy as np
from OpenGL.GL import *
import math
import glm
import ctypes

class SceneObject:
    def __init__(self, name, vertices, indices, textures):
        self.name = name
        self.vertex_count = len(indices)
        self.textures = textures
        
        # Animation properties
        self.animation_data = {
            'time': 0,
            'offset': glm.vec3(0.0, 0.0, 0.0),
            'rotation': glm.vec3(0.0, 0.0, 0.0),
            'scale': glm.vec3(1.0, 1.0, 1.0),
            'custom': {}  # Store custom animation parameters
        }

        self.VAO = glGenVertexArrays(1)
        self.VBO = glGenBuffers(1)
        self.EBO = glGenBuffers(1)

        vertex_data = np.array(vertices, dtype=np.float32)
        index_data = np.array(indices, dtype=np.uint32)

        glBindVertexArray(self.VAO)

        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, vertex_data.nbytes, vertex_data, GL_STATIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.EBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, index_data.nbytes, index_data, GL_STATIC_DRAW)

        # Positions
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * 4, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        # TexCoords
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * 4, ctypes.c_void_p(12))
        glEnableVertexAttribArray(1)

        glBindVertexArray(0)
        
    def update_animation(self, dt):
        self.animation_data['time'] += dt
        
    def get_model_matrix(self, base_model):
        # Apply object-specific transformations on top of the base model matrix
        model = glm.translate(base_model, self.animation_data['offset'])
        
        # Apply rotations if any
        if any(self.animation_data['rotation']):
            model = glm.rotate(model, self.animation_data['rotation'].x, glm.vec3(1, 0, 0))
            model = glm.rotate(model, self.animation_data['rotation'].y, glm.vec3(0, 1, 0))
            model = glm.rotate(model, self.animation_data['rotation'].z, glm.vec3(0, 0, 1))
            
        # Apply scaling if any
        if any(v != 1.0 for v in [self.animation_data['scale'].x, self.animation_data['scale'].y, self.animation_data['scale'].z]):
            model = glm.scale(model, self.animation_data['scale'])
            
        return model

    def draw(self, shader_program, texture_units, model_loc, model_matrix=None):
        # Set textures
        for tex_type, tex_id in self.textures.items():
            unit = texture_units.get(tex_type, 0)
            glActiveTexture(GL_TEXTURE0 + unit)
            glBindTexture(GL_TEXTURE_2D, tex_id)
            glUniform1i(glGetUniformLocation(shader_program, tex_type), unit)

        # Set model matrix (if provided)
        if model_matrix is not None:
            glUniformMatrix4fv(model_loc, 1, GL_FALSE, glm.value_ptr(model_matrix))
            
        # Draw the object
        glBindVertexArray(self.VAO)
        glDrawElements(GL_TRIANGLES, self.vertex_count, GL_UNSIGNED_INT, None)
        glBindVertexArray(0)
        
    def cleanup(self):
        if self.VAO:
            glDeleteVertexArrays(1, [self.VAO])
        if self.VBO:
            glDeleteBuffers(1, [self.VBO])
        if self.EBO:
            glDeleteBuffers(1, [self.EBO])
        for tex_id in self.textures.values():
            if tex_id:
                glDeleteTextures([tex_id])

def load_model_from_txt(folder_path, texture_loader):
    objects = []
    texture_types = ["BaseColor", "Normal", "Roughness", "Alpha", "Metallic", "Emissive"]
    texture_cache = {}  
    
    for filename in os.listdir(folder_path):
        if not filename.endswith(".txt"):
            continue

        with open(os.path.join(folder_path, filename), 'r') as f:
            lines = f.readlines()

        name = lines[0].split(":")[1].strip()
        textures = {}
        for i, ttype in enumerate(texture_types):
            tex_name = lines[i+1].split(":")[1].strip()
            if tex_name != "None":
                tex_path = os.path.join("texture", tex_name)
                if tex_path not in texture_cache:
                    texture_cache[tex_path] = texture_loader(tex_path)
                textures[ttype] = texture_cache[tex_path]

        v_start = lines.index("Vertices:\n") + 1
        i_start = lines.index("Indices:\n")
        vertices = [list(map(float, l.strip().split())) for l in lines[v_start:i_start]]
        indices = [int(i) for l in lines[i_start+1:] for i in l.strip().split()]
        flat_vertices = [coord for v in vertices for coord in v]

        obj = SceneObject(name, flat_vertices, indices, textures)
        objects.append(obj)

    return objects

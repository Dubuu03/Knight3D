from OpenGL.GL import *

vertex_shader = """
#version 330 core
layout (location = 0) in vec3 position;
layout (location = 1) in vec2 texCoord;
layout (location = 2) in vec3 normal;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

out vec2 TexCoord;
out vec3 FragPos;
out vec3 Normal;

void main() {
    FragPos = vec3(model * vec4(position, 1.0));
    Normal = mat3(transpose(inverse(model))) * normal;
    TexCoord = texCoord;
    gl_Position = projection * view * model * vec4(position, 1.0);
}
"""

fragment_shader = """
#version 330 core
in vec2 TexCoord;
in vec3 FragPos;
in vec3 Normal;

out vec4 FragColor;

uniform sampler2D texture_diffuse;
uniform vec3 lightPos;
uniform vec3 viewPos;
uniform vec3 emissiveColor;

void main() {
    vec3 texColor = texture(texture_diffuse, TexCoord).rgb;

    vec3 ambient = 0.3 * texColor;

    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(lightPos - FragPos);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * texColor;

    vec3 viewDir = normalize(viewPos - FragPos);
    vec3 reflectDir = reflect(-lightDir, norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32);
    vec3 specular = 0.5 * spec * vec3(1.0);

    vec3 finalColor = ambient + diffuse + specular + emissiveColor;
    FragColor = vec4(finalColor, 1.0);
}
"""

def create_shader_program():
    vs = glCreateShader(GL_VERTEX_SHADER)
    fs = glCreateShader(GL_FRAGMENT_SHADER)

    glShaderSource(vs, vertex_shader)
    glShaderSource(fs, fragment_shader)

    glCompileShader(vs)
    glCompileShader(fs)

    for shader, name in [(vs, "VERTEX"), (fs, "FRAGMENT")]:
        success = glGetShaderiv(shader, GL_COMPILE_STATUS)
        if not success:
            info_log = glGetShaderInfoLog(shader)
            print(f"ERROR::SHADER_COMPILATION_ERROR of type: {name}\n{info_log.decode()}")

    program = glCreateProgram()
    glAttachShader(program, vs)
    glAttachShader(program, fs)
    glLinkProgram(program)

    success = glGetProgramiv(program, GL_LINK_STATUS)
    if not success:
        info_log = glGetProgramInfoLog(program)
        print(f"ERROR::PROGRAM_LINKING_ERROR\n{info_log.decode()}")

    glDeleteShader(vs)
    glDeleteShader(fs)

    return program

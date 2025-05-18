import os
import numpy as np

# Function to read vertices, texture coordinates, and indices from OBJ
def read_obj(obj_path):
    vertices = []
    texcoords = []
    faces = []
    material_faces = {}  # Dictionary to store faces per material
    current_material = None

    with open(obj_path, 'r') as obj_file:
        lines = obj_file.readlines()

        for line in lines:
            parts = line.strip().split()

            if len(parts) == 0:
                continue

            # Vertex data (v x y z)
            if parts[0] == 'v':
                vertices.append([float(p) for p in parts[1:]])

            # Texture coordinates (vt u v)
            elif parts[0] == 'vt':
                texcoords.append([float(p) for p in parts[1:]])

            # Face data (f v1/vt1 v2/vt2 v3/vt3)
            elif parts[0] == 'f':
                face = []
                for p in parts[1:]:
                    v_idx, vt_idx = map(int, p.split('/')[:2])  # Get vertex and texture indices
                    face.append((v_idx - 1, vt_idx - 1))  # Convert to 0-based indexing
                if len(face) == 3:
                    if current_material not in material_faces:
                        material_faces[current_material] = []
                    material_faces[current_material].append(face)
                elif len(face) > 3:
                    for i in range(1, len(face) - 1):
                        material_faces[current_material].append([face[0], face[i], face[i + 1]])

            # Switch material
            elif parts[0] == 'usemtl':
                current_material = parts[1]

    return np.array(vertices), np.array(texcoords), material_faces

# Function to read the MTL file and extract texture data
def read_mtl(mtl_path):
    textures = {}
    current_material = None

    with open(mtl_path, 'r') as mtl_file:
        lines = mtl_file.readlines()

        for line in lines:
            parts = line.strip().split()

            if len(parts) == 0:
                continue

            if parts[0] == 'newmtl':
                current_material = parts[1]
            elif parts[0] == 'map_Kd':  # Diffuse texture
                texture = parts[1]
                textures[current_material] = {"diffuse": texture}
            elif parts[0] == 'map_Ns':  # Roughness texture
                if current_material in textures:
                    textures[current_material]["roughness"] = parts[1]
            elif parts[0] == 'map_refl':  # Metallic texture
                if current_material in textures:
                    textures[current_material]["metallic"] = parts[1]
            elif parts[0] == 'map_Bump':  # Normal map
                if current_material in textures:
                    textures[current_material]["normal"] = parts[1]

    return textures

# Save vertices, indices, and textures to txt
def save_to_txt(vertices, indices, texture_name, output_dir):
    # Sanitize texture_name to avoid file name issues (e.g., removing invalid characters)
    texture_name = texture_name.replace(".jpg", "").replace(".png", "").replace(".jpeg", "")  # Remove invalid file extensions
    texture_name = texture_name.replace("/", "_").replace("\\", "_")  # Replace slashes with underscores
    texture_name = texture_name.replace(":", "_").replace(" ", "_")  # Replace colon and spaces with underscores

    # Save vertices
    v_path = os.path.join(output_dir, f"{texture_name}_vertices.txt")
    try:
        np.savetxt(v_path, vertices, fmt="%.6f", delimiter=",")
        print(f"✅ Saved {texture_name}_vertices.txt")
    except PermissionError:
        print(f"❌ Permission denied while saving {texture_name}_vertices.txt. Please check the directory permissions.")

    # Save indices
    i_path = os.path.join(output_dir, f"{texture_name}_indices.txt")
    try:
        np.savetxt(i_path, indices, fmt="%d", delimiter=",")
        print(f"✅ Saved {texture_name}_indices.txt")
    except PermissionError:
        print(f"❌ Permission denied while saving {texture_name}_indices.txt. Please check the directory permissions.")

def main():
    obj_path = "models/knight.obj"  # Replace with your actual OBJ file path
    mtl_path = "models/knight.mtl"  # Replace with your actual MTL file path
    output_dir = "parts"  # Directory to save the extracted vertices and indices
    os.makedirs(output_dir, exist_ok=True)

    # Read OBJ file
    vertices, texcoords, material_faces = read_obj(obj_path)

    # Read MTL file for texture
    textures = read_mtl(mtl_path)

    # Process each material in the MTL and associate it with the OBJ data
    for material, faces in material_faces.items():
        if material in textures:
            texture_name = textures[material]["diffuse"]  # Extract texture name from MTL
        else:
            texture_name = "default_texture"  # Default texture if not found in MTL

        # Prepare vertices and indices for saving
        material_vertices = []
        material_indices = []
        index_map = {}
        index_counter = 0

        # Collect the vertices and indices for the material
        for face in faces:
            for v_idx, vt_idx in face:
                key = (v_idx, vt_idx)
                if key not in index_map:
                    index_map[key] = index_counter
                    material_vertices.append(vertices[v_idx] + texcoords[vt_idx])  # Append [x, y, z, u, v]
                    index_counter += 1
                material_indices.append(index_map[key])

        # Convert to numpy arrays for saving
        material_vertices_np = np.array(material_vertices, dtype=np.float32)
        material_indices_np = np.array(material_indices, dtype=np.uint32)

        # Save to TXT files
        save_to_txt(material_vertices_np, material_indices_np, texture_name, output_dir)

if __name__ == "__main__":
    main()

import os

def extract_obj_and_mtl(obj_path, mtl_path, out_dir="materials"):
    os.makedirs(out_dir, exist_ok=True)

    # Parse MTL file
    materials = parse_mtl(mtl_path)

    # Parse OBJ file
    with open(obj_path, "r") as f:
        lines = f.readlines()

    positions, texcoords = [], []
    current_material = None
    material_data = {}

    for line in lines:
        parts = line.strip().split()
        if not parts:
            continue

        if parts[0] == "v":
            positions.append(list(map(float, parts[1:4])))

        elif parts[0] == "vt":
            texcoords.append(list(map(float, parts[1:3])))

        elif parts[0] == "usemtl":
            current_material = parts[1]
            if current_material not in material_data:
                material_data[current_material] = {
                    "vertices": [],
                    "indices": [],
                    "map": {},
                    "counter": 0
                }

        elif parts[0] == "f" and current_material:
            face_vertices = parts[1:]
            if len(face_vertices) < 3:
                print(f"Skipping invalid face: {line.strip()}")
                continue  # Invalid face, skip

            for i in range(1, len(face_vertices) - 1):
                tri = [face_vertices[0], face_vertices[i], face_vertices[i + 1]]
                indices = []
                for ref in tri:
                    refs = ref.split("/")
                    if len(refs) < 2:
                        print(f"Skipping malformed face vertex: {ref}")
                        continue  # Malformed face vertex

                    try:
                        v_idx = int(refs[0]) - 1
                        vt_idx = int(refs[1]) - 1
                    except ValueError:
                        print(f"Skipping non-integer index: {ref}")
                        continue

                    key = (v_idx, vt_idx)
                    mat = material_data[current_material]
                    if key not in mat["map"]:
                        try:
                            vertex = positions[v_idx] + texcoords[vt_idx]
                        except IndexError:
                            print(f"Index error: v={v_idx}, vt={vt_idx}")
                            continue
                        mat["vertices"].append(vertex)
                        mat["map"][key] = mat["counter"]
                        mat["counter"] += 1
                    indices.append(mat["map"][key])
                if len(indices) == 3:
                    material_data[current_material]["indices"].append(indices)

    # Save output for each material
    for name, data in material_data.items():
        mat = materials.get(name, {
            "basecolor": None,
            "normal": None,
            "roughness": None,
            "metallic": None,
            "alpha": "1.0",
            "emissive": None
        })
        write_material_txt(name, mat, data["vertices"], data["indices"], out_dir)

def parse_mtl(mtl_path):
    materials = {}
    with open(mtl_path, "r") as f:
        lines = f.readlines()

    current = None
    for line in lines:
        line = line.strip()
        if line.startswith("newmtl"):
            current = line.split()[1]
            materials[current] = {
                "basecolor": None,
                "normal": None,
                "roughness": None,
                "metallic": None,
                "alpha": "1.0",
                "emissive": None
            }
        elif current:
            if "map_Kd" in line:
                materials[current]["basecolor"] = os.path.basename(line.split()[-1])
            elif "map_Bump" in line or "bump" in line:
                materials[current]["normal"] = os.path.basename(line.split()[-1])
            elif "map_Ns" in line:
                materials[current]["roughness"] = os.path.basename(line.split()[-1])
            elif "map_refl" in line:
                materials[current]["metallic"] = os.path.basename(line.split()[-1])
            elif line.startswith("d "):
                materials[current]["alpha"] = line.split()[1]
    return materials

def write_material_txt(name, mat_data, vertices, indices, out_dir):
    out_path = os.path.join(out_dir, f"{name}.txt")
    with open(out_path, "w") as f:
        f.write(f"Material: {name}\n")
        f.write(f"BaseColor: {mat_data['basecolor'] or 'None'}\n")
        f.write(f"Normal: {mat_data['normal'] or 'None'}\n")
        f.write(f"Roughness: {mat_data['roughness'] or 'None'}\n")
        f.write(f"Metallic: {mat_data['metallic'] or 'None'}\n")
        f.write(f"Alpha: {mat_data['alpha'] or '1.0'}\n")
        f.write(f"Emissive: {mat_data['emissive'] or 'None'}\n")

        f.write("Vertices:\n")
        for v in vertices:
            f.write(" ".join(f"{x:.6f}" for x in v) + "\n")

        f.write("Indices:\n")
        for tri in indices:
            f.write(" ".join(str(i) for i in tri) + "\n")

    print(f"Saved: {out_path}")

# === Run the script ===
if __name__ == "__main__":
    # CHANGE THESE to your actual filenames
    obj_path = "models/bone_dragon.obj"
    mtl_path = "models/bone_dragon.obj"
    extract_obj_and_mtl(obj_path, mtl_path, out_dir="dragon/parts")
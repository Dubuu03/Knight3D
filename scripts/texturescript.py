import os
import shutil

# 🔧 CONFIGURATION — Update this before running
MTL_PATH = "models/knight.mtl"  # Path to your MTL file
SOURCE_TEXTURE_DIR = r"D:/BSCS/CS -3A 2nd Sem/CS Electives/Finals/stronghold - Copy/textures"
DEST_TEXTURE_DIR = "./texturess"
os.makedirs(DEST_TEXTURE_DIR, exist_ok=True)

# Extract all unique texture base names from the MTL file
def extract_texture_names_from_mtl(mtl_path):
    texture_names = set()
    with open(mtl_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith("map_"):
                parts = line.split()
                texture_path = parts[-1]
                clean_name = os.path.splitext(os.path.basename(texture_path.split("@")[0]))[0]
                texture_names.add(clean_name)
    return sorted(texture_names)

# Tries to find matching file with common extensions
def find_texture_file(base_name, source_folder):
    extensions = [".png", ".jpg", ".jpeg"]
    for ext in extensions:
        full_path = os.path.join(source_folder, base_name + ext)
        if os.path.exists(full_path):
            return full_path
    return None

# Main logic
def main():
    print("📦 Extracting texture references from:", MTL_PATH)
    textures_needed = extract_texture_names_from_mtl(MTL_PATH)
    print(f"🧵 Found {len(textures_needed)} texture base names.\n")

    for tex_name in textures_needed:
        src = find_texture_file(tex_name, SOURCE_TEXTURE_DIR)
        if src:
            dst = os.path.join(DEST_TEXTURE_DIR, os.path.basename(src))
            shutil.copy2(src, dst)
            print(f"✅ Copied: {tex_name} → {os.path.basename(dst)}")
        else:
            print(f"❌ Missing: {tex_name} (checked .png/.jpg/.jpeg)")

    print(f"\n🎉 Done! Textures saved in: {DEST_TEXTURE_DIR}")

if __name__ == "__main__":
    main()

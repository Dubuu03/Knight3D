
import os
import shutil

# Source folder where original textures are located
SOURCE_DIR = r"D:/BSCS/CS -3A 2nd Sem/CS Electives/Finals/stronghold - Copy/textures"
# Destination folder where cleaned textures will be saved
DEST_DIR = r"./texture"
os.makedirs(DEST_DIR, exist_ok=True)

# Mapping from old filenames to clean names
RENAME_MAP = {
    # bottom armor
    "bottom_armor_mat_BaseColor.jpeg": "bottom_armor_mat_BaseColor.jpeg",
    "bottom_armor_mat_Normal.png": "bottom_armor_mat_Normal.png",
    "bottom_armor_mat_Metallic-bottom_armor_mat_Roughness@channel.png": "bottom_armor_mat_Roughness.png",  # manual split needed

    # center armor
    "center_armor_mat_BaseColor.jpeg": "center_armor_mat_BaseColor.jpeg",
    "center_armor_mat_Normal.png": "center_armor_mat_Normal.png",
    "center_armor_mat_Metallic-center_armor_mat_Roughness@channel.png": "center_armor_mat_Roughness.png",  # manual split needed

    # cloak
    "cloak_mat_BaseColor-cloak_mat_Alpha.png": "cloak_mat_BaseColor.png",  # also contains alpha
    "cloak_mat_Normal.png": "cloak_mat_Normal.png",
    "cloak_mat_Roughness@channels=G.png": "cloak_mat_Roughness.png",

    # details
    "details_mat_BaseColor.jpeg": "details_mat_BaseColor.jpeg",
    "details_mat_Normal.png": "details_mat_Normal.png",
    "details_mat_Metallic-details_mat_Roughness@channels=B.png": "details_mat_Metallic.png",
    "details_mat_Metallic-details_mat_Roughness@channels=G.png": "details_mat_Roughness.png",

    # roses
    "roses_mat_BaseColor.jpeg": "roses_mat_BaseColor.jpeg",
    "roses_mat_Normal.png": "roses_mat_Normal.png",
    "roses_mat_Roughness@channels=G.png": "roses_mat_Roughness.png",

    # sword
    "sword_mat_BaseColor.jpeg": "sword_mat_BaseColor.jpeg",
    "sword_mat_Normal.png": "sword_mat_Normal.png",
    "sword_mat_Metallic-sword_mat_Roughness@channels=B.png": "sword_mat_Metallic.png",
    "sword_mat_Metallic-sword_mat_Roughness@channels=G.png": "sword_mat_Roughness.png",

    # top armor
    "top_armor_mat_BaseColor.jpeg": "top_armor_mat_BaseColor.jpeg",
    "top_armor_mat_Normal.png": "top_armor_mat_Normal.png",
    "top_armor_mat_Emissive.jpeg": "top_armor_mat_Emissive.jpeg",
    "top_armor_mat_Metallic-top_armor_mat_Roughness@channels=B.png": "top_armor_mat_Metallic.png",
    "top_armor_mat_Metallic-top_armor_mat_Roughness@channels=G.png": "top_armor_mat_Roughness.png",
}

# Copy and rename files
for original_name, new_name in RENAME_MAP.items():
    src_path = os.path.join(SOURCE_DIR, original_name)
    dst_path = os.path.join(DEST_DIR, new_name)

    if os.path.exists(src_path):
        shutil.copy2(src_path, dst_path)
        print(f"Copied: {original_name} → {new_name}")
    else:
        print(f"Missing: {original_name}")

import glm
import math
import json

def load_animation_data():
    """Load animation data from JSON file"""
    try:
        with open('data/animation_data.json', 'r') as f:
            data = json.load(f)
        print("Animation data loaded from data/animation_data.json")
        return data
    except Exception as e:
        print(f"Error loading animation data: {e}")
        return {}

def initialize_animations(objects):
    animation_json = load_animation_data()
    for obj in objects:
        name = getattr(obj, 'name', '').lower()
        obj.animation_data['offset'] = glm.vec3(0.0)
        obj.animation_data['rotation'] = glm.vec3(0.0)
        obj.animation_data['scale'] = glm.vec3(1.0)

        if name in animation_json:
            obj.animation_data['custom'] = animation_json[name]
    return animation_json

def update_animations(objects, dt, time):
    for obj in objects:
        obj.update_animation(dt)
        name = getattr(obj, 'name', '').lower()

        if 'rose' in name and 'custom' in obj.animation_data:
            custom = obj.animation_data['custom']
            bob_y = custom['bob_amplitude'] * math.sin(time * custom['bob_frequency'] + custom['bob_phase'])
            obj.animation_data['offset'].y = bob_y
            obj.animation_data['rotation'].y = math.sin(time * 0.5) * 0.02

        elif 'cloak' in name and 'custom' in obj.animation_data:
            custom = obj.animation_data['custom']
            
            # Time with slight random offset for natural difference
            time_offset = time + custom.get('random_offset', 0)
            
            # Gentle vertical sway
            wave_y = custom['primary_amplitude'] * math.sin(time_offset * custom['primary_frequency'])
            
            # Gentle lateral motion with phase shift
            wave_x = custom['secondary_amplitude'] * math.sin(time_offset * custom['secondary_frequency'] + math.pi / 2)
            
            # Small Z depth flutter (trailing)
            wave_z = (custom['secondary_amplitude'] * 0.5) * math.sin(time_offset * custom['secondary_frequency'] * 0.6)
            
            min_y = -0.03  # Adjust this to control how low it can go
            clamped_y = max(wave_y * 0.3, min_y)
            
            # Apply soft translation offsets
            obj.animation_data['offset'].x = wave_x * 0.2
            obj.animation_data['offset'].y = clamped_y
            obj.animation_data['offset'].z = wave_z * 0.1
            
            # Apply natural smooth rotations (like the cloak tilting back and forth)
            obj.animation_data['rotation'].x = wave_y * 0.1
            obj.animation_data['rotation'].y = wave_z * 0.08
            obj.animation_data['rotation'].z = wave_x * 0.1

            # Subtle breathing/puffing scaling (less intense)
            flutter = custom['flutter'] * math.sin(time_offset * 1.5)
            obj.animation_data['scale'].x = 1.0 + flutter * 0.2
            obj.animation_data['scale'].y = 1.0 + flutter * 0.3
            obj.animation_data['scale'].z = 1.0 - flutter * 0.1

def load_camera_presets():
    """Load camera preset data from JSON file"""
    try:
        with open('data/camera_presets.json', 'r') as f:
            presets = json.load(f)
        print("Camera presets loaded from data/camera_presets.json")
        return presets
    except Exception as e:
        print(f"Error loading camera presets: {e}")
        # Return default presets if file can't be loaded
        return [
            {"name": "Full View", "rot_x": 0.0, "rot_y": 0.0, "zoom": 6.0, "focus_y": 1.0},
            {"name": "Sword Focus", "rot_x": -14.4, "rot_y": -0.3, "zoom": 3.5, "focus_y": 1.0},
            {"name": "Head/Eyes Focus", "rot_x": 20.0, "rot_y": 0.0, "zoom": 3.0, "focus_y": 2.0},
            {"name": "Cloak Focus", "rot_x": 5.0, "rot_y": 135.0, "zoom": 4.0, "focus_y": 1.5},
            {"name": "Roses Focus", "rot_x": -15.0, "rot_y": 30.0, "zoom": 4.0, "focus_y": 0.7}
        ]

import os
from PIL import Image, ImageDraw, ImageFont

def create_logo(output_path):
    # Dimensions (800x800 for high resolution)
    width, height = 800, 800
    
    # Pure deep black background (#000000)
    bg_color = (0, 0, 0, 255)
    img = Image.new("RGBA", (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Premium Corporate Color Palette
    primary_cyan = (6, 182, 212, 255)    # Cyber Cyan (#06B6D4)
    electric_blue = (59, 130, 246, 255)  # Electric Royal Blue (#3B82F6)
    white = (255, 255, 255, 255)          # Clean Pure White
    muted_grey = (148, 163, 184, 80)      # Translucent Slate Grey (#94A3B8, alpha 80)
    silver_border = (71, 85, 105, 120)    # Slate Border (#475569, alpha 120)
    
    # Center coordinates
    cx, cy = 400, 310
    
    # 1. Draw Outer Hexagonal Tech Frame (Highly Professional Corporate Seal Look)
    # A regular hexagon layout
    hex_radius = 240
    import math
    hex_points = []
    for i in range(6):
        angle_rad = math.radians(60 * i - 30) # Rotated by 30deg to make top/bottom flat
        hx = cx + hex_radius * math.cos(angle_rad)
        hy = cy + hex_radius * math.sin(angle_rad)
        hex_points.append((hx, hy))
        
    # Draw Hexagonal outline
    draw.polygon(hex_points, outline=silver_border, width=3)
    
    # 2. Draw "Omni-Chaos" Connection Network (Order out of Chaos lines)
    # Define connection nodes placed on key geometric intersections
    nodes = [
        (400, 90),   # Top Hexagon corner
        (400, 530),  # Bottom Hexagon corner
        (200, 310),  # Left
        (600, 310),  # Right
        (300, 140),  # Top-Left
        (500, 140),  # Top-Right
        (300, 480),  # Bottom-Left
        (500, 480),  # Bottom-Right
    ]
    
    # Draw grid connector lines radiating from the central lens
    for node in nodes:
        draw.line([node, (cx, cy)], fill=muted_grey, width=2)
        
    # Draw secondary orbital lines between nodes
    draw.line([nodes[4], nodes[5]], fill=muted_grey, width=1)
    draw.line([nodes[6], nodes[7]], fill=muted_grey, width=1)
    draw.line([nodes[2], nodes[4]], fill=muted_grey, width=1)
    draw.line([nodes[3], nodes[5]], fill=muted_grey, width=1)
    draw.line([nodes[2], nodes[6]], fill=muted_grey, width=1)
    draw.line([nodes[3], nodes[7]], fill=muted_grey, width=1)
    
    # Draw connection terminal circles
    for x, y in nodes:
        draw.ellipse([x-6, y-6, x+6, y+6], fill=electric_blue, outline=primary_cyan, width=2)
        
    # 3. Draw Concentric Sensor Rings (Focal lens design for surveillance/vignette feel)
    draw.ellipse([cx - 130, cy - 130, cx + 130, cy + 130], outline=silver_border, width=1)
    draw.ellipse([cx - 100, cy - 100, cx + 100, cy + 100], outline=muted_grey, width=1)
    
    # 4. Draw Vigilant Eye of Argus
    eye_w = 260
    eye_h = 140
    # Overlapping arcs to form a sleek modern eye vector
    draw.arc([cx - eye_w//2, cy - eye_h, cx + eye_w//2, cy + eye_h//2], start=200, end=340, fill=primary_cyan, width=4)
    draw.arc([cx - eye_w//2, cy - eye_h//2, cx + eye_w//2, cy + eye_h], start=20, end=160, fill=primary_cyan, width=4)
    
    # Iris (Glowing Cyber Core)
    iris_r = 55
    draw.ellipse([cx - iris_r, cy - iris_r, cx + iris_r, cy + iris_r], fill=electric_blue, outline=primary_cyan, width=3)
    
    # Pupil (Pure Black Centre)
    pupil_r = 25
    draw.ellipse([cx - pupil_r, cy - pupil_r, cx + pupil_r, cy + pupil_r], fill=(0, 0, 0, 255), outline=primary_cyan, width=1)
    
    # Inner light reflection node (White offset dot for realism/depth)
    draw.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=white)
    
    # 5. Professional Typography
    # Font path resolution
    font_path = "C:\\Windows\\Fonts\\segoeui.ttf"
    font_bold_path = "C:\\Windows\\Fonts\\segoeuib.ttf"
    
    if not os.path.exists(font_path):
        font_path = "C:\\Windows\\Fonts\\arial.ttf"
    if not os.path.exists(font_bold_path):
        font_bold_path = "C:\\Windows\\Fonts\\arialbd.ttf"
        
    try:
        title_font = ImageFont.truetype(font_bold_path, 48)
        subtitle_font = ImageFont.truetype(font_path, 22)
    except IOError:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        
    # Draw "ARGUS" with tracking
    title_text = "A R G U S"
    t_w = draw.textlength(title_text, font=title_font)
    draw.text((400 - t_w//2, 600), title_text, fill=white, font=title_font)
    
    # Draw "OMNICHAOS" with tracking
    subtitle_text = "O M N I C H A O S"
    s_w = draw.textlength(subtitle_text, font=subtitle_font)
    draw.text((400 - s_w//2, 670), subtitle_text, fill=primary_cyan, font=subtitle_font)
    
    # Save Image
    img.save(output_path, "PNG")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(base_dir, "argus_omnichaos_logo.png")
    create_logo(logo_path)
    print(f"Professional Deep Black logo drawn successfully at: {logo_path}")

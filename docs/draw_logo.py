import os
from PIL import Image, ImageDraw, ImageFont

def create_logo(output_path):
    # Dimensions
    width, height = 800, 800
    
    # Create background image: Deep Slate/Navy (#0B132B)
    bg_color = (11, 19, 43, 255)
    img = Image.new("RGBA", (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Clean vector colors
    cyan = (6, 182, 212, 255)      # Cyber Cyan (#06B6D4)
    blue = (59, 130, 246, 255)      # Royal Blue (#3B82F6)
    white = (248, 250, 252, 255)    # Clean Slate White (#F8FAFC)
    grey = (100, 116, 139, 100)     # Translucent Slate Grey (#64748B)
    dark_blue = (15, 23, 42, 255)   # Slate-900 (#0F172A)
    
    # Center coordinates
    cx, cy = 400, 320
    
    # 1. Draw "Chaos to Order" Network (Symmetrical, precise geometric lines)
    # Radiating nodes and connection segments
    nodes = [
        (400, 120),  # Top
        (400, 520),  # Bottom
        (180, 320),  # Left
        (620, 320),  # Right
        (245, 165),  # Top-Left
        (555, 165),  # Top-Right
        (245, 475),  # Bottom-Left
        (555, 475),  # Bottom-Right
    ]
    
    # Draw connections to central eye and between nodes
    for node in nodes:
        draw.line([node, (cx, cy)], fill=grey, width=2)
        
    draw.line([nodes[0], nodes[4], nodes[2], nodes[6], nodes[1], nodes[7], nodes[3], nodes[5], nodes[0]], fill=grey, width=2)
    
    # Draw node circles
    for x, y in nodes:
        draw.ellipse([x-8, y-8, x+8, y+8], fill=blue, outline=cyan, width=2)
        
    # 2. Draw Vigilant Eye of Argus (Geometric Arcs)
    # Outer Eye boundary (2 overlapping arcs forming a lens)
    eye_width = 320
    eye_height = 180
    
    # Drawing bounding boxes for the top and bottom arcs
    draw.arc([cx - eye_width//2, cy - eye_height, cx + eye_width//2, cy + eye_height//2], start=190, end=350, fill=cyan, width=5)
    draw.arc([cx - eye_width//2, cy - eye_height//2, cx + eye_width//2, cy + eye_height], start=10, end=170, fill=cyan, width=5)
    
    # Draw Iris (Vibrant Cyber Blue Circle)
    iris_r = 75
    draw.ellipse([cx - iris_r, cy - iris_r, cx + iris_r, cy + iris_r], fill=blue, outline=cyan, width=4)
    
    # Draw Pupil (Dark Core)
    pupil_r = 38
    draw.ellipse([cx - pupil_r, cy - pupil_r, cx + pupil_r, cy + pupil_r], fill=dark_blue, outline=cyan, width=2)
    
    # Draw Inner core glow / core node (White small circle)
    glow_r = 10
    draw.ellipse([cx - glow_r, cy - glow_r, cx + glow_r, cy + glow_r], fill=white)
    
    # 3. Text Section
    # Load Segoe UI Bold or Arial Bold for a crisp corporate font style
    font_path = "C:\\Windows\\Fonts\\segoeui.ttf"
    font_bold_path = "C:\\Windows\\Fonts\\segoeuib.ttf"
    
    # Fallback to standard if fonts don't exist
    if not os.path.exists(font_path):
        font_path = "C:\\Windows\\Fonts\\arial.ttf"
    if not os.path.exists(font_bold_path):
        font_bold_path = "C:\\Windows\\Fonts\\arialbd.ttf"
        
    try:
        title_font = ImageFont.truetype(font_bold_path, 46)
        subtitle_font = ImageFont.truetype(font_path, 22)
    except IOError:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        
    # Draw text: "ARGUS"
    title_text = "A R G U S"
    t_w = draw.textlength(title_text, font=title_font)
    draw.text((400 - t_w//2, 600), title_text, fill=white, font=title_font)
    
    # Draw text: "OMNICHAOS"
    subtitle_text = "O M N I C H A O S"
    s_w = draw.textlength(subtitle_text, font=subtitle_font)
    draw.text((400 - s_w//2, 670), subtitle_text, fill=cyan, font=subtitle_font)
    
    # Save Image
    img.save(output_path, "PNG")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(base_dir, "argus_omnichaos_logo.png")
    create_logo(logo_path)
    print(f"Professional logo drawn successfully at: {logo_path}")

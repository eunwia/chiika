"""
icons.py - Custom Vector-Style Icon Generator for Chiikawa Study Planner
Generates crisp, antialiased monochrome / accent icons using Pillow supersampling.
Replaces all generic emojis with a consistent, modern icon set.
"""

from typing import Dict, Tuple, Optional
from PIL import Image, ImageDraw
import customtkinter as ctk

_icon_cache: Dict[Tuple[str, int, str], ctk.CTkImage] = {}

def clear_icon_cache():
    """Clear in-memory CTkImage cache when Tk instance is recreated."""
    _icon_cache.clear()

def get_icon(name: str, size: int = 18, color: str = "#4A3E4D") -> ctk.CTkImage:
    """
    Returns a cached CTkImage for the given icon name, pixel size, and hex color.
    Uses 4x supersampling for ultra-crisp antialiasing on high-DPI displays.
    """
    cache_key = (name, size, color)
    if cache_key in _icon_cache:
        return _icon_cache[cache_key]

    scale = 4
    canvas_size = size * scale
    img = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Parse hex color
    c = color.lstrip("#")
    if len(c) == 6:
        rgb = tuple(int(c[i:i+2], 16) for i in (0, 2, 4)) + (255,)
    else:
        rgb = (100, 100, 100, 255)

    stroke = max(1.8 * scale, 2.0)

    # Helper functions
    def line(x1, y1, x2, y2, w=stroke):
        draw.line([x1 * scale, y1 * scale, x2 * scale, y2 * scale], fill=rgb, width=int(w))

    def rect(x1, y1, x2, y2, r=2.0):
        draw.rounded_rectangle([x1 * scale, y1 * scale, x2 * scale, y2 * scale], radius=r * scale, outline=rgb, width=int(stroke))

    def filled_rect(x1, y1, x2, y2, r=1.5):
        draw.rounded_rectangle([x1 * scale, y1 * scale, x2 * scale, y2 * scale], radius=r * scale, fill=rgb)

    def circle(cx, cy, radius, fill=False):
        bbox = [(cx - radius) * scale, (cy - radius) * scale, (cx + radius) * scale, (cy + radius) * scale]
        if fill:
            draw.ellipse(bbox, fill=rgb)
        else:
            draw.ellipse(bbox, outline=rgb, width=int(stroke))

    # Icon definitions (normalized to 20x20 grid)
    if name == "dashboard":
        rect(2.5, 2.5, 9, 9, r=1.5)
        rect(11, 2.5, 17.5, 9, r=1.5)
        rect(2.5, 11, 9, 17.5, r=1.5)
        rect(11, 11, 17.5, 17.5, r=1.5)

    elif name == "tasks":
        rect(2.5, 2.5, 17.5, 17.5, r=2.5)
        line(6, 7, 8, 9)
        line(8, 9, 13, 5.5)
        line(6, 12, 14, 12)
        line(6, 15, 11, 15)

    elif name == "corkboard":
        line(10, 3, 10, 11, w=stroke*1.2)
        line(6, 11, 14, 11)
        line(8, 3, 12, 3)
        line(10, 11, 10, 18, w=stroke)
        circle(10, 6, 2.5, fill=True)

    elif name == "calendar":
        rect(2.5, 4, 17.5, 18, r=2)
        line(2.5, 8, 17.5, 8)
        line(6, 2, 6, 5.5)
        line(14, 2, 14, 5.5)
        circle(7, 12, 1, fill=True)
        circle(10, 12, 1, fill=True)
        circle(13, 12, 1, fill=True)
        circle(7, 15, 1, fill=True)
        circle(10, 15, 1, fill=True)

    elif name == "study":
        line(10, 5, 10, 17)
        line(2.5, 5, 10, 5)
        line(2.5, 5, 2.5, 16)
        line(2.5, 16, 10, 16)
        line(10, 5, 17.5, 5)
        line(17.5, 5, 17.5, 16)
        line(10, 16, 17.5, 16)
        line(5, 8, 8, 8)
        line(12, 8, 15, 8)

    elif name == "timer":
        circle(10, 11, 6.5)
        line(10, 7.5, 10, 11)
        line(10, 11, 13, 11)
        line(8, 2, 12, 2)
        line(10, 2, 10, 4.5)

    elif name == "habits":
        circle(10, 9, 4)
        line(10, 2, 10, 4)
        line(10, 14, 10, 16)
        line(3, 9, 5, 9)
        line(15, 9, 17, 9)

    elif name == "notes":
        rect(3.5, 2.5, 16.5, 17.5, r=2)
        line(7, 6.5, 13, 6.5)
        line(7, 10, 13, 10)
        line(7, 13.5, 11, 13.5)

    elif name == "progress":
        line(2.5, 17.5, 17.5, 17.5)
        filled_rect(4.5, 11, 7, 16.5, r=1)
        filled_rect(8.5, 6, 11, 16.5, r=1)
        filled_rect(12.5, 8.5, 15, 16.5, r=1)

    elif name == "search":
        circle(8.5, 8.5, 4.8)
        line(12.2, 12.2, 17, 17, w=stroke*1.2)

    elif name == "settings":
        circle(10, 10, 3)
        circle(10, 10, 6.5)
        for angle_deg in [0, 45, 90, 135, 180, 225, 270, 315]:
            import math
            rad = math.radians(angle_deg)
            x1 = 10 + 6.5 * math.cos(rad)
            y1 = 10 + 6.5 * math.sin(rad)
            x2 = 10 + 8.5 * math.cos(rad)
            y2 = 10 + 8.5 * math.sin(rad)
            line(x1, y1, x2, y2, w=stroke*1.1)

    elif name == "plus":
        line(10, 4, 10, 16, w=stroke*1.1)
        line(4, 10, 16, 10, w=stroke*1.1)

    elif name == "edit":
        line(4, 16, 4, 13)
        line(4, 13, 13, 4)
        line(13, 4, 16, 7)
        line(16, 7, 7, 16)
        line(7, 16, 4, 16)
        line(11.5, 5.5, 14.5, 8.5)

    elif name == "trash":
        line(4, 5.5, 16, 5.5)
        line(8, 3, 12, 3)
        line(5.5, 5.5, 6.5, 17)
        line(6.5, 17, 13.5, 17)
        line(13.5, 17, 14.5, 5.5)
        line(8.5, 8, 8.5, 14.5)
        line(11.5, 8, 11.5, 14.5)

    elif name == "check":
        line(4, 10.5, 8.5, 15, w=stroke*1.2)
        line(8.5, 15, 16, 5.5, w=stroke*1.2)

    elif name == "x":
        line(5, 5, 15, 15, w=stroke*1.1)
        line(15, 5, 5, 15, w=stroke*1.1)

    elif name == "chevron_left":
        line(12.5, 4.5, 7, 10, w=stroke*1.1)
        line(7, 10, 12.5, 15.5, w=stroke*1.1)

    elif name == "chevron_right":
        line(7.5, 4.5, 13, 10, w=stroke*1.1)
        line(13, 10, 7.5, 15.5, w=stroke*1.1)

    elif name == "play":
        draw.polygon([(6 * scale, 4 * scale), (16 * scale, 10 * scale), (6 * scale, 16 * scale)], fill=rgb)

    elif name == "pause":
        filled_rect(5.5, 4, 8.5, 16, r=1)
        filled_rect(11.5, 4, 14.5, 16, r=1)

    elif name == "rotate_ccw":
        circle(10, 10.5, 5.5)
        draw.rectangle([10 * scale, 3 * scale, 18 * scale, 10 * scale], fill=(0, 0, 0, 0))
        draw.polygon([(10 * scale, 3 * scale), (10 * scale, 7 * scale), (6 * scale, 5 * scale)], fill=rgb)

    elif name == "skip_forward":
        draw.polygon([(4 * scale, 5 * scale), (11 * scale, 10 * scale), (4 * scale, 15 * scale)], fill=rgb)
        line(14, 5, 14, 15, w=stroke*1.2)

    elif name == "pin":
        line(10, 3, 10, 12, w=stroke*1.2)
        circle(10, 6, 3, fill=True)
        line(10, 12, 10, 17, w=stroke)

    elif name == "clock":
        circle(10, 10, 7)
        line(10, 6, 10, 10)
        line(10, 10, 13.5, 10)

    elif name == "sun":
        circle(10, 10, 4)
        for angle_deg in [0, 45, 90, 135, 180, 225, 270, 315]:
            import math
            rad = math.radians(angle_deg)
            x1 = 10 + 6 * math.cos(rad)
            y1 = 10 + 6 * math.sin(rad)
            x2 = 10 + 8 * math.cos(rad)
            y2 = 10 + 8 * math.sin(rad)
            line(x1, y1, x2, y2, w=stroke*1.0)

    elif name == "moon":
        circle(10, 10, 6.5)
        # cut out inner arc for crescent effect
        draw.ellipse([(6.5) * scale, (3.5) * scale, (17.5) * scale, (14.5) * scale], fill=(0, 0, 0, 0))

    else:
        circle(10, 10, 3, fill=True)

    scaled_img = img.resize((size, size), Image.Resampling.LANCZOS)
    ctk_img = ctk.CTkImage(light_image=scaled_img, dark_image=scaled_img, size=(size, size))
    _icon_cache[cache_key] = ctk_img
    return ctk_img

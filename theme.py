"""
theme.py - Modern Cozy Productivity Aesthetic for Chiikawa Study Planner
Features centralized pastel pink/cream palette, clean Segoe UI typography hierarchy,
radii, spacing, and complete light/dark theme support.
"""

from typing import Dict, Any, Tuple


class Theme:
    MODE = "light"  # "light" or "dark"

    # Cozy Day (Pastel Pink / Cream Light Palette)
    LIGHT = {
        "bg_app": "#FBF9F5",            # Warm alabaster cream canvas
        "bg_sidebar": "#F4EFEA",        # Soft warm neutral sidebar
        "bg_sidebar_active": "#EBDED6",  # Clear active-tab highlight pill
        "bg_sidebar_hover": "#EEE8E1",  # Subtle nav hover state
        
        "bg_card": "#FFFFFF",           # Elevated pure white card surface
        "bg_card_secondary": "#F8F4EE", # Soft grouped surface / secondary button
        "bg_card_hover": "#FCFAF7",     # Subtle card hover depth

        "border": "#EBE3D8",            # Soft warm border
        "border_subtle": "#F2ECE3",     # Hairline divider
        "border_focus": "#FF7597",      # Focus glow pink border

        # Refined Chiikawa Accents
        "accent_pink": "#FF7597",        # Vibrant cheerful Chiikawa rose pink (primary)
        "accent_pink_hover": "#E65C80",  # Darker pressed/hover pink
        "accent_pink_subtle": "#FFF0F4", # Soft pink tint badge background
        "accent_blue": "#5B9BD5",        # Crisp serene slate blue
        "accent_blue_hover": "#4785C0",
        "accent_yellow": "#F5A623",      # Warm golden honey amber
        "accent_yellow_hover": "#DF9215",
        "accent_lavender": "#9A7BD6",    # Dusty cozy lavender
        "accent_lavender_hover": "#8665C5",
        "accent_mint": "#42B883",        # Fresh matcha green
        "accent_mint_hover": "#339D6D",

        # Priority Badges
        "priority_high_bg": "#FFEBF0",
        "priority_high_fg": "#E03A62",
        "priority_med_bg": "#FFF4E5",
        "priority_med_fg": "#C97A19",
        "priority_low_bg": "#EDF9F2",
        "priority_low_fg": "#268C5E",

        # Text Hierarchy (High Contrast & Clear Readability)
        "text_primary": "#2D2630",      # Deep charcoal plum
        "text_secondary": "#6E6472",    # Clean readable secondary gray
        "text_muted": "#A298A6",        # Placeholder / inactive text
        "text_on_accent": "#FFFFFF",

        # Form Inputs
        "input_bg": "#FFFFFF",
        "input_border": "#DCD3C7",
        "input_border_focus": "#FF7597",

        # Corkboard
        "cork_bg": "#EFE6DA",
        "cork_dot": "#E2D8C9",
    }

    # Cozy Night (Deep Twilight Dark Palette)
    DARK = {
        "bg_app": "#16131D",            # Deep twilight canvas
        "bg_sidebar": "#1E1A27",        # Dark eggplant sidebar
        "bg_sidebar_active": "#352C46",  # Active nav pill surface
        "bg_sidebar_hover": "#2B2438",

        "bg_card": "#241F31",           # Elevated dark card
        "bg_card_secondary": "#1C1827", # Subtle grouped surface
        "bg_card_hover": "#2B253A",

        "border": "#372F47",            # Refined hairline border
        "border_subtle": "#2C253B",
        "border_focus": "#FF85A5",

        # Refined Accents in Dark Mode
        "accent_pink": "#FF85A5",
        "accent_pink_hover": "#EB6E8F",
        "accent_pink_subtle": "#3D1F2B",
        "accent_blue": "#6AA3DE",
        "accent_blue_hover": "#548FC9",
        "accent_yellow": "#F6B34A",
        "accent_yellow_hover": "#E19E33",
        "accent_lavender": "#A78BE3",
        "accent_lavender_hover": "#9374D4",
        "accent_mint": "#53C492",
        "accent_mint_hover": "#40AE7D",

        # Priority Badges
        "priority_high_bg": "#421C2B",
        "priority_high_fg": "#FFA3BA",
        "priority_med_bg": "#422E1A",
        "priority_med_fg": "#FFCD87",
        "priority_low_bg": "#1A3B2E",
        "priority_low_fg": "#8CE5BC",

        # Text Hierarchy
        "text_primary": "#F7F3FA",
        "text_secondary": "#B2A7B8",
        "text_muted": "#7B7183",
        "text_on_accent": "#FFFFFF",

        # Form Inputs
        "input_bg": "#1C1827",
        "input_border": "#3D354F",
        "input_border_focus": "#FF85A5",

        # Corkboard
        "cork_bg": "#221D2C",
        "cork_dot": "#322A42",
    }

    # Corner Radii System
    RADIUS_SM = 8
    RADIUS_MD = 12
    RADIUS_LG = 16
    RADIUS_XL = 20
    RADIUS_FULL = 999

    # Sizing & Spacing Constants
    BTN_HEIGHT = 42
    BTN_HEIGHT_SM = 34
    INPUT_HEIGHT = 42
    SIDEBAR_WIDTH = 236
    CARD_PAD_X = 22
    CARD_PAD_Y = 18

    # Typography System (Clean Segoe UI / Poppins hierarchy)
    FONT_FAMILY = "Segoe UI"
    FONT_HEADING = "Segoe UI"

    @classmethod
    def current(cls) -> Dict[str, str]:
        return cls.DARK if cls.MODE == "dark" else cls.LIGHT

    @classmethod
    def set_mode(cls, mode: str):
        if mode in ("light", "dark"):
            cls.MODE = mode

    @classmethod
    def toggle_mode(cls) -> str:
        cls.MODE = "dark" if cls.MODE == "light" else "light"
        return cls.MODE

    # Typography Hierarchy
    @classmethod
    def font_page_title(cls) -> Tuple[str, int, str]:
        """Page titles: 28-32px bold"""
        return (cls.FONT_HEADING, 28, "bold")

    @classmethod
    def font_title(cls) -> Tuple[str, int, str]:
        """Alias for page title"""
        return (cls.FONT_HEADING, 28, "bold")

    @classmethod
    def font_card_title(cls) -> Tuple[str, int, str]:
        """Card titles: 18px semibold/bold"""
        return (cls.FONT_HEADING, 18, "bold")

    @classmethod
    def font_header(cls) -> Tuple[str, int, str]:
        """Section header / Card title (18px)"""
        return (cls.FONT_HEADING, 18, "bold")

    @classmethod
    def font_subheader(cls) -> Tuple[str, int, str]:
        """Subheader: 16px bold"""
        return (cls.FONT_HEADING, 16, "bold")

    @classmethod
    def font_body(cls) -> Tuple[str, int]:
        """Base body text: 14px clean"""
        return (cls.FONT_FAMILY, 14)

    @classmethod
    def font_body_bold(cls) -> Tuple[str, int, str]:
        """Bold body text / Button text: 14px bold"""
        return (cls.FONT_HEADING, 14, "bold")

    @classmethod
    def font_small(cls) -> Tuple[str, int]:
        """Captions & meta info: 12px"""
        return (cls.FONT_FAMILY, 12)

    @classmethod
    def font_tag(cls) -> Tuple[str, int, str]:
        """Badges & tags: 12px bold"""
        return (cls.FONT_HEADING, 12, "bold")

    @classmethod
    def font_logo(cls) -> Tuple[str, int, str]:
        """Sidebar logo text: 20px bold"""
        return (cls.FONT_HEADING, 20, "bold")

    @classmethod
    def font_timer(cls) -> Tuple[str, int, str]:
        """Focus timer countdown: 56px bold"""
        return (cls.FONT_HEADING, 56, "bold")

    @classmethod
    def font_metric(cls) -> Tuple[str, int, str]:
        """Dashboard stat numbers: 26px bold"""
        return (cls.FONT_HEADING, 26, "bold")

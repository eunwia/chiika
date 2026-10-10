"""
theme.py - Modern Cozy Productivity Aesthetic for Chiikawa Study Planner
Features refined Yu Gothic UI / Segoe UI typography and complete light/dark palette definitions.
"""

from typing import Dict, Any

class Theme:
    MODE = "light"  # "light" or "dark"

    # Cozy Day (Light Palette)
    LIGHT = {
        "bg_app": "#F9F7F4",            # Soft warm alabaster paper
        "bg_sidebar": "#F1ECE6",        # Clean warm neutral sidebar
        "bg_sidebar_active": "#E4DDD3",  # Refined active highlight
        "bg_sidebar_hover": "#EAE4DC",
        
        "bg_card": "#FFFFFF",           # Pure elevated card surface
        "bg_card_secondary": "#F5F2EC", # Subtle grouped surface
        "bg_card_hover": "#FAFAF8",

        "border": "#EAE4DC",            # Hairline subtle border
        "border_subtle": "#F2ECE5",
        "border_focus": "#E66882",

        # Refined Accents
        "accent_pink": "#E66882",        # Warm modern rose coral (primary)
        "accent_pink_hover": "#D4536D",
        "accent_blue": "#5694D6",        # Crisp serene slate blue
        "accent_blue_hover": "#4481C2",
        "accent_yellow": "#E5A038",      # Warm golden amber
        "accent_yellow_hover": "#CD8B29",
        "accent_lavender": "#8B70CF",    # Dusty cozy lavender
        "accent_lavender_hover": "#785EBA",
        "accent_mint": "#48A87D",        # Fresh matcha green
        "accent_mint_hover": "#39946C",

        # Priority Badges
        "priority_high_bg": "#FDF0F3",
        "priority_high_fg": "#D94161",
        "priority_med_bg": "#FEF7EE",
        "priority_med_fg": "#C57C26",
        "priority_low_bg": "#EEF8F2",
        "priority_low_fg": "#2E8860",

        # Text Hierarchy
        "text_primary": "#2D2630",      # Deep charcoal plum
        "text_secondary": "#746977",    # Refined muted gray
        "text_muted": "#A69DA9",        # Placeholder / subtle
        "text_on_accent": "#FFFFFF",

        # Form Inputs
        "input_bg": "#FFFFFF",
        "input_border": "#DCD5CC",
        "input_border_focus": "#E66882",

        # Corkboard
        "cork_bg": "#EFE6DA",
        "cork_dot": "#E2D8C9",
    }

    # Cozy Night (Dark Palette)
    DARK = {
        "bg_app": "#17141E",            # Deep twilight night canvas
        "bg_sidebar": "#1F1B29",        # Distinct sleek dark eggplant sidebar
        "bg_sidebar_active": "#332C44",  # Active nav item surface
        "bg_sidebar_hover": "#2A2438",

        "bg_card": "#252132",           # Elevated dark card
        "bg_card_secondary": "#1E1A29",
        "bg_card_hover": "#2C273B",

        "border": "#362F46",            # Refined hairline dark border
        "border_subtle": "#2B2538",
        "border_focus": "#F0748F",

        # Refined Accents in Dark Mode
        "accent_pink": "#F0748F",
        "accent_pink_hover": "#DD5F7B",
        "accent_blue": "#6AA3DE",
        "accent_blue_hover": "#548FC9",
        "accent_yellow": "#EDB04C",
        "accent_yellow_hover": "#DA9B35",
        "accent_lavender": "#9F85DF",
        "accent_lavender_hover": "#8C6FCC",
        "accent_mint": "#56B88B",
        "accent_mint_hover": "#44A477",

        # Priority Badges
        "priority_high_bg": "#3D1D29",
        "priority_high_fg": "#F896AC",
        "priority_med_bg": "#3D2E1A",
        "priority_med_fg": "#F8C67B",
        "priority_low_bg": "#19362A",
        "priority_low_fg": "#84E2B7",

        # Text Hierarchy
        "text_primary": "#F4F0F6",
        "text_secondary": "#A89FAE",
        "text_muted": "#756D7C",
        "text_on_accent": "#FFFFFF",

        # Form Inputs
        "input_bg": "#1E1A29",
        "input_border": "#3A334B",
        "input_border_focus": "#F0748F",

        # Corkboard
        "cork_bg": "#231F2E",
        "cork_dot": "#332D43",
    }

    @classmethod
    def current(cls) -> Dict[str, str]:
        return cls.DARK if cls.MODE == "dark" else cls.LIGHT

    @classmethod
    def set_mode(cls, mode: str):
        if mode in ("light", "dark"):
            cls.MODE = mode

    # Refined typography: Yu Gothic UI provides soft modern letterforms and clean kerning
    FONT_FAMILY = "Yu Gothic UI"
    FONT_HEADING = "Yu Gothic UI Semibold"
    
    @classmethod
    def font_logo(cls):
        return (cls.FONT_HEADING, 18, "bold")

    @classmethod
    def font_title(cls):
        return (cls.FONT_HEADING, 21, "bold")

    @classmethod
    def font_header(cls):
        return (cls.FONT_HEADING, 15, "bold")

    @classmethod
    def font_subheader(cls):
        return (cls.FONT_HEADING, 13, "bold")

    @classmethod
    def font_body(cls):
        return (cls.FONT_FAMILY, 12)

    @classmethod
    def font_body_bold(cls):
        return (cls.FONT_HEADING, 12, "bold")

    @classmethod
    def font_small(cls):
        return (cls.FONT_FAMILY, 11)

    @classmethod
    def font_timer(cls):
        return (cls.FONT_FAMILY, 48, "bold")

    @classmethod
    def font_tag(cls):
        return (cls.FONT_HEADING, 10, "bold")

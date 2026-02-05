"""Centralized theme system for Stembler GUI.

This module defines all design tokens (colors, spacing, typography, shadows)
used throughout the application for consistent styling and easy maintenance.

Inspired by: Spotify Desktop App, macOS Native Apps (Music, Photos)
Design System: Modern Flat with subtle shadows and depth
"""


class Theme:
    """Central theme class containing all design tokens."""

    # ==================== COLORS ====================

    # Background Colors
    BACKGROUND_PRIMARY = "#FFFFFF"  # Pure white for main background
    BACKGROUND_SECONDARY = "#F8F9FA"  # Slight gray for cards/panels
    BACKGROUND_TERTIARY = "#F0F2F5"  # Lighter gray for input backgrounds
    BACKGROUND_HOVER = "#F5F7FA"  # Hover state background

    # Primary Colors (Spotify-inspired green)
    PRIMARY = "#1DB954"  # Primary actions, success, progress
    PRIMARY_HOVER = "#1ED760"  # Brighter on hover
    PRIMARY_PRESSED = "#1AA34A"  # Darker on press
    PRIMARY_LIGHT = "#F0F9F4"  # Very light green for backgrounds

    # Secondary Colors
    SECONDARY = "#535353"  # Dark gray for secondary actions
    SECONDARY_HOVER = "#3E3E3E"  # Darker on hover
    SECONDARY_PRESSED = "#2A2A2A"  # Even darker on press

    # Accent Colors (blue — secondary interactive elements: Browse, focus rings)
    ACCENT = "#3B82F6"  # Accent actions (Browse button, focus borders)
    ACCENT_HOVER = "#2563EB"  # Darker on hover
    ACCENT_PRESSED = "#1D4ED8"  # Darker on press

    # Semantic Colors
    ERROR = "#E22134"  # Error states, cancel
    ERROR_LIGHT = "#FFEBEE"  # Light error background
    SUCCESS = "#1DB954"  # Success states (same as primary)
    SUCCESS_LIGHT = "#F0F9F4"  # Light success background
    WARNING = "#FF9800"  # Warning states
    INFO = "#2196F3"  # Info states

    # Text Colors
    TEXT_PRIMARY = "#121212"  # Almost black for main text
    TEXT_SECONDARY = "#6A6A6A"  # Medium gray for supporting text
    TEXT_TERTIARY = "#9B9B9B"  # Light gray for hints/placeholders
    TEXT_DISABLED = "#BDBDBD"  # Disabled text
    TEXT_ON_PRIMARY = "#FFFFFF"  # White text on colored backgrounds
    TEXT_ON_ERROR = "#FFFFFF"  # White text on error backgrounds

    # Border Colors
    BORDER_LIGHT = "#E5E5E5"  # Subtle borders
    BORDER_MEDIUM = "#D1D1D1"  # Visible borders
    BORDER_DARK = "#9E9E9E"  # Strong borders
    BORDER_FOCUS = ACCENT  # Focus state borders (blue, not green)

    # ==================== SPACING ====================
    # Following 8px grid system for consistent rhythm

    SPACING_XS = 4  # 4px - Tight spacing
    SPACING_SM = 8  # 8px - Small gaps
    SPACING_MD = 16  # 16px - Default spacing
    SPACING_LG = 24  # 24px - Section spacing
    SPACING_XL = 32  # 32px - Large margins
    SPACING_XXL = 48  # 48px - Extra large spacing

    # ==================== SHADOWS ====================
    # Subtle shadows for depth without being heavy-handed

    SHADOW_SM = "0 1px 3px rgba(0, 0, 0, 0.1)"
    SHADOW_MD = "0 4px 6px rgba(0, 0, 0, 0.07), 0 2px 4px rgba(0, 0, 0, 0.06)"
    SHADOW_LG = "0 10px 15px rgba(0, 0, 0, 0.1), 0 4px 6px rgba(0, 0, 0, 0.05)"
    SHADOW_XL = "0 20px 25px rgba(0, 0, 0, 0.15), 0 10px 10px rgba(0, 0, 0, 0.04)"

    # Special shadows
    SHADOW_FOCUS = f"0 0 0 3px {PRIMARY}40"  # Primary color at 25% opacity
    SHADOW_GLOW = f"0 0 8px {PRIMARY}4D"  # Glow effect (30% opacity)

    # ==================== BORDER RADIUS ====================

    RADIUS_SM = 6  # Small elements (chips, tags)
    RADIUS_MD = 10  # Medium elements (buttons, inputs)
    RADIUS_LG = 16  # Large elements (cards, containers)
    RADIUS_XL = 20  # Extra large (dialogs)
    RADIUS_FULL = 9999  # Fully rounded (pills)

    # ==================== TYPOGRAPHY ====================

    # Font Family
    FONT_FAMILY = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
    FONT_FAMILY_MONO = "'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace"

    # Font Sizes
    FONT_SIZE_XS = 11  # Captions, hints
    FONT_SIZE_SM = 13  # Labels, helper text
    FONT_SIZE_MD = 15  # Body text, buttons
    FONT_SIZE_LG = 18  # Subheadings
    FONT_SIZE_XL = 24  # Headings
    FONT_SIZE_XXL = 32  # Large headings

    # Font Weights
    FONT_WEIGHT_REGULAR = "normal"
    FONT_WEIGHT_MEDIUM = "500"
    FONT_WEIGHT_SEMIBOLD = "600"
    FONT_WEIGHT_BOLD = "bold"

    # Line Heights
    LINE_HEIGHT_TIGHT = 1.2
    LINE_HEIGHT_NORMAL = 1.5
    LINE_HEIGHT_RELAXED = 1.75

    # Letter Spacing
    LETTER_SPACING_TIGHT = "-0.5px"
    LETTER_SPACING_NORMAL = "0"
    LETTER_SPACING_WIDE = "0.5px"

    # ==================== TRANSITIONS ====================

    # Timing
    TRANSITION_FAST = "0.15s"
    TRANSITION_NORMAL = "0.2s"
    TRANSITION_SLOW = "0.3s"

    # Easing Functions
    EASE_IN_OUT = "cubic-bezier(0.4, 0, 0.2, 1)"
    EASE_OUT = "cubic-bezier(0.0, 0, 0.2, 1)"
    EASE_IN = "cubic-bezier(0.4, 0, 1, 1)"

    # Common Transitions
    TRANSITION_ALL = f"all {TRANSITION_NORMAL} {EASE_IN_OUT}"
    TRANSITION_COLOR = f"color {TRANSITION_NORMAL} {EASE_IN_OUT}"
    TRANSITION_BACKGROUND = f"background-color {TRANSITION_NORMAL} {EASE_IN_OUT}"
    TRANSITION_TRANSFORM = f"transform {TRANSITION_NORMAL} {EASE_OUT}"
    TRANSITION_SHADOW = f"box-shadow {TRANSITION_NORMAL} {EASE_IN_OUT}"

    # ==================== COMPONENT SIZES ====================

    # Buttons
    BUTTON_HEIGHT_SM = 32
    BUTTON_HEIGHT_MD = 40
    BUTTON_HEIGHT_LG = 48
    BUTTON_PADDING_X = 16
    BUTTON_PADDING_X_LG = 24

    # Inputs
    INPUT_HEIGHT = 40
    INPUT_PADDING_X = 12
    INPUT_PADDING_Y = 10

    # Icons
    ICON_SIZE_SM = 16
    ICON_SIZE_MD = 24
    ICON_SIZE_LG = 32
    ICON_SIZE_XL = 48

    # ==================== HELPER METHODS ====================

    @staticmethod
    def button_style(
        bg_color: str,
        hover_color: str,
        pressed_color: str,
        text_color: str = None,
        height: int = None,
        add_shadow: bool = True,
    ) -> str:
        """Generate consistent button stylesheet.

        Args:
            bg_color: Background color
            hover_color: Hover state color
            pressed_color: Pressed state color
            text_color: Text color (defaults to white)
            height: Button height (defaults to BUTTON_HEIGHT_LG)
            add_shadow: Whether to add shadow (note: Qt doesn't support box-shadow in QSS)

        Returns:
            Qt stylesheet string
        """
        text_color = text_color or Theme.TEXT_ON_PRIMARY
        height = height or Theme.BUTTON_HEIGHT_LG

        return f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                border: none;
                border-radius: {Theme.RADIUS_MD}px;
                font-size: {Theme.FONT_SIZE_MD}px;
                font-weight: {Theme.FONT_WEIGHT_SEMIBOLD};
                padding: 0 {Theme.BUTTON_PADDING_X}px;
                min-height: {height}px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {pressed_color};
            }}
            QPushButton:disabled {{
                background-color: {Theme.BORDER_LIGHT};
                color: {Theme.TEXT_DISABLED};
            }}
        """

    @staticmethod
    def card_style(padding: int = None, radius: int = None, shadow: str = None) -> str:
        """Generate consistent card/container stylesheet.

        Args:
            padding: Internal padding (defaults to SPACING_LG)
            radius: Border radius (defaults to RADIUS_LG)
            shadow: Shadow style (defaults to SHADOW_MD)

        Returns:
            Qt stylesheet string
        """
        padding = padding or Theme.SPACING_LG
        radius = radius or Theme.RADIUS_LG
        shadow = shadow or Theme.SHADOW_MD

        return f"""
            QFrame {{
                background-color: {Theme.BACKGROUND_PRIMARY};
                border: none;
                border-radius: {radius}px;
                padding: {padding}px;
            }}
        """

    @staticmethod
    def input_style(height: int = None) -> str:
        """Generate consistent input field stylesheet.

        Args:
            height: Input height (defaults to INPUT_HEIGHT)

        Returns:
            Qt stylesheet string
        """
        height = height or Theme.INPUT_HEIGHT

        return f"""
            QLineEdit, QComboBox {{
                background-color: {Theme.BACKGROUND_TERTIARY};
                color: {Theme.TEXT_PRIMARY};
                border: 1px solid {Theme.BORDER_MEDIUM};
                border-radius: {Theme.RADIUS_MD}px;
                padding: {Theme.INPUT_PADDING_Y}px {Theme.INPUT_PADDING_X}px;
                font-size: {Theme.FONT_SIZE_MD}px;
                min-height: {height}px;
            }}
            QLineEdit:focus, QComboBox:focus {{
                border: 2px solid {Theme.BORDER_FOCUS};
                background-color: {Theme.BACKGROUND_PRIMARY};
            }}
            QLineEdit:disabled, QComboBox:disabled {{
                background-color: {Theme.BORDER_LIGHT};
                color: {Theme.TEXT_DISABLED};
            }}
        """

    @staticmethod
    def label_style(size: int = None, color: str = None, weight: str = None) -> str:
        """Generate consistent label stylesheet.

        Args:
            size: Font size (defaults to FONT_SIZE_MD)
            color: Text color (defaults to TEXT_PRIMARY)
            weight: Font weight (defaults to FONT_WEIGHT_REGULAR)

        Returns:
            Qt stylesheet string
        """
        size = size or Theme.FONT_SIZE_MD
        color = color or Theme.TEXT_PRIMARY
        weight = weight or Theme.FONT_WEIGHT_REGULAR

        return f"""
            QLabel {{
                color: {color};
                font-size: {size}px;
                font-weight: {weight};
            }}
        """


# Convenience constants for common use cases
PRIMARY_BUTTON = Theme.button_style(
    Theme.PRIMARY, Theme.PRIMARY_HOVER, Theme.PRIMARY_PRESSED
)

SECONDARY_BUTTON = Theme.button_style(
    Theme.SECONDARY, Theme.SECONDARY_HOVER, Theme.SECONDARY_PRESSED
)

ACCENT_BUTTON = Theme.button_style(
    Theme.ACCENT, Theme.ACCENT_HOVER, Theme.ACCENT_PRESSED
)

ERROR_BUTTON = Theme.button_style(
    Theme.ERROR, "#D32F2F", "#B71C1C"  # Darker red on hover  # Even darker on press
)

CARD_DEFAULT = Theme.card_style()
CARD_COMPACT = Theme.card_style(padding=Theme.SPACING_MD, radius=Theme.RADIUS_MD)
INPUT_DEFAULT = Theme.input_style()

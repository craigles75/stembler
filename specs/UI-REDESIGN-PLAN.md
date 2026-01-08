# UI/UX Redesign Plan: Stembler Desktop GUI

**Date**: 2026-01-08
**Goal**: Transform the Stembler GUI from a basic functional interface to a polished, modern application with visual depth, refined typography, and professional aesthetics.

**Design Inspiration**: Spotify Desktop App, macOS Native Apps (Music, Photos)

---

## Design Goals

- **Modern Flat Design** with subtle shadows and depth
- **Visual Hierarchy** through refined spacing, typography, and color
- **Professional Polish** similar to Spotify and macOS Music/Photos apps
- **Centralized Theming** for easy maintenance and consistency
- **Built-in Qt Icons** for visual enhancement without external dependencies
- **Smooth Interactions** with hover states and visual feedback

---

## Current Issues to Address

1. **Flat, lifeless appearance** - No depth, shadows, or visual interest
2. **Scattered inline stylesheets** - Colors and styles duplicated across 6+ files
3. **Basic typography** - Limited hierarchy, no refined spacing
4. **Minimal hover feedback** - No animations or smooth transitions
5. **Inconsistent spacing** - Uniform 20px everywhere, lacks visual rhythm
6. **No icons** - Text-only interface lacks visual cues

---

## Implementation Strategy

### Phase 1: Create Centralized Theme System

**New File**: `src/music_stem_separator/gui/utils/theme.py`

Create a centralized theme class that defines:
- **Color palette** (primary, secondary, background, text, borders)
- **Spacing constants** (margins, paddings, gaps)
- **Typography** (font families, sizes, weights)
- **Shadow definitions** (subtle box shadows for depth)
- **Border radius values** (consistent rounded corners)
- **Transition speeds** (for smooth animations)

**Benefits**:
- Single source of truth for design tokens
- Easy to update colors globally
- Consistent spacing and sizing
- Foundation for future dark mode support

**Key Theme Values**:

```python
class Theme:
    # Colors
    BACKGROUND_PRIMARY = "#FFFFFF"      # Pure white for main background
    BACKGROUND_SECONDARY = "#F8F9FA"    # Slight gray for cards/panels
    BACKGROUND_TERTIARY = "#F0F2F5"     # Lighter gray for input backgrounds

    PRIMARY = "#1DB954"                 # Spotify green (replacing #4CAF50)
    PRIMARY_HOVER = "#1ED760"           # Brighter on hover
    PRIMARY_PRESSED = "#1AA34A"         # Darker on press

    SECONDARY = "#535353"               # Dark gray for secondary actions
    SECONDARY_HOVER = "#3E3E3E"

    ERROR = "#E22134"                   # Modern red
    SUCCESS = "#1DB954"                 # Spotify green

    TEXT_PRIMARY = "#121212"            # Almost black (better than #333)
    TEXT_SECONDARY = "#6A6A6A"          # Medium gray
    TEXT_TERTIARY = "#9B9B9B"           # Light gray

    BORDER_LIGHT = "#E5E5E5"            # Subtle borders
    BORDER_MEDIUM = "#D1D1D1"           # Visible borders

    # Spacing (following 8px grid system)
    SPACING_XS = 4
    SPACING_SM = 8
    SPACING_MD = 16
    SPACING_LG = 24
    SPACING_XL = 32
    SPACING_XXL = 48

    # Shadows (for depth)
    SHADOW_SM = "0 1px 3px rgba(0, 0, 0, 0.1)"
    SHADOW_MD = "0 4px 6px rgba(0, 0, 0, 0.07), 0 2px 4px rgba(0, 0, 0, 0.06)"
    SHADOW_LG = "0 10px 15px rgba(0, 0, 0, 0.1), 0 4px 6px rgba(0, 0, 0, 0.05)"

    # Border Radius
    RADIUS_SM = 6
    RADIUS_MD = 10
    RADIUS_LG = 16

    # Typography
    FONT_FAMILY = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    FONT_SIZE_XS = 11
    FONT_SIZE_SM = 13
    FONT_SIZE_MD = 15
    FONT_SIZE_LG = 18
    FONT_SIZE_XL = 24
```

---

### Phase 2: Update Main Window

**File**: `src/music_stem_separator/gui/main_window.py`

**Changes**:

1. **Apply window background color**
   ```python
   self.setStyleSheet(f"QMainWindow {{ background-color: {Theme.BACKGROUND_PRIMARY}; }}")
   ```

2. **Update header styling**
   - Increase header size to **28px** (from 24px)
   - Use `Theme.TEXT_PRIMARY` color
   - Add letter-spacing for refinement
   - Reduce subtitle opacity

3. **Adjust layout spacing**
   - Change from uniform 20px to **24px** vertical spacing
   - Maintain 32px side margins
   - Add more breathing room between major sections

4. **Add subtle separator lines** between sections
   - Use `Theme.BORDER_LIGHT` color
   - 1px height, subtle dividers

---

### Phase 3: Redesign File Input Widget

**File**: `src/music_stem_separator/gui/widgets/file_input.py`

**Major Changes**:

#### 1. Drop Zone Enhancement
- **Increase height** to 180px (from 150px)
- **Add shadow**: `box-shadow: ${Theme.SHADOW_MD}` for depth
- **Larger border radius**: 12px (from 8px)
- **Refined colors**:
  - Default background: `#FAFBFC` (lighter than current)
  - Default border: `2px dashed #D1D1D1` (less aggressive)
  - Hover background: `#F5F7FA`
- **Add icon**: Upload/cloud icon using Qt's standard icons above text
- **Centered layout** with icon, main text, and hint text

#### 2. Active/Dragging State
- Border changes to `3px solid ${Theme.PRIMARY}` (thicker, more visible)
- Background: `#F0F9F4` (subtle green tint)
- Add pulsing animation

#### 3. Valid Input State
- **Card-like appearance** with `box-shadow: ${Theme.SHADOW_SM}`
- Checkmark icon (Qt standard icon) next to filename
- **Colored left border accent**: `4px solid ${Theme.SUCCESS}`
- Rounded corners: 10px

#### 4. Browse Button
- Style as secondary action button
- Add folder icon (Qt standard icon)
- Refined padding and hover state

---

### Phase 4: Enhance Process Button

**File**: `src/music_stem_separator/gui/widgets/process_button.py`

**Changes**:

1. **Increase button height** to **48px** (from 40px minimum)

2. **Add shadow for depth**
   ```css
   box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
   ```

3. **Smooth transitions** for hover/press states
   ```css
   transition: all 0.2s ease;
   ```

4. **Hover effects**:
   - Slight lift: `box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1)`
   - Transform: `translateY(-1px)`

5. **Add icons**:
   - Processing state: Play icon → Spinner
   - Cancel state: Stop/X icon
   - Use Qt's standard icons

6. **Refined colors**:
   - Primary button: Spotify green (`#1DB954`)
   - Hover: Brighter green (`#1ED760`)
   - Pressed: Deeper green (`#1AA34A`)

7. **Typography refinement**:
   - Font size: **15px** (from 14px)
   - Letter spacing: **0.5px** for better readability

---

### Phase 5: Redesign Progress Display

**File**: `src/music_stem_separator/gui/widgets/progress_display.py`

**Major Changes**:

#### 1. Container Frame
- Remove visible border (currently `1px solid #ddd`)
- Add **card shadow**: `box-shadow: ${Theme.SHADOW_MD}`
- Background: Pure white `#FFFFFF` (not gray)
- **Larger border radius**: 16px (from 8px)
- **Increase padding**: 24px (from 20px)

#### 2. Progress Bar Redesign
- **Height**: 8px (from 25px) - modern slim progress bar
- **Remove border** entirely
- **Background**: `#E5E5E5` (track color)
- **Chunk/fill**: Gradient from `#1DB954` to `#1ED760`
- **Border radius**: 4px (pill shape)
- **Add subtle glow** when active: `box-shadow: 0 0 8px rgba(29, 185, 84, 0.3)`

#### 3. Percentage Display
- Move to **right side of status label** (inline, not separate row)
- Larger size: **20px bold** (from 13px)
- Gradient text color matching progress bar

#### 4. ETA Display
- Add clock icon (Qt standard icon)
- Refined typography: **13px semibold**
- Position to right side of bar

#### 5. Stage/Status Messages
- Move to top (above progress bar)
- Larger: **15px semibold**
- Add animated dots for "Processing..." effect
- Icon indicators for each stage (loading, processing, saving)

---

### Phase 6: Improve Result Display

**File**: `src/music_stem_separator/gui/widgets/result_display.py`

**Changes**:

#### 1. Container Frame
- **Card design**: Pure white background with `box-shadow: ${Theme.SHADOW_MD}`
- Remove border
- Larger radius: 16px
- Padding: 24px

#### 2. Success State
- Large checkmark icon (Qt standard icon, 48px)
- **Success color**: Spotify green
- Title: **18px bold**
- Add subtle green accent background

#### 3. Error State
- Large error icon (48px)
- **Error color**: Modern red
- Refined error message display
- Add "Try Again" suggestion

#### 4. Open Folder Button
- Add folder icon (Qt standard)
- Refined button styling to match secondary style
- **Height**: 40px
- Shadow on hover
- Smooth transitions

---

### Phase 7: Enhance Settings Panel

**File**: `src/music_stem_separator/gui/widgets/settings_panel.py`

**Changes**:

#### 1. Dialog Styling
- Increase width to **650px** (from 600px)
- Apply card background with shadow
- Refined spacing between groups

#### 2. Group Boxes
- **Card-style containers** with white backgrounds
- Add subtle shadows: `box-shadow: ${Theme.SHADOW_SM}`
- Border radius: 12px
- Padding: 20px
- Remove default QGroupBox borders

#### 3. Form Elements
- **Larger input fields**: 40px height
- **Refined borders**: `1px solid ${Theme.BORDER_MEDIUM}`
- **Border radius**: 8px
- **Focus state**: Border changes to `${Theme.PRIMARY}` with shadow glow
- Add icons to inputs (model icon, folder icon, etc.)

#### 4. Dropdown/ComboBox
- Custom styling for better appearance
- Dropdown arrow icon
- Hover effects

#### 5. Test Credentials Button
- Secondary button style
- Add checkmark icon on success
- Add loading spinner during test

---

### Phase 8: Polish About Dialog

**File**: `src/music_stem_separator/gui/widgets/about_dialog.py`

**Changes**:

1. **Increase dialog width** to 550px

2. **Add app icon** at top (using Qt icons as placeholder)

3. **Refined typography**:
   - App name: **32px bold** (from 24px)
   - Version: **15px medium**
   - Description: **14px regular**

4. **Links**:
   - Better visual distinction
   - Hover effects (underline, color change)
   - Add external link icons

5. **Overall spacing**:
   - More generous padding: 40px
   - Better section separation

---

### Phase 9: Add Visual Polish

**Cross-Widget Enhancements**:

#### 1. Smooth Transitions
Add to all interactive elements:
```css
transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
```

#### 2. Focus States
Add visible focus rings:
```css
outline: 2px solid ${Theme.PRIMARY};
outline-offset: 2px;
```

#### 3. Hover Effects
Consistent across buttons/clickable elements:
- Subtle lift (translateY -1px)
- Shadow increase
- Color brightness shift

#### 4. Loading States
Add spinners/animations for async operations

#### 5. Empty States
Better messaging when no input selected

---

## Implementation Order

1. ✅ **Create theme.py** - Foundation for all other changes
2. ✅ **Update main_window.py** - Set overall application style
3. ✅ **Redesign file_input.py** - Most visible component, biggest impact
4. ✅ **Enhance process_button.py** - Primary action, critical UX
5. ✅ **Redesign progress_display.py** - User spends most time here
6. ✅ **Improve result_display.py** - Final impression
7. ✅ **Enhance settings_panel.py** - Power user feature
8. ✅ **Polish about_dialog.py** - Nice to have

---

## Files to Modify

### New Files:
- `src/music_stem_separator/gui/utils/theme.py`

### Modified Files:
- `src/music_stem_separator/gui/main_window.py`
- `src/music_stem_separator/gui/widgets/file_input.py`
- `src/music_stem_separator/gui/widgets/process_button.py`
- `src/music_stem_separator/gui/widgets/progress_display.py`
- `src/music_stem_separator/gui/widgets/result_display.py`
- `src/music_stem_separator/gui/widgets/settings_panel.py`
- `src/music_stem_separator/gui/widgets/about_dialog.py`

---

## Design Tokens Reference

### Color Palette

| Token | Value | Usage |
|-------|-------|-------|
| `PRIMARY` | `#1DB954` | Primary actions, success, progress |
| `PRIMARY_HOVER` | `#1ED760` | Hover states |
| `PRIMARY_PRESSED` | `#1AA34A` | Pressed states |
| `SECONDARY` | `#535353` | Secondary actions |
| `ERROR` | `#E22134` | Error states, cancel |
| `TEXT_PRIMARY` | `#121212` | Main text |
| `TEXT_SECONDARY` | `#6A6A6A` | Supporting text |
| `TEXT_TERTIARY` | `#9B9B9B` | Hints, placeholders |
| `BACKGROUND_PRIMARY` | `#FFFFFF` | Main background |
| `BACKGROUND_SECONDARY` | `#F8F9FA` | Cards, panels |
| `BORDER_LIGHT` | `#E5E5E5` | Subtle borders |
| `BORDER_MEDIUM` | `#D1D1D1` | Visible borders |

### Spacing Scale (8px Grid)

| Token | Value | Usage |
|-------|-------|-------|
| `SPACING_XS` | 4px | Tight spacing |
| `SPACING_SM` | 8px | Small gaps |
| `SPACING_MD` | 16px | Default spacing |
| `SPACING_LG` | 24px | Section spacing |
| `SPACING_XL` | 32px | Large margins |
| `SPACING_XXL` | 48px | Extra large spacing |

### Typography Scale

| Token | Size | Usage |
|-------|------|-------|
| `FONT_SIZE_XS` | 11px | Captions, hints |
| `FONT_SIZE_SM` | 13px | Labels, helper text |
| `FONT_SIZE_MD` | 15px | Body text, buttons |
| `FONT_SIZE_LG` | 18px | Subheadings |
| `FONT_SIZE_XL` | 24px | Headings |

### Shadows

| Token | Value | Usage |
|-------|-------|-------|
| `SHADOW_SM` | `0 1px 3px rgba(0,0,0,0.1)` | Small elements |
| `SHADOW_MD` | `0 4px 6px rgba(0,0,0,0.07), 0 2px 4px rgba(0,0,0,0.06)` | Cards, panels |
| `SHADOW_LG` | `0 10px 15px rgba(0,0,0,0.1), 0 4px 6px rgba(0,0,0,0.05)` | Modals, elevated elements |

### Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| `RADIUS_SM` | 6px | Small elements |
| `RADIUS_MD` | 10px | Buttons, inputs |
| `RADIUS_LG` | 16px | Cards, containers |

---

## Expected Outcome

A modern, polished GUI that:
- ✅ Has visual depth through subtle shadows and layering
- ✅ Uses Spotify-inspired green accent color
- ✅ Features refined typography with proper hierarchy
- ✅ Includes icons for better visual communication
- ✅ Provides smooth hover/focus feedback
- ✅ Maintains consistent spacing using 8px grid
- ✅ Has centralized theming for easy updates
- ✅ Looks professional like Spotify or macOS native apps
- ✅ Improves user confidence and perceived quality

---

## Before & After Comparison

### Before
- Flat, gray backgrounds (`#f5f5f5`, `#f9f9f9`)
- 1px borders everywhere
- Basic green (`#4CAF50`)
- Uniform 20px spacing
- No shadows
- No icons
- 14px button text
- 25px progress bar height

### After
- Pure white backgrounds with card shadows
- Minimal borders, shadow-based depth
- Spotify green (`#1DB954`)
- 8px grid spacing system (8, 16, 24, 32px)
- Subtle multi-layered shadows
- Qt standard icons throughout
- 15px button text with letter-spacing
- 8px slim progress bar with glow

---

## Notes

- **Dark Mode**: Not included in this phase but theme system enables future implementation
- **Accessibility**: Maintain WCAG 2.1 AA contrast ratios (4.5:1 for normal text)
- **Performance**: CSS transitions are GPU-accelerated, minimal performance impact
- **Cross-Platform**: Qt stylesheets work identically on macOS, Windows, Linux
- **Icons**: Using Qt's built-in `QStyle.StandardPixmap` - no external dependencies

---

**Status**: Ready for implementation
**Estimated Impact**: High - Transforms basic functional UI into professional desktop application

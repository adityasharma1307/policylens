"""Color roles from the validated dataviz reference palette (light mode only --
this dashboard doesn't implement a dark-mode toggle, so only the light steps
are used). Chart code should reference these roles, never raw hex inline.
"""

SURFACE = "#fcfcfb"
PAGE = "#f9f9f7"
TEXT_PRIMARY = "#0b0b0b"
TEXT_SECONDARY = "#52514e"
TEXT_MUTED = "#898781"
GRIDLINE = "#e1e0d9"
BASELINE = "#c3c2b7"
BORDER = "rgba(11,11,11,0.10)"

# Sequential (magnitude): one hue, light -> dark. Used for the state ranking bar
# and the state x commodity heatmap -- both are "compare magnitude" jobs, not
# identity, so they get one hue rather than a categorical palette per category.
SEQUENTIAL_BLUE = [
    "#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec",
    "#5598e7", "#3987e5", "#2a78d6", "#256abf", "#1c5cab",
    "#184f95", "#104281", "#0d366b",
]

# Categorical slots, fixed order -- only used where series identity is the point
# (retail vs wholesale line pair). Never cycled past what's assigned here.
CATEGORICAL = {
    "blue": "#2a78d6",
    "orange": "#eb6834",
    "aqua": "#1baf7a",
    "yellow": "#eda100",
}

# Status palette (fixed, never themed, never reused as a series color).
STATUS_GOOD = "#0ca30c"
STATUS_WARNING = "#fab219"
STATUS_SERIOUS = "#ec835a"
STATUS_CRITICAL = "#d03b3b"

FONT_FAMILY = "system-ui, -apple-system, 'Segoe UI', sans-serif"

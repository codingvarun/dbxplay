"""
SVG icons used in the Databricks-like table UI.
These are inline SVG strings matching the Databricks visual style.
"""


def get_type_icon_svg(dtype_category: str, accent_color: str = "var(--db-accent)") -> str:
    """Return an inline SVG icon for the given data type category.

    Categories: 'string', 'integer', 'float', 'boolean', 'datetime', 'complex'
    """
    icons = {
        # ABC icon for string columns
        "string": (
            '<svg class="db-type-icon" viewBox="0 0 16 16" width="14" height="14" fill="none">'
            '<text x="1" y="12" font-size="7.5" font-weight="700" fill="#5f6368" '
            'font-family="Arial,sans-serif" letter-spacing="0.5">'
            f'<tspan fill="{accent_color}">A</tspan>'
            '<tspan fill="#5f6368">B</tspan>'
            '</text>'
            '<text x="10.5" y="8" font-size="5.5" font-weight="600" fill="#5f6368" '
            'font-family="Arial,sans-serif">C</text>'
            '</svg>'
        ),
        # 123 icon for integer columns
        "integer": (
            '<svg class="db-type-icon" viewBox="0 0 16 16" width="14" height="14" fill="none">'
            '<text x="0" y="12" font-size="10" font-weight="700" fill="#5f6368" '
            'font-family="Arial,sans-serif" letter-spacing="-0.5">#</text>'
            '</svg>'
        ),
        # Decimal icon for float columns
        "float": (
            '<svg class="db-type-icon" viewBox="0 0 16 16" width="14" height="14" fill="none">'
            '<text x="0" y="12" font-size="7" font-weight="700" fill="#5f6368" '
            'font-family="Arial,sans-serif" letter-spacing="-0.2">1.2</text>'
            '</svg>'
        ),
        # T/F icon for boolean columns
        "boolean": (
            '<svg class="db-type-icon" viewBox="0 0 16 16" width="14" height="14" fill="none">'
            '<text x="0" y="12" font-size="7.5" font-weight="700" fill="#5f6368" '
            'font-family="Arial,sans-serif">'
            f'<tspan fill="{accent_color}">T</tspan>'
            '<tspan fill="#5f6368">/F</tspan>'
            '</text>'
            '</svg>'
        ),
        # Calendar icon for datetime columns
        "datetime": (
            '<svg class="db-type-icon" viewBox="0 0 16 16" width="14" height="14" fill="none">'
            '<rect x="1" y="3" width="14" height="12" rx="2" stroke="#5f6368" stroke-width="1.3" fill="none"/>'
            '<line x1="1" y1="7" x2="15" y2="7" stroke="#5f6368" stroke-width="1.3"/>'
            '<line x1="5" y1="1" x2="5" y2="5" stroke="#5f6368" stroke-width="1.3" stroke-linecap="round"/>'
            '<line x1="11" y1="1" x2="11" y2="5" stroke="#5f6368" stroke-width="1.3" stroke-linecap="round"/>'
            f'<rect x="4" y="9.5" width="2.5" height="2" rx="0.5" fill="{accent_color}"/>'
            '</svg>'
        ),
        # Braces icon for complex/json columns
        "complex": (
            '<svg class="db-type-icon" viewBox="0 0 16 16" width="14" height="14" fill="none">'
            '<text x="1" y="13" font-size="12" font-weight="400" fill="#5f6368" '
            'font-family="Arial,sans-serif">{}</text>'
            '</svg>'
        ),
    }
    return icons.get(dtype_category, icons["string"])


def get_sort_icon_svg() -> str:
    """Return the sort arrow SVG for column headers."""
    return (
        '<svg class="db-sort-icon" viewBox="0 0 10 14" width="8" height="12" fill="none">'
        '<path class="db-sort-asc" d="M5 0L9 5H1L5 0Z" fill="#bcc0c4"/>'
        '<path class="db-sort-desc" d="M5 14L1 9H9L5 14Z" fill="#bcc0c4"/>'
        '</svg>'
    )


def get_chevron_down_svg(size: int = 12) -> str:
    """Return a small chevron-down SVG for dropdown indicators."""
    return (
        f'<svg viewBox="0 0 10 6" width="{size}" height="{size}" fill="none" '
        f'style="vertical-align:middle;">'
        f'<path d="M1 1L5 5L9 1" stroke="#444" stroke-width="1.5" '
        f'stroke-linecap="round" stroke-linejoin="round"/>'
        f'</svg>'
    )


def get_plus_svg(size: int = 14) -> str:
    """Return a plus icon SVG."""
    return (
        f'<svg viewBox="0 0 12 12" width="{size}" height="{size}" fill="none">'
        f'<path d="M6 1V11M1 6H11" stroke="#666" stroke-width="1.5" '
        f'stroke-linecap="round"/>'
        f'</svg>'
    )


def get_download_svg() -> str:
    """Return a download icon SVG."""
    return (
        '<svg viewBox="0 0 16 16" width="14" height="14" fill="none">'
        '<path d="M8 2V10M8 10L5 7M8 10L11 7" stroke="#333" stroke-width="1.4" '
        'stroke-linecap="round" stroke-linejoin="round"/>'
        '<path d="M3 13H13" stroke="#333" stroke-width="1.4" stroke-linecap="round"/>'
        '</svg>'
    )


def get_copy_svg() -> str:
    """Return a copy icon SVG."""
    return (
        '<svg viewBox="0 0 16 16" width="14" height="14" fill="none">'
        '<rect x="5" y="5" width="8" height="9" rx="1.5" stroke="#333" stroke-width="1.2"/>'
        '<path d="M11 5V3.5A1.5 1.5 0 009.5 2H3.5A1.5 1.5 0 002 3.5V10.5A1.5 1.5 0 003.5 12H5" '
        'stroke="#333" stroke-width="1.2"/>'
        '</svg>'
    )


def get_filter_svg() -> str:
    """Return a filter funnel icon SVG."""
    return (
        '<svg viewBox="0 0 16 16" width="14" height="14" fill="none">'
        '<path d="M2 3H14L10 8.5V12L6 14V8.5L2 3Z" stroke="#333" stroke-width="1.2" '
        'stroke-linejoin="round"/>'
        '</svg>'
    )


def get_exclude_svg() -> str:
    """Return a circle-slash (exclude) icon SVG."""
    return (
        '<svg viewBox="0 0 16 16" width="14" height="14" fill="none">'
        '<circle cx="8" cy="8" r="6" stroke="#333" stroke-width="1.2"/>'
        '<line x1="3.5" y1="12.5" x2="12.5" y2="3.5" stroke="#333" stroke-width="1.2"/>'
        '</svg>'
    )


def get_panel_svg() -> str:
    """Return a side-panel toggle icon SVG."""
    return (
        '<svg viewBox="0 0 16 16" width="14" height="14" fill="none">'
        '<rect x="1" y="2" width="14" height="12" rx="2" stroke="#333" stroke-width="1.2"/>'
        '<line x1="10" y1="2" x2="10" y2="14" stroke="#333" stroke-width="1.2"/>'
        '</svg>'
    )


def get_search_svg() -> str:
    """Return a search/magnifying glass icon SVG."""
    return (
        '<svg viewBox="0 0 16 16" width="14" height="14" fill="none">'
        '<circle cx="7" cy="7" r="4.5" stroke="#888" stroke-width="1.3"/>'
        '<line x1="10.5" y1="10.5" x2="14" y2="14" stroke="#888" stroke-width="1.3" '
        'stroke-linecap="round"/>'
        '</svg>'
    )


def get_close_svg(size: int = 12) -> str:
    """Return a small X close icon SVG."""
    return (
        f'<svg viewBox="0 0 10 10" width="{size}" height="{size}" fill="none">'
        f'<path d="M2 2L8 8M8 2L2 8" stroke="#666" stroke-width="1.5" '
        f'stroke-linecap="round"/>'
        f'</svg>'
    )


def get_sun_icon_svg(size: int = 14) -> str:
    """Return a sun icon SVG for theme toggle."""
    return (
        f'<svg viewBox="0 0 16 16" width="{size}" height="{size}" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round">'
        f'<circle cx="8" cy="8" r="3.5"/>'
        f'<path d="M8 1v2M8 13v2M1 8h2M13 8h2M3.05 3.05l1.41 1.41M11.54 11.54l1.41 1.41M3.05 12.95l1.41-1.41M11.54 4.46l1.41-1.41"/>'
        f'</svg>'
    )


def get_moon_icon_svg(size: int = 14) -> str:
    """Return a moon icon SVG for theme toggle."""
    return (
        f'<svg viewBox="0 0 16 16" width="{size}" height="{size}" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round">'
        f'<path d="M14 9.5A6 6 0 116.5 2 4.5 4.5 0 0014 9.5z"/>'
        f'</svg>'
    )

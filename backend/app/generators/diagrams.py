"""Deterministic SVG diagram primitives.

Diagrams are drawn from the question's parameters — never from an image model —
so they are reproducible, accessible, and cheap. Geometry here is fixed and
deliberately *not to scale* (matching Edexcel's "Diagrams are NOT accurately
drawn" convention); only the labels change.
"""

from __future__ import annotations

# Fixed right-angled triangle. Right angle at bottom-left.
#   top-left (40,70) --- hypotenuse ---> bottom-right (260,210)
#        |                                   /
#     vertical leg                      base leg
#        |                                 /
#   bottom-left (40,210) -- base -- bottom-right (260,210)
_BL = (40, 210)  # bottom-left  (right angle)
_BR = (260, 210)  # bottom-right
_TL = (40, 70)  # top-left


def _label(text: str, x: int, y: int, variable: str, anchor: str = "middle") -> str:
    italic = ' font-style="italic"' if text == variable else ""
    return (
        f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="16" '
        f'fill="currentColor"{italic}>{text}</text>'
    )


def right_triangle_svg(
    *,
    base_label: str,
    vert_label: str,
    hyp_label: str,
    variable: str = "x",
) -> str:
    """Render a right-angled triangle with the three sides labelled.

    `base_label`  -> bottom (horizontal) side
    `vert_label`  -> left (vertical) side
    `hyp_label`   -> hypotenuse (the sloping side)
    Any label equal to `variable` is rendered in italic, like a real paper.
    """
    return (
        '<svg viewBox="0 0 300 260" xmlns="http://www.w3.org/2000/svg" '
        'role="img" font-family="-apple-system, system-ui, sans-serif">'
        f'<polygon points="{_BL[0]},{_BL[1]} {_BR[0]},{_BR[1]} {_TL[0]},{_TL[1]}" '
        'fill="none" stroke="currentColor" stroke-width="2" '
        'stroke-linejoin="round"/>'
        # right-angle marker at bottom-left
        '<polyline points="40,196 54,196 54,210" fill="none" '
        'stroke="currentColor" stroke-width="2"/>'
        + _label(base_label, 150, 232, variable)
        + _label(vert_label, 22, 145, variable)
        + _label(hyp_label, 165, 130, variable)
        + "</svg>"
    )

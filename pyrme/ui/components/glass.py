"""Glassmorphism components for Noct Map Editor.

Implements the frosted glass aesthetic using QWidget techniques.
Note: True backdrop-filter blur requires desktop-environment-specific composer
integrations or expensive parent-pixel sampling in PyQt6. We approximate this
using translucent backgrounds and CSS fallback as standard for cross-platform PyQt6 apps.
"""

from __future__ import annotations

import logging

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QPainter, QPaintEvent, QPen
from PyQt6.QtWidgets import QDockWidget, QHBoxLayout, QLabel, QWidget

from pyrme.ui.styles import section_heading_qss
from pyrme.ui.theme import THEME


class GlassPanel(QWidget):
    """A generic glass-styled panel (Obsidian Glass).

    Used for dock panels and floating windows.
    """

    def __init__(self, parent: QWidget | None = None, elevation: int = 1) -> None:
        super().__init__(parent)
        self._elevation = elevation

        # Enable translucent background rendering
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAutoFillBackground(False)

    def paintEvent(self, event: QPaintEvent | None) -> None:  # noqa: N802
        """Draw the glass background and borders."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()

        # Decide background color based on elevation
        if self._elevation == 1:
            bg_color = THEME.obsidian_glass
            radius = 8.0
        elif self._elevation == 2:
            bg_color = THEME.obsidian_glass # Could add more opacity here
            radius = 8.0
        else: # Elevation 3 (Dialogs)
            bg_color = THEME.elevated_surface
            radius = 12.0

        # Draw background
        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, radius, radius)

        # Draw 1px Ghost Border (all edges)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(THEME.ghost_border, 1))
        # Reduce rect slightly to fit border
        border_rect = rect.adjusted(0, 0, -1, -1)
        painter.drawRoundedRect(border_rect, radius, radius)

        # Draw 1px Active Border (Top edge "Rim of the glass")
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False) # precise 1px line
        painter.setPen(QPen(THEME.active_border, 1))
        # Draw a line along the top inner edge, keeping rounded corners in mind
        painter.drawLine(int(radius), 0, rect.width() - int(radius), 0)

        painter.end()


class GlassTitleBar(QWidget):
    """Custom title bar for dock widgets matching the Noct Map Editor design."""

    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedHeight(28)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(4)

        self.title_label = QLabel(title.upper())
        self.title_label.setStyleSheet(section_heading_qss())
        layout.addWidget(self.title_label)
        layout.addStretch()

    def paintEvent(self, event: QPaintEvent | None) -> None:  # noqa: N802
        """Draw the bottom separator line."""
        painter = QPainter(self)
        # 1px Ghost Border at the bottom separating header from panel body
        painter.setPen(QPen(THEME.ghost_border, 1))
        painter.drawLine(0, self.height() - 1, self.width(), self.height() - 1)
        painter.end()


class GlassDockWidget(QDockWidget):
    """A custom QDockWidget that utilizes the glassmorphism theme."""

    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(title, parent)

        self.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetFloatable |
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetClosable
        )

        # Custom title bar
        self.title_bar = GlassTitleBar(title, self)
        self.setTitleBarWidget(self.title_bar)

        # For docks, we usually rely on QSS for the main structure,
        # but we can embed a GlassPanel as its inner container.
        self._container = GlassPanel(self, elevation=1)
        self.setWidget(self._container)

    def content_widget(self) -> GlassPanel:
        """Return the inner glass container widget.

        Use this to set the widget of a dock directly, e.g.::

            dock.content_widget().setLayout(my_layout)
        """
        return self._container

    def set_inner_layout(self, layout) -> None:  # noqa: ANN001
        """Helper to set layout on the inner glass container.

        Warns if the container already has a layout assigned.
        """
        if self._container.layout() is not None:
            logging.getLogger(__name__).warning(
                "GlassDockWidget '%s': layout already set on container, "
                "replacing may cause Qt warnings.",
                self.windowTitle(),
            )
        self._container.setLayout(layout)

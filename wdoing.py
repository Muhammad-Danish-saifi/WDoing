import sys
import os
import time
from datetime import datetime

from PyQt6.QtCore import Qt, QPoint, QRect, QTimer, pyqtSignal
from PyQt6.QtGui import QIcon, QFont, QColor, QCursor, QAction
from PyQt6.QtWidgets import (
    QApplication, QWidget, QFrame, QLabel, QHBoxLayout, QVBoxLayout,
    QPlainTextEdit, QPushButton, QMenu, QSystemTrayIcon, QSizePolicy,
    QGraphicsDropShadowEffect
)

import storage

if getattr(sys, 'frozen', False):
    APP_DIR = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))

ICON_PATH = os.path.join(APP_DIR, "assets", "icon.png")
ICO_PATH = os.path.join(APP_DIR, "assets", "icon.ico")


def format_time_ago(timestamp_str):
    if not timestamp_str:
        return ""
    try:
        dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        diff = datetime.now() - dt
        seconds = int(diff.total_seconds())
        if seconds < 60:
            return "just now"
        minutes = seconds // 60
        if minutes < 60:
            return f"{minutes}m ago"
        hours = minutes // 60
        if hours < 24:
            return f"{hours}h {minutes % 60}m ago"
        days = hours // 24
        return f"{days}d ago"
    except Exception:
        return timestamp_str


def get_first_words(text, max_words=6, max_chars=32):
    if not text:
        return ""
    first_line = text.strip().split("\n")[0].strip()
    words = first_line.split()
    if len(words) <= max_words and len(first_line) <= max_chars:
        return first_line
    truncated = " ".join(words[:max_words])
    if len(truncated) > max_chars:
        truncated = truncated[:max_chars].rstrip()
    return truncated + "..."


class HoverTooltipCard(QWidget):
    """
    Sleek, modern floating tooltip card that appears smoothly on hover
    showing the full task text, timestamp, and helpful hints.
    """
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        
        self.main_frame = QFrame(self)
        self.main_frame.setObjectName("tooltipFrame")
        self.main_frame.setStyleSheet("""
            QFrame#tooltipFrame {
                background-color: #161822;
                border: 1px solid #33394d;
                border-radius: 10px;
                padding: 10px;
            }
            QLabel#badge {
                color: #38bdf8;
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 0.5px;
            }
            QLabel#timestamp {
                color: #94a3b8;
                font-size: 10px;
            }
            QLabel#fullText {
                color: #f1f5f9;
                font-size: 13px;
                font-family: 'Segoe UI', -apple-system, sans-serif;
                line-height: 1.4;
            }
            QLabel#footerHint {
                color: #64748b;
                font-size: 10px;
                border-top: 1px solid #232736;
                padding-top: 6px;
                margin-top: 4px;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(18)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 4)
        self.main_frame.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self.main_frame)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)
        
        # Header layout
        header_layout = QHBoxLayout()
        self.badge_label = QLabel("🎯 CURRENT FOCUS", self)
        self.badge_label.setObjectName("badge")
        self.time_label = QLabel("", self)
        self.time_label.setObjectName("timestamp")
        header_layout.addWidget(self.badge_label)
        header_layout.addStretch()
        header_layout.addWidget(self.time_label)
        layout.addLayout(header_layout)
        
        # Full text content
        self.text_label = QLabel(self)
        self.text_label.setObjectName("fullText")
        self.text_label.setWordWrap(True)
        self.text_label.setMaximumWidth(420)
        layout.addWidget(self.text_label)
        
        # Footer
        self.footer_label = QLabel("💡 Left-Click to edit  •  Right-Click for menu  •  Drag to reposition", self)
        self.footer_label.setObjectName("footerHint")
        layout.addWidget(self.footer_label)
        
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(8, 8, 8, 8)
        outer_layout.addWidget(self.main_frame)
    
    def set_content(self, text, updated_at):
        if not text:
            self.badge_label.setText("🎯 WHAT'S NEXT?")
            self.text_label.setText("No task active right now. Click to write what you want to do!")
            self.time_label.setText("")
        else:
            self.badge_label.setText("🎯 CURRENT FOCUS")
            self.text_label.setText(text)
            time_ago = format_time_ago(updated_at)
            self.time_label.setText(f"🕒 {time_ago}" if time_ago else "")
        self.adjustSize()


class NotepadEditor(QWidget):
    """
    Minimalist Notepad-like editor popup to quickly view & edit the task.
    Supports Ctrl+Enter / Ctrl+S to save, Esc to close, word/char counts.
    """
    task_saved = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(500, 340)
        self.drag_position = None
        self.init_ui()

    def init_ui(self):
        container = QFrame(self)
        container.setObjectName("notepadContainer")
        container.setStyleSheet("""
            QFrame#notepadContainer {
                background-color: #13141f;
                border: 1px solid #2d3148;
                border-radius: 12px;
            }
            QFrame#titleBar {
                background-color: #1a1c2b;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                border-bottom: 1px solid #282b3d;
            }
            QLabel#appTitle {
                color: #e2e8f0;
                font-size: 13px;
                font-weight: 600;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton#closeBtn {
                background: transparent;
                color: #94a3b8;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
            }
            QPushButton#closeBtn:hover {
                background-color: #ef4444;
                color: #ffffff;
            }
            QPlainTextEdit#editor {
                background-color: #13141f;
                color: #f8fafc;
                font-family: 'Cascadia Code', 'Consolas', 'Segoe UI', monospace;
                font-size: 14px;
                border: none;
                padding: 12px;
                selection-background-color: #4f46e5;
                selection-color: #ffffff;
            }
            QFrame#statusBar {
                background-color: #181926;
                border-bottom-left-radius: 12px;
                border-bottom-right-radius: 12px;
                border-top: 1px solid #232638;
                padding: 6px 12px;
            }
            QLabel#statLabel {
                color: #64748b;
                font-size: 11px;
            }
            QPushButton#actionBtn {
                background-color: #272a3e;
                color: #cbd5e1;
                border: 1px solid #383c56;
                border-radius: 6px;
                padding: 5px 14px;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton#actionBtn:hover {
                background-color: #333852;
                color: #ffffff;
            }
            QPushButton#saveBtn {
                background-color: #4f46e5;
                color: #ffffff;
                border: 1px solid #6366f1;
                border-radius: 6px;
                padding: 5px 16px;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton#saveBtn:hover {
                background-color: #4338ca;
            }
        """)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setColor(QColor(0, 0, 0, 220))
        shadow.setOffset(0, 8)
        container.setGraphicsEffect(shadow)

        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Custom Title Bar
        title_bar = QFrame(container)
        title_bar.setObjectName("titleBar")
        title_bar.setFixedHeight(38)
        tb_layout = QHBoxLayout(title_bar)
        tb_layout.setContentsMargins(14, 0, 10, 0)

        title_label = QLabel("📝 WDoing — Notepad Editor", title_bar)
        title_label.setObjectName("appTitle")
        tb_layout.addWidget(title_label)
        tb_layout.addStretch()

        close_btn = QPushButton("✕", title_bar)
        close_btn.setObjectName("closeBtn")
        close_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        close_btn.clicked.connect(self.save_and_close)
        tb_layout.addWidget(close_btn)
        main_layout.addWidget(title_bar)

        # Notepad Text Area
        self.editor = QPlainTextEdit(container)
        self.editor.setObjectName("editor")
        self.editor.setPlaceholderText(
            "Write what you are doing or what to do next...\n\n"
            "• Single line text will stay visible on the taskbar.\n"
            "• Hover over the taskbar widget to view full notes anytime.\n"
            "• Press Ctrl+Enter or click 'Save & Dock' when ready."
        )
        self.editor.textChanged.connect(self.update_stats)
        main_layout.addWidget(self.editor)

        # Status and Action Bar
        status_bar = QFrame(container)
        status_bar.setObjectName("statusBar")
        status_bar.setFixedHeight(46)
        sb_layout = QHBoxLayout(status_bar)
        sb_layout.setContentsMargins(14, 6, 14, 6)

        self.stat_label = QLabel("Words: 0 | Chars: 0", status_bar)
        self.stat_label.setObjectName("statLabel")
        sb_layout.addWidget(self.stat_label)

        sb_layout.addStretch()

        clear_btn = QPushButton("🧹 Clear", status_bar)
        clear_btn.setObjectName("actionBtn")
        clear_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        clear_btn.clicked.connect(self.clear_text)
        sb_layout.addWidget(clear_btn)

        save_btn = QPushButton("💾 Save & Dock (Ctrl+↵)", status_bar)
        save_btn.setObjectName("saveBtn")
        save_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        save_btn.clicked.connect(self.save_and_close)
        sb_layout.addWidget(save_btn)

        main_layout.addWidget(status_bar)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(10, 10, 10, 10)
        outer.addWidget(container)

    def load_task(self, text):
        self.editor.setPlainText(text or "")
        self.editor.moveCursor(self.editor.textCursor().MoveOperation.End)
        self.update_stats()

    def update_stats(self):
        text = self.editor.toPlainText().strip()
        words = len(text.split()) if text else 0
        chars = len(text)
        self.stat_label.setText(f"Words: {words} | Chars: {chars}")

    def clear_text(self):
        self.editor.clear()
        self.update_stats()
        self.editor.setFocus()

    def save_and_close(self):
        text = self.editor.toPlainText().strip()
        self.task_saved.emit(text)
        self.close()

    def keyPressEvent(self, event):
        # Ctrl + Enter or Ctrl + S to save
        if (event.modifiers() & Qt.KeyboardModifier.ControlModifier) and event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_S):
            self.save_and_close()
            event.accept()
        elif event.key() == Qt.Key.Key_Escape:
            # Auto save on escape as well for zero friction
            self.save_and_close()
            event.accept()
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and event.position().y() <= 40:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.drag_position and (event.buttons() & Qt.MouseButton.LeftButton):
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_position = None


class TaskbarWidget(QWidget):
    """
    The compact single-line widget docked on/above the Windows taskbar.
    - Shows truncated words: "🎯 Fix auth bug..."
    - Hover: Rich tooltip with full details
    - Left Click: Opens Notepad editor
    - Right Click: Context menu with position snap, history, auto-start, quit
    - Draggable: Can be placed anywhere along the taskbar
    """
    def __init__(self):
        super().__init__(
            None,
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.current_data = storage.load_data()
        self.drag_position = None
        self.is_dragging = False
        self.hover_timer = QTimer(self)
        self.hover_timer.setSingleShot(True)
        self.hover_timer.timeout.connect(self.show_tooltip)
        
        self.tooltip_card = HoverTooltipCard()
        self.notepad = NotepadEditor()
        self.notepad.task_saved.connect(self.on_task_saved)
        
        self.init_ui()
        self.init_tray()
        self.apply_position()
        self.refresh_display()

    def init_ui(self):
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        self.pill_frame = QFrame(self)
        self.pill_frame.setObjectName("pillFrame")
        self.pill_frame.setStyleSheet("""
            QFrame#pillFrame {
                background-color: rgba(18, 20, 30, 0.94);
                border: 1px solid rgba(99, 102, 241, 0.45);
                border-radius: 17px;
            }
            QFrame#pillFrame:hover {
                background-color: rgba(24, 27, 42, 0.98);
                border: 1px solid rgba(129, 140, 248, 0.85);
            }
            QLabel#indicator {
                font-size: 13px;
                padding-left: 2px;
            }
            QLabel#taskLabel {
                color: #f1f5f9;
                font-family: 'Segoe UI', -apple-system, sans-serif;
                font-size: 12px;
                font-weight: 500;
            }
            QLabel#taskLabel:hover {
                color: #38bdf8;
            }
            QLabel#dragHandle {
                color: #475569;
                font-size: 11px;
                padding-right: 4px;
            }
            QLabel#dragHandle:hover {
                color: #94a3b8;
            }
        """)

        # Drop shadow for taskbar contrast
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(16)
        shadow.setColor(QColor(0, 0, 0, 160))
        shadow.setOffset(0, 2)
        self.pill_frame.setGraphicsEffect(shadow)

        layout = QHBoxLayout(self.pill_frame)
        layout.setContentsMargins(10, 4, 10, 4)
        layout.setSpacing(6)

        # Pulse/Target Indicator Icon
        self.indicator_label = QLabel("🎯", self.pill_frame)
        self.indicator_label.setObjectName("indicator")
        layout.addWidget(self.indicator_label)

        # Task Text Label (Single line, truncated)
        self.task_label = QLabel("Click to write task...", self.pill_frame)
        self.task_label.setObjectName("taskLabel")
        layout.addWidget(self.task_label)

        # Drag grip dots
        self.grip_label = QLabel("⋮⋮", self.pill_frame)
        self.grip_label.setObjectName("dragHandle")
        self.grip_label.setToolTip("Drag to move")
        layout.addWidget(self.grip_label)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(4, 4, 4, 4)
        outer.addWidget(self.pill_frame)

        self.setFixedHeight(42)
        self.setMinimumWidth(180)
        self.setMaximumWidth(400)

    def init_tray(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
            
        self.tray_icon = QSystemTrayIcon(self)
        if os.path.exists(ICO_PATH):
            self.tray_icon.setIcon(QIcon(ICO_PATH))
        elif os.path.exists(ICON_PATH):
            self.tray_icon.setIcon(QIcon(ICON_PATH))

        tray_menu = QMenu()
        tray_menu.setStyleSheet("""
            QMenu {
                background-color: #1e1e2e;
                color: #cdd6f4;
                border: 1px solid #3b4261;
                border-radius: 8px;
                padding: 6px;
            }
            QMenu::item {
                padding: 6px 24px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #4f46e5;
                color: #ffffff;
            }
            QMenu::separator {
                height: 1px;
                background-color: #313244;
                margin: 4px 0;
            }
        """)

        edit_act = QAction("📝 Edit Task (Notepad)", self)
        edit_act.triggered.connect(self.open_editor)
        tray_menu.addAction(edit_act)

        clear_act = QAction("🧹 Clear Task", self)
        clear_act.triggered.connect(self.clear_task)
        tray_menu.addAction(clear_act)

        tray_menu.addSeparator()

        snap_menu = tray_menu.addMenu("📌 Snap Position")
        snap_menu.setStyleSheet(tray_menu.styleSheet())
        
        snap_br = QAction("Bottom Right (Above Tray)", self)
        snap_br.triggered.connect(lambda: self.snap_to("bottom-right"))
        snap_menu.addAction(snap_br)

        snap_bc = QAction("Bottom Center (Win 11 Taskbar)", self)
        snap_bc.triggered.connect(lambda: self.snap_to("bottom-center"))
        snap_menu.addAction(snap_bc)

        snap_bl = QAction("Bottom Left (Classic Start)", self)
        snap_bl.triggered.connect(lambda: self.snap_to("bottom-left"))
        snap_menu.addAction(snap_bl)

        snap_tr = QAction("Top Right", self)
        snap_tr.triggered.connect(lambda: self.snap_to("top-right"))
        snap_menu.addAction(snap_tr)

        # Windows Startup toggle
        self.startup_act = QAction("🚀 Run on Windows Startup", self, checkable=True)
        self.startup_act.setChecked(storage.is_startup_enabled())
        self.startup_act.triggered.connect(self.toggle_startup)
        tray_menu.addAction(self.startup_act)

        tray_menu.addSeparator()

        quit_act = QAction("✕ Quit WDoing", self)
        quit_act.triggered.connect(self.quit_app)
        tray_menu.addAction(quit_act)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()

    def on_tray_activated(self, reason):
        if reason in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick):
            self.open_editor()

    def refresh_display(self):
        task_text = self.current_data.get("task", "").strip()
        updated_at = self.current_data.get("updated_at", "")
        
        if not task_text:
            self.task_label.setText("Click to set what's next...")
            self.task_label.setStyleSheet("color: #64748b; font-style: italic;")
            self.indicator_label.setText("⚪")
            if hasattr(self, 'tray_icon'):
                self.tray_icon.setToolTip("WDoing — No active task (Click to set)")
        else:
            truncated = get_first_words(task_text, max_words=6, max_chars=30)
            self.task_label.setText(truncated)
            self.task_label.setStyleSheet("color: #f1f5f9; font-style: normal;")
            self.indicator_label.setText("🎯")
            if hasattr(self, 'tray_icon'):
                self.tray_icon.setToolTip(f"WDoing Focus:\n{task_text[:120]}")

        self.pill_frame.adjustSize()
        self.adjustSize()
        self.tooltip_card.set_content(task_text, updated_at)

    def apply_position(self):
        saved_pos = storage.get_saved_position()
        if saved_pos and "x" in saved_pos and "y" in saved_pos:
            self.move(saved_pos["x"], saved_pos["y"])
        else:
            self.snap_to("bottom-right")

    def snap_to(self, corner="bottom-right"):
        screen = QApplication.primaryScreen()
        if not screen:
            return
        
        # availableGeometry takes Windows taskbar into account!
        avail = screen.availableGeometry()
        full = screen.geometry()
        
        self.adjustSize()
        w = self.width()
        h = self.height()
        
        # Detect if taskbar is at bottom
        taskbar_height = full.height() - avail.height()
        
        if corner == "bottom-right":
            x = avail.right() - w - 24
            # Place right above or snug against the taskbar
            y = avail.bottom() - h - 6
        elif corner == "bottom-center":
            x = avail.left() + (avail.width() - w) // 2
            y = avail.bottom() - h - 6
        elif corner == "bottom-left":
            x = avail.left() + 24
            y = avail.bottom() - h - 6
        elif corner == "top-right":
            x = avail.right() - w - 24
            y = avail.top() + 16
        else:
            x = avail.right() - w - 24
            y = avail.bottom() - h - 6
            
        self.move(x, y)
        storage.save_position(x, y)

    def open_editor(self):
        self.tooltip_card.hide()
        current_text = self.current_data.get("task", "")
        self.notepad.load_task(current_text)
        
        # Position notepad right above or centered relative to widget
        screen = QApplication.primaryScreen().availableGeometry()
        target_x = max(screen.left() + 20, min(self.x() - 100, screen.right() - self.notepad.width() - 20))
        target_y = max(screen.top() + 40, self.y() - self.notepad.height() - 12)
        
        self.notepad.move(target_x, target_y)
        self.notepad.show()
        self.notepad.raise_()
        self.notepad.activateWindow()

    def on_task_saved(self, new_text):
        self.current_data = storage.set_current_task(new_text)
        self.refresh_display()

    def clear_task(self):
        self.current_data = storage.clear_task()
        self.refresh_display()

    def toggle_startup(self, checked):
        storage.set_startup(checked)
        if hasattr(self, 'startup_act'):
            self.startup_act.setChecked(storage.is_startup_enabled())

    def quit_app(self):
        self.tooltip_card.close()
        self.notepad.close()
        QApplication.quit()

    # --- Mouse Events & Hover Handling ---
    def enterEvent(self, event):
        # 300ms hover delay before showing tooltip to avoid jarring flashes
        self.hover_timer.start(250)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.hover_timer.stop()
        self.tooltip_card.hide()
        super().leaveEvent(event)

    def show_tooltip(self):
        if not self.isVisible() or self.notepad.isVisible():
            return
        
        task_text = self.current_data.get("task", "").strip()
        updated_at = self.current_data.get("updated_at", "")
        self.tooltip_card.set_content(task_text, updated_at)
        
        # Position tooltip card directly above the widget
        self.tooltip_card.adjustSize()
        card_w = self.tooltip_card.width()
        card_h = self.tooltip_card.height()
        
        screen = QApplication.primaryScreen().availableGeometry()
        
        # Center horizontally over widget
        card_x = self.x() + (self.width() - card_w) // 2
        card_x = max(screen.left() + 10, min(card_x, screen.right() - card_w - 10))
        
        # Place above widget, or below if too close to top
        if self.y() - card_h - 8 >= screen.top():
            card_y = self.y() - card_h - 6
        else:
            card_y = self.y() + self.height() + 6
            
        self.tooltip_card.move(card_x, card_y)
        self.tooltip_card.show()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.is_dragging = False
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            self.show_context_menu(event.globalPosition().toPoint())
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            if self.drag_position:
                delta = event.globalPosition().toPoint() - self.frameGeometry().topLeft() - self.drag_position
                if delta.manhattanLength() > 4:
                    self.is_dragging = True
                    self.tooltip_card.hide()
                    self.move(event.globalPosition().toPoint() - self.drag_position)
                    event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.is_dragging:
                # Save new dragged position
                storage.save_position(self.x(), self.y())
                self.is_dragging = False
            else:
                # Pure click -> open editor!
                self.open_editor()
            event.accept()

    def show_context_menu(self, global_pos):
        self.tooltip_card.hide()
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #161822;
                color: #e2e8f0;
                border: 1px solid #33394d;
                border-radius: 8px;
                padding: 6px;
                font-family: 'Segoe UI', sans-serif;
            }
            QMenu::item {
                padding: 6px 22px;
                border-radius: 5px;
            }
            QMenu::item:selected {
                background-color: #4f46e5;
                color: #ffffff;
            }
            QMenu::separator {
                height: 1px;
                background-color: #262a3b;
                margin: 4px 6px;
            }
        """)

        edit_act = menu.addAction("📝 Edit in Notepad")
        edit_act.triggered.connect(self.open_editor)

        clear_act = menu.addAction("🧹 Clear / Completed")
        clear_act.triggered.connect(self.clear_task)

        # Recent history submenu
        history = self.current_data.get("history", [])
        if history:
            hist_menu = menu.addMenu("🕒 Recent Tasks")
            hist_menu.setStyleSheet(menu.styleSheet())
            for item in history[:5]:
                t = item.get("task", "")
                label = get_first_words(t, max_words=5, max_chars=25)
                act = hist_menu.addAction(f"↺ {label}")
                act.triggered.connect(lambda checked, text=t: self.on_task_saved(text))

        menu.addSeparator()

        snap_menu = menu.addMenu("📌 Dock / Snap Position")
        snap_menu.setStyleSheet(menu.styleSheet())
        
        snap_br = snap_menu.addAction("Bottom Right (Taskbar)")
        snap_br.triggered.connect(lambda: self.snap_to("bottom-right"))

        snap_bc = snap_menu.addAction("Bottom Center (Win 11)")
        snap_bc.triggered.connect(lambda: self.snap_to("bottom-center"))

        snap_bl = snap_menu.addAction("Bottom Left (Start Menu)")
        snap_bl.triggered.connect(lambda: self.snap_to("bottom-left"))

        snap_tr = snap_menu.addAction("Top Right")
        snap_tr.triggered.connect(lambda: self.snap_to("top-right"))

        startup_act = menu.addAction("🚀 Start on Windows Boot")
        startup_act.setCheckable(True)
        startup_act.setChecked(storage.is_startup_enabled())
        startup_act.triggered.connect(self.toggle_startup)

        menu.addSeparator()

        quit_act = menu.addAction("✕ Exit")
        quit_act.triggered.connect(self.quit_app)

        menu.exec(global_pos)


def main():
    # Enable high DPI scaling
    app = QApplication(sys.argv)
    app.setApplicationName("WDoing")
    app.setQuitOnLastWindowClosed(False)

    if os.path.exists(ICO_PATH):
        app.setWindowIcon(QIcon(ICO_PATH))
    elif os.path.exists(ICON_PATH):
        app.setWindowIcon(QIcon(ICON_PATH))

    widget = TaskbarWidget()
    widget.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

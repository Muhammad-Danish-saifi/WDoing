# 🎯 WDoing — Windows Taskbar Focus Bar


https://github.com/user-attachments/assets/fea54717-f5de-4ffd-b5ad-76f51bf5926f



<p align="center">
  <img src="assets/icon.png" width="96" height="96" alt="WDoing Icon" />
</p>

<p align="center">
  <strong>A minimalist, zero-friction desktop focus bar docked right on your Windows Taskbar.</strong><br>
  <em>Single line. One task at a time. Zero cognitive load.</em>
</p>

<p align="center">
  <a href="https://github.com/Muhammad-Danish-saifi/WDoing/releases/latest"><img src="https://img.shields.io/github/v/release/Muhammad-Danish-saifi/WDoing?color=indigo&label=Download%20EXE" alt="Latest Release"></a>
  <img src="https://img.shields.io/badge/Platform-Windows%2010%20%2F%2011-blue" alt="Windows 10/11">
  <img src="https://img.shields.io/badge/Built%20with-PyQt6-brightgreen" alt="PyQt6">
  <img src="https://img.shields.io/badge/License-MIT-purple" alt="License">
</p>

---

## 💡 The Problem

As developers, engineers, and creators, we spend our entire day inside code editors, terminals, and browsers:

- **Flow-State Interruptions**: While deep in debugging an API or styling a component, an urgent next step pops into mind:  
  *“Right after fixing this bug, I need to refactor the auth token refresh flow.”*
- **The Overhead of Traditional Tools**: Opening Jira, Linear, Trello, or Notion takes multiple clicks, loads heavy web interfaces, and completely derails your mental focus.
- **Buried Notes Syndrome**: Opening the default Windows Notepad or Sticky Notes sounds quick, but within 10 minutes, that window gets buried under 15 VS Code workspaces, 30 browser tabs, and multiple command prompts. You forget it even exists.
- **Cognitive Exhaustion**: Trying to mentally juggle *"what am I doing now?"* and *"what should I do next?"* drains mental energy that should be going into problem-solving.

---

## ⚡ How WDoing Solves It

**WDoing** was built with a single guiding principle: **Zero friction. One task at a time. Always in sight.**

| Feature | How It Works |
| :--- | :--- |
| **📍 Taskbar Docked** | Sits unobtrusively directly on or right above the Windows taskbar (`Always-On-Top`). It’s in the one spot your eyes naturally glance at throughout the day. |
| **🔤 Single Line Truncated** | Displays just the first few words (`🎯 Fix auth token expiry...`). It never hogs screen real estate or distracts you with lengthy text. |
| **🔍 Hover Tooltip Card** | Hovering your cursor over the bar smoothly reveals a rich, dark-mode preview card with your complete multi-line notes and time elapsed (*"🕒 35m ago"*). |
| **📝 1-Click Notepad Editor** | Single-click the bar to pop open a clean, distraction-free Notepad editor. Type or paste your task, press `Ctrl + Enter` (or `Esc`), and it immediately docks back to the taskbar. |
| **🎯 Single Active Focus** | Enforces focusing on **one thing at a time**. No overwhelming backlogs, no complex Kanban columns. Just what you're doing right now or next. |
| **🖱️ Drag & Snap Anywhere** | Hold and drag the bar anywhere along your taskbar or monitors. Snaps automatically to presets (Bottom-Right, Bottom-Center, etc.) and remembers your preferred coordinates. |
| **🔒 100% Offline & Private** | Zero telemetry, zero accounts, no cloud sync needed. Persists locally in a lightweight JSON file (`wdoing_data.json`) and exports to `current_task.txt`. |

---

## 🎬 How It Looks & Works

### 1. The Taskbar Pill
A discreet, translucent pill docked near your system tray or taskbar:
```
[ 🎯 Fix auth token refresh...  ⋮⋮ ]
```

### 2. The Hover Tooltip Card
Hovering shows the full context without having to open any app:
```
┌────────────────────────────────────────────────────────┐
│ 🎯 CURRENT FOCUS                          🕒 25m ago   │
│                                                        │
│ Refactor refreshToken() in auth.service.ts to handle   │
│ 401 interceptors before processing the payment queue.  │
│                                                        │
│ 💡 Left-Click to edit  •  Right-Click for menu         │
└────────────────────────────────────────────────────────┘
```

### 3. The Minimalist Notepad Editor
Clicking the bar opens a fast, keyboard-friendly editor:
- **`Ctrl + Enter`** or **`Ctrl + S`**: Save & Dock
- **`Esc`**: Save & Close
- **`Clear`**: Clear task once done
- **Character & Word Counter** in the status bar

---

## 📦 Download & Installation

### Option 1: Standalone Portable `.exe` (Recommended)
No Python, runtime, or installation required!
1. Download **`WDoing.exe`** from the [GitHub Releases](https://github.com/Muhammad-Danish-saifi/WDoing/releases/latest) page.
2. Double-click to run. That's it!
3. *(Optional)* Right-click the bar and check **"🚀 Start on Windows Boot"** so it launches automatically when you turn on your PC.

### Option 2: Run from Source

#### Prerequisites
- Windows 10 or 11
- Python 3.10+
- PyQt6

#### Quick Setup
```bash
# Clone the repository
git clone https://github.com/Muhammad-Danish-saifi/WDoing.git
cd WDoing

# Install dependencies
pip install -r requirements.txt

# Run the app
python wdoing.py
```

Or double-click `run_silent.vbs` to launch in the background without any console window.

---

## ⌨️ Shortcuts & Controls

| Action | Control | Description |
| :--- | :--- | :--- |
| **Open Editor** | `Left-Click` on Bar | Opens the Notepad editor to write or edit your task. |
| **View Full Task** | `Hover` cursor on Bar | Smoothly displays the rich tooltip card with full task & elapsed time. |
| **Move Position** | `Click & Drag` on Bar | Move the bar anywhere on your taskbar or screen; position auto-saves. |
| **Save & Dock** | `Ctrl + Enter` or `Ctrl + S` | Instantly saves your task in the editor and docks to taskbar. |
| **Close Editor** | `Esc` | Auto-saves and closes the editor back to the taskbar. |
| **Context Menu** | `Right-Click` on Bar | Quick options for Snap Presets, Recent Tasks, Auto-Start, and Exit. |
| **Tray Icon** | `Click / Double-Click` | Toggle editor from Windows notification tray. |

---

## 🛠️ Building from Source (.exe)

If you'd like to compile the standalone binary yourself using PyInstaller:

```bash
# Run the included build script
build_exe.bat
```
The output executable will be created in `dist/`.

---

## 📂 Project Architecture

```
WDoing/
├── assets/
│   ├── icon.ico             # Windows Application Icon
│   └── icon.png             # High-res App Logo
├── wdoing.py                # Core PyQt6 UI: TaskbarWidget, TooltipCard, NotepadEditor
├── storage.py               # Local JSON persistence & Windows Registry auto-start
├── requirements.txt         # Dependencies (PyQt6)
├── run.bat                  # Batch launcher
├── run_silent.vbs           # Zero-console background launcher
├── build_exe.bat            # PyInstaller compilation script
├── .gitignore               # Clean git exclusions
└── README.md                # Documentation & Guide
```

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

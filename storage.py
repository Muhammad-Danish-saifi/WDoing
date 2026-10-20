import os
import json
import time
import winreg
from datetime import datetime

import sys

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_FILE = os.path.join(BASE_DIR, "wdoing_data.json")
TEXT_FILE = os.path.join(BASE_DIR, "current_task.txt")
APP_NAME = "WDoing"

DEFAULT_DATA = {
    "task": "Subha coding shuru: pehla task yahan likhein...",
    "updated_at": "",
    "created_at": "",
    "is_completed": False,
    "position": None,  # None means auto-calculate on taskbar
    "history": [],
    "settings": {
        "always_on_top": True,
        "max_words": 6,
        "opacity": 0.95,
        "snap_corner": "bottom-right"
    }
}

def load_data():
    if not os.path.exists(DATA_FILE):
        data = DEFAULT_DATA.copy()
        data["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data["updated_at"] = data["created_at"]
        save_data(data)
        return data
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # merge with defaults if keys missing
            for k, v in DEFAULT_DATA.items():
                if k not in data:
                    data[k] = v
            return data
    except Exception as e:
        print(f"Error loading data: {e}")
        return DEFAULT_DATA.copy()

def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Also sync to plain text file
        task_text = data.get("task", "").strip()
        with open(TEXT_FILE, "w", encoding="utf-8") as f:
            f.write(task_text)
    except Exception as e:
        print(f"Error saving data: {e}")

def set_current_task(task_text):
    data = load_data()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    old_task = data.get("task", "").strip()
    
    # Save old to history if different
    if old_task and old_task != task_text.strip():
        history = data.get("history", [])
        history.insert(0, {
            "task": old_task,
            "archived_at": now_str
        })
        data["history"] = history[:15]  # Keep last 15
        
    data["task"] = task_text.strip()
    data["updated_at"] = now_str
    data["is_completed"] = False
    save_data(data)
    return data

def clear_task():
    data = load_data()
    old_task = data.get("task", "").strip()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if old_task:
        history = data.get("history", [])
        history.insert(0, {
            "task": old_task,
            "archived_at": now_str
        })
        data["history"] = history[:15]
    data["task"] = ""
    data["updated_at"] = now_str
    data["is_completed"] = False
    save_data(data)
    return data

def save_position(x, y):
    data = load_data()
    data["position"] = {"x": int(x), "y": int(y)}
    save_data(data)

def get_saved_position():
    data = load_data()
    return data.get("position")

def is_startup_enabled():
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_READ
        )
        try:
            val, _ = winreg.QueryValueEx(key, APP_NAME)
            winreg.CloseKey(key)
            return bool(val)
        except FileNotFoundError:
            winreg.CloseKey(key)
            return False
    except Exception:
        return False

def set_startup(enable: bool, exe_path: str = None):
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        if enable:
            if getattr(sys, 'frozen', False):
                cmd = f'"{sys.executable}"'
            elif exe_path:
                cmd = f'"{exe_path}"'
            else:
                # If running as python script
                script_path = os.path.join(BASE_DIR, "wdoing.py")
                pythonw = sys.executable.replace("python.exe", "pythonw.exe")
                cmd = f'"{pythonw}" "{script_path}"'
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, cmd)
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"Error setting startup: {e}")
        return False

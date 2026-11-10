"""Launch Image Restore Studio with a persistent diagnostic log."""
import os, sys, traceback, datetime
from pathlib import Path

def log_path():
    d = Path.home() / "Library" / "Logs" / "Image Restore Studio"
    d.mkdir(parents=True, exist_ok=True)
    return d / "startup.log"

def main():
    try:
        import tkinter
        from PIL import Image, ImageTk
        if "--self-test" in sys.argv:
            print("SELF-TEST PASS: Python, Tkinter and Pillow import successfully")
            return
        from app import Studio
        window = Studio()
        window.mainloop()
    except Exception as exc:
        report = datetime.datetime.utcnow().isoformat() + "Z\n" + traceback.format_exc()
        try:
            with log_path().open("a", encoding="utf-8") as f:
                f.write(report + "\n")
        except Exception:
            pass
        print(report, file=sys.stderr)
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Image Restore Studio could not start",
                "Launch failed. Diagnostic details have been saved to:\n" +
                str(log_path()) + "\n\n" + str(exc))
            root.destroy()
        except Exception:
            pass
        sys.exit(1)

if __name__ == "__main__":
    main()

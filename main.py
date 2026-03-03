import tkinter as tk
from tkinter import ttk, messagebox
import psutil
import ctypes
import subprocess
import os
import threading
import time
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from matplotlib import style

style.use("dark_background")
DRIVE_REMOVABLE = 2

class MatrixUSBManager:
    def __init__(self, root):
        self.root = root
        self.root.title("AUGION 👁 USB Hardware Control PRO MAX")
        self.root.geometry("1350x900")
        self.root.configure(bg="#1b1b1b")

        self.usb_drives = {}
        self.usage_history = []
        self.max_history = 30

        self.create_ui()
        self.auto_refresh()
        self.update_live_graph()

    # -------------------------
    # SYSTEM FUNCTIONS
    # -------------------------
    def get_drive_type(self, letter):
        return ctypes.windll.kernel32.GetDriveTypeW(f"{letter}:\\")

    def get_volume_label(self, letter):
        volume_name = ctypes.create_unicode_buffer(1024)
        ctypes.windll.kernel32.GetVolumeInformationW(
            ctypes.c_wchar_p(f"{letter}:\\"), volume_name,
            ctypes.sizeof(volume_name), None, None, None, None, 0
        )
        return volume_name.value if volume_name.value else "No Name"

    def get_filesystem(self, letter):
        fs_name = ctypes.create_unicode_buffer(1024)
        ctypes.windll.kernel32.GetVolumeInformationW(
            ctypes.c_wchar_p(f"{letter}:\\"), None, 0, None, None, None,
            fs_name, ctypes.sizeof(fs_name)
        )
        return fs_name.value

    def detect_usb_version(self, read_speed):
        if read_speed < 40:
            return "USB 2.0"
        elif read_speed < 400:
            return "USB 3.x"
        else:
            return "USB 4"

    def format_bytes(self, size):
        for unit in ["B","KB","MB","GB","TB"]:
            if size < 1024: return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} PB"

    def get_usb_drives(self):
        drives = {}
        partitions = psutil.disk_partitions(all=False)
        for p in partitions:
            letter = p.device.replace("\\","").replace(":","")
            if self.get_drive_type(letter) == DRIVE_REMOVABLE:
                usage = psutil.disk_usage(p.mountpoint)
                drives[letter] = {
                    "mountpoint": p.mountpoint,
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent": usage.percent,
                    "label": self.get_volume_label(letter),
                    "fs": self.get_filesystem(letter)
                }
        return drives

    # -------------------------
    # UI CREATION
    # -------------------------
    def create_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#111111", height=60)
        header.pack(fill="x")
        root.iconbitmap("app.ico") 
        tk.Label(header, text="AUGIONS 👁 USB CONTROLLER", bg="#111111", fg="#00ff88",
                 font=("Consolas", 24, "bold")).pack(pady=10)

        # Notebook
        style_tt = ttk.Style()
        style_tt.theme_use("clam")
        style_tt.configure("TNotebook.Tab", background="#222222", foreground="lime", font=("Consolas",12,"bold"))
        style_tt.map("TNotebook.Tab", background=[("selected", "#333333")])
        self.tab_control = ttk.Notebook(self.root, style="TNotebook")
        self.tab_control.pack(expand=1, fill="both")

        # ----------------- DASHBOARD TAB -----------------
        self.tab_dashboard = tk.Frame(self.tab_control, bg="#1b1b1b")
        self.tab_control.add(self.tab_dashboard, text="Dashboard")

        self.info_frame = tk.LabelFrame(self.tab_dashboard, text="USB Info", bg="#1b1b1b", fg="#00ff88",
                                        font=("Consolas",12,"bold"), padx=15, pady=15)
        self.info_frame.pack(fill="x", padx=20, pady=20)

        self.combo = ttk.Combobox(self.info_frame, state="readonly", width=50)
        self.combo.pack(pady=10)
        self.combo.bind("<<ComboboxSelected>>", self.update_info)

        self.info_label = tk.Label(self.info_frame, text="", bg="#1b1b1b", fg="#00ff88",
                                   font=("Consolas",11), justify="left")
        self.info_label.pack(pady=5)

        style_tt.configure("green.Horizontal.TProgressbar", background="#00ff88", troughcolor="#333333", thickness=25)
        self.progress = ttk.Progressbar(self.info_frame, length=600, style="green.Horizontal.TProgressbar")
        self.progress.pack(pady=10)

        btn_frame = tk.Frame(self.info_frame, bg="#1b1b1b")
        btn_frame.pack(pady=15)
        self.create_modern_button(btn_frame, "Refresh", self.refresh)
        self.create_modern_button(btn_frame, "Benchmark", self.speed_test)
        self.create_modern_button(btn_frame, "Analyse", self.run_stats)
        self.create_modern_button(btn_frame, "Toggle Cache", self.toggle_write_cache)

        # ----------------- USB OVERVIEW TAB -----------------
        self.tab_overview = tk.Frame(self.tab_control, bg="#1b1b1b")
        self.tab_control.add(self.tab_overview, text="USB Overview")

        columns = ("Letter","Name","Filesystem","Total","Used","Free","Usage %","Bus")
        self.tree = ttk.Treeview(self.tab_overview, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        self.tree.pack(padx=20, pady=20, fill="x")

        # ----------------- BENCHMARK TAB -----------------
        self.tab_benchmark = tk.Frame(self.tab_control, bg="#1b1b1b")
        self.tab_control.add(self.tab_benchmark, text="Benchmark")

        self.fig = Figure(figsize=(10,5), dpi=100)
        self.ax_live = self.fig.add_subplot(211)
        self.ax_bench = self.fig.add_subplot(212)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.tab_benchmark)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, pady=15)

        # ----------------- STATUS BAR -----------------
        self.status = tk.Label(self.root, text="System Ready", bg="#111111", fg="#00ff88",
                               anchor="w", font=("Consolas",10,"bold"))
        self.status.pack(side="bottom", fill="x")

    def create_modern_button(self, parent, text, command):
        btn = tk.Button(parent, text=text, command=command, bg="#111111", fg="#00ff88",
                        activebackground="#00ff88", activeforeground="#111111",
                        font=("Consolas",11,"bold"), bd=0, relief="ridge", width=18, pady=5)
        btn.pack(side="left", padx=7)

        def on_enter(e):
            btn['bg'] = "#00ff88"
            btn['fg'] = "#111111"
        def on_leave(e):
            btn['bg'] = "#111111"
            btn['fg'] = "#00ff88"

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

    # -------------------------
    # CORE FUNCTIONS
    # -------------------------
    def refresh(self):
        self.usb_drives = self.get_usb_drives()
        drive_list = [f"{k}: ({v['label']}) - {v['fs']}" for k,v in self.usb_drives.items()]
        self.combo["values"] = drive_list
        if drive_list:
            self.combo.current(0)
            self.update_info()
        self.update_tree()

    def auto_refresh(self):
        self.refresh()
        self.root.after(5000, self.auto_refresh)

    def update_info(self, event=None):
        selected = self.combo.get()
        if not selected: return
        letter = selected.split(":")[0]
        d = self.usb_drives.get(letter)
        if not d: return
        info = (f"Name: {d['label']}\nFilesystem: {d['fs']}\n"
                f"Total: {self.format_bytes(d['total'])}\nUsed: {self.format_bytes(d['used'])}\n"
                f"Free: {self.format_bytes(d['free'])}\nUsage: {d['percent']}%")
        self.info_label.config(text=info)
        self.progress["value"] = d["percent"]

    def update_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for letter, d in self.usb_drives.items():
            bus = self.detect_usb_version(d['percent']*5)
            self.tree.insert("", "end", values=(
                letter, d['label'], d['fs'],
                self.format_bytes(d['total']),
                self.format_bytes(d['used']),
                self.format_bytes(d['free']),
                f"{d['percent']}%", bus
            ))

    def update_live_graph(self):
        selected = self.combo.get()
        if selected:
            letter = selected.split(":")[0]
            d = self.usb_drives.get(letter)
            if d:
                self.usage_history.append(d["percent"])
                if len(self.usage_history) > self.max_history:
                    self.usage_history.pop(0)

        self.ax_live.clear()
        if self.usage_history:
            x = np.arange(len(self.usage_history))
            y = np.array(self.usage_history)
            self.ax_live.fill_between(x, y, color='lime', alpha=0.3)
            self.ax_live.plot(x, y, color='lime', linewidth=2)
        self.ax_live.set_title("Live USB Usage %")
        self.ax_live.set_ylim(0,100)
        self.canvas.draw()
        self.root.after(2000, self.update_live_graph)

    def speed_test(self):
        threading.Thread(target=self._run_speed_test, daemon=True).start()

    def _run_speed_test(self):
        selected = self.combo.get()
        if not selected: return
        letter = selected.split(":")[0]
        test_file = f"{letter}:\\benchmark.tmp"
        size = 200*1024*1024
        chunk = b"\0" * (4*1024*1024)
        self.status.config(text="Running Benchmark...")

        try:
            start = time.time()
            with open(test_file,"wb",buffering=0) as f:
                for _ in range(size//len(chunk)):
                    f.write(chunk)
            write_time = time.time()-start

            start = time.time()
            with open(test_file,"rb") as f:
                f.read()
            read_time = time.time()-start
            os.remove(test_file)

            write_speed = (size/1024/1024)/write_time
            read_speed = (size/1024/1024)/read_time

            self.ax_bench.clear()
            bars = ["Write MB/s","Read MB/s"]
            values = [write_speed, read_speed]
            colors = ['#00ff88','#00cc55']
            self.ax_bench.bar(bars, values, color=colors, alpha=0.7)
            self.ax_bench.set_title("Benchmark Result")
            self.canvas.draw()
        except Exception as e:
            messagebox.showerror("Error",str(e))
        self.status.config(text="Benchmark Complete")

    def run_stats(self):
        threading.Thread(target=self._analyse_stats, daemon=True).start()

    def _analyse_stats(self):
        selected = self.combo.get()
        if not selected: return
        letter = selected.split(":")[0]
        root_path = f"{letter}:\\"
        file_count, folder_count = 0,0
        for root, dirs, files in os.walk(root_path):
            file_count += len(files)
            folder_count += len(dirs)
        messagebox.showinfo("Analyse", f"Files: {file_count}\nFolders: {folder_count}")

    def toggle_write_cache(self):
        try:
            subprocess.run("wmic diskdrive set WriteCacheEnabled=True", shell=True)
            messagebox.showinfo("Write Cache","Write Cache aktiviert (Admin nötig)")
        except Exception as e:
            messagebox.showerror("Error",str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = MatrixUSBManager(root)
    root.mainloop()
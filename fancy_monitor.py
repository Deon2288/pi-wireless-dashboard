from tkinter import *
from PIL import Image, ImageTk
import csv
import os

CSV_PATH = "/tmp/display_data.csv"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def load_image(name, size=None):
    path = os.path.join(SCRIPT_DIR, name)
    img = Image.open(path)
    if size:
        img = img.resize(size, Image.LANCZOS)
    return ImageTk.PhotoImage(img)


def read_data():
    default = {
        "SIG1": "", "CONN1": "", "SIG2": "", "CONN2": "",
        "SSID2G": "", "SIG2G": "", "CLIENTS2G": "0",
        "SSID5G": "", "SIG5G": "", "CLIENTS5G": "0",
        "BT": "unavailable", "GPS": "unavailable",
        "GPSLAT": "", "GPSLONG": "", "BATTERY": "100",
    }
    if not os.path.exists(CSV_PATH):
        return default
    try:
        with open(CSV_PATH, "r") as f:
            rows = list(csv.reader(f))
        if not rows:
            return default
        row = rows[0]
        def col(i, fallback=""):
            return row[i] if len(row) > i else fallback
        return {
            "SIG1":      col(0),
            "CONN1":     col(1),
            "SIG2":      col(2),
            "CONN2":     col(3),
            "SSID2G":    col(4),
            "SIG2G":     col(5),
            "CLIENTS2G": col(6, "0"),
            "SSID5G":    col(7),
            "SIG5G":     col(8),
            "CLIENTS5G": col(9, "0"),
            "BT":        col(10, "unavailable"),
            "GPS":       col(11, "unavailable"),
            "GPSLAT":    col(12),
            "GPSLONG":   col(13),
            "BATTERY":   col(14, "100"),
        }
    except Exception:
        return default


def pick_battery_image(battery_pct):
    try:
        pct = int(battery_pct)
    except (ValueError, TypeError):
        pct = 100
    if pct > 60:
        return 0  # green
    elif pct > 30:
        return 1  # yellow
    elif pct > 10:
        return 2  # red
    else:
        return 3  # empty


root = Tk()
root.geometry("800x480")
root.configure(bg="#082567")
root.title("Wireless Dashboard")

bluetooth_img = load_image("bluetooth_logo.png", (80, 80))
gps_img = load_image("gps_icon.png", (120, 120))
battery_imgs = [
    load_image("battery_green.png",  (90, 60)),
    load_image("battery_yellow.png", (90, 60)),
    load_image("battery_red.png",    (90, 60)),
    load_image("battery_empty.png",  (90, 60)),
]

# Persistent widgets — avoids destroying/recreating every 3 s (memory leak fix)
canvas = Canvas(root, width=800, height=480, bg="#082567", highlightthickness=0)
canvas.place(x=0, y=0)

lbl_btimg    = Label(root, image=bluetooth_img, bg="#082567")
lbl_btonoff  = Label(root, font=("Helvetica", 28, "bold"), bg="#082567", fg="white")
lbl_gpsimg   = Label(root, image=gps_img, bg="#082567")
lbl_gpscords = Label(root, font=("Helvetica", 16, "bold"), bg="#082567", fg="white")
lbl_batt     = Label(root, image=battery_imgs[0], bg="#082567")
lbl_batt_pct = Label(root, font=("Helvetica", 16, "bold"), bg="#082567", fg="white")

lbl_btimg.place(x=70,  y=260)
lbl_btonoff.place(x=170, y=275)
lbl_gpsimg.place(x=400, y=245)
lbl_gpscords.place(x=530, y=265)
lbl_batt.place(x=330, y=400)
lbl_batt_pct.place(x=432, y=415)


def draw_dashboard():
    data = read_data()

    canvas.delete("all")

    # Title
    canvas.create_text(400, 25, text="WIRELESS DASHBOARD",
                       fill="white", font=("Helvetica", 22, "bold"))

    # --- 2.4 GHz ---
    clients2g = int(data["CLIENTS2G"]) if data["CLIENTS2G"].isdigit() else 0
    canvas.create_oval(60, 45, 260, 210, fill="#1a2767", outline="#355be6", width=8)
    angle2g = min(100, clients2g * 10) * 3.6
    if angle2g > 0:
        canvas.create_arc(60, 45, 260, 210, start=90, extent=-angle2g,
                          fill="#1c87ff", outline="", width=0)
    canvas.create_oval(100, 75, 220, 180, fill="white", outline="")
    canvas.create_text(160, 127, text=f"{clients2g * 10}%",
                       font=("Helvetica", 18, "bold"), fill="#082567")
    canvas.create_text(160, 220, text="WI-FI 2.4 GHz",
                       font=("Helvetica", 14), fill="white")
    canvas.create_text(160, 240, text=f"Clients: {clients2g}",
                       font=("Helvetica", 12), fill="white")
    if data["SSID2G"]:
        canvas.create_text(160, 258, text=f"SSID: {data['SSID2G']}",
                           font=("Helvetica", 11), fill="#aaccff")
    if data["SIG2G"]:
        canvas.create_text(160, 275, text=f"Signal: {data['SIG2G']} dBm",
                           font=("Helvetica", 11), fill="#aaccff")

    # --- 5 GHz ---
    clients5g = int(data["CLIENTS5G"]) if data["CLIENTS5G"].isdigit() else 0
    canvas.create_oval(540, 45, 740, 210, fill="#1a2767", outline="#355be6", width=8)
    angle5g = min(100, clients5g * 10) * 3.6
    if angle5g > 0:
        canvas.create_arc(540, 45, 740, 210, start=90, extent=-angle5g,
                          fill="#1c87ff", outline="", width=0)
    canvas.create_oval(580, 75, 700, 180, fill="white", outline="")
    canvas.create_text(640, 127, text=f"{clients5g * 10}%",
                       font=("Helvetica", 18, "bold"), fill="#082567")
    canvas.create_text(640, 220, text="WI-FI 5 GHz",
                       font=("Helvetica", 14), fill="white")
    canvas.create_text(640, 240, text=f"Clients: {clients5g}",
                       font=("Helvetica", 12), fill="white")
    if data["SSID5G"]:
        canvas.create_text(640, 258, text=f"SSID: {data['SSID5G']}",
                           font=("Helvetica", 11), fill="#aaccff")
    if data["SIG5G"]:
        canvas.create_text(640, 275, text=f"Signal: {data['SIG5G']} dBm",
                           font=("Helvetica", 11), fill="#aaccff")

    # --- Bluetooth ---
    lbl_btonoff.config(text=data["BT"].upper())

    # --- GPS ---
    gps_lat  = data['GPSLAT']  or '--'
    gps_lon  = data['GPSLONG'] or '--'
    gps_text = f"Long: {gps_lon}\nLat:  {gps_lat}"
    lbl_gpscords.config(text=gps_text)

    # --- Battery ---
    batt_idx = pick_battery_image(data["BATTERY"])
    lbl_batt.config(image=battery_imgs[batt_idx])
    lbl_batt_pct.config(text=f"{data['BATTERY']}%")

    root.after(3000, draw_dashboard)


draw_dashboard()
root.mainloop()

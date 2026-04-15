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
        img = img.resize(size, Image.ANTIALIAS)
    return ImageTk.PhotoImage(img)

def read_data():
    if not os.path.exists(CSV_PATH):
        return {
            "SIG1": "", "CONN1": "", "SIG2": "", "CONN2": "",
            "SSID2G": "", "SIG2G": "", "CLIENTS2G": "0",
            "SSID5G": "", "SIG5G": "", "CLIENTS5G": "0",
            "BT": "unavailable", "GPS": "unavailable",
            "GPSLAT": "", "GPSLONG": ""
        }
    with open(CSV_PATH, 'r') as f:
        row = list(csv.reader(f))[0]
        return {
            "SIG1": row[0], "CONN1": row[1], "SIG2": row[2], "CONN2": row[3],
            "SSID2G": row[4], "SIG2G": row[5], "CLIENTS2G": row[6],
            "SSID5G": row[7], "SIG5G": row[8], "CLIENTS5G": row[9],
            "BT": row[10], "GPS": row[11], "GPSLAT": row[12], "GPSLONG": row[13]
        }

root = Tk()
root.geometry("800x480")
root.configure(bg='#082567')
root.title("Wireless Dashboard")

bluetooth_img = load_image("bluetooth_logo.png", (80, 80))
gps_img = load_image("gps_icon.png", (120, 120))
battery_imgs = [
    load_image("battery_green.png", (90, 60)),
    load_image("battery_yellow.png", (90, 60)),
    load_image("battery_red.png", (90, 60)),
    load_image("battery_empty.png", (90, 60)),
]

def draw_dashboard():
    data = read_data()
    for widget in root.winfo_children():
        if isinstance(widget, Canvas) or isinstance(widget, Label):
            widget.destroy()
    canvas = Canvas(root, width=800, height=480, bg="#082567", highlightthickness=0)
    canvas.place(x=0, y=0)
    clients2g = int(data["CLIENTS2G"]) if data["CLIENTS2G"].isdigit() else 0
    canvas.create_oval(80, 40, 240, 200, fill="#1a2767", outline="#355be6", width=8)
    angle2g = min(100, clients2g*10) * 3.6
    if angle2g > 0:
        canvas.create_arc(80, 40, 240, 200, start=90, extent=-angle2g, fill="#1c87ff", outline="", width=0)
    canvas.create_oval(110, 70, 210, 170, fill="white", outline="")
    canvas.create_text(160, 120, text=f"{clients2g*10}%", font=("Helvetica", 20, "bold"), fill="#082567")
    canvas.create_text(160, 190, text="WI-FI 2.4GHz", font=("Helvetica", 15), fill="white")
    canvas.create_text(160, 215, text=f"Clients Connected: {clients2g}", font=("Helvetica", 13), fill="white")

    clients5g = int(data["CLIENTS5G"]) if data["CLIENTS5G"].isdigit() else 0
    canvas.create_oval(560, 40, 720, 200, fill="#1a2767", outline="#355be6", width=8)
    angle5g = min(100, clients5g*10) * 3.6
    if angle5g > 0:
        canvas.create_arc(560, 40, 720, 200, start=90, extent=-angle5g, fill="#1c87ff", outline="", width=0)
    canvas.create_oval(590, 70, 690, 170, fill="white", outline="")
    canvas.create_text(640, 120, text=f"{clients5g*10}%", font=("Helvetica", 20, "bold"), fill="#082567")
    canvas.create_text(640, 190, text="WI-FI 5GHz", font=("Helvetica", 15), fill="white")
    canvas.create_text(640, 215, text=f"Clients Connected: {clients5g}", font=("Helvetica", 13), fill="white")

    lbl_btimg = Label(root, image=bluetooth_img, bg="#082567")
    lbl_btimg.place(x=70, y=260)
    lbl_btonoff = Label(root, text=f"{data['BT'].upper()}", font=('Helvetica', 28, "bold"), bg='#082567', fg="white")
    lbl_btonoff.place(x=170, y=275)

    lbl_gpsimg = Label(root, image=gps_img, bg='#082567')
    lbl_gpsimg.place(x=400, y=245)
    gps_text = f"Long: {data['GPSLONG'] or '--'}\nLat : {data['GPSLAT'] or '--'}"
    lbl_gpscords = Label(root, text=gps_text, font=('Helvetica', 20, "bold"), bg='#082567', fg="white")
    lbl_gpscords.place(x=530, y=275)

    for i in range(4):
        lbl_batt = Label(root, image=battery_imgs[i], bg='#082567')
        lbl_batt.place(x=220 + i*100, y=400)

    canvas.create_text(400, 30, text="WIRELESS DASHBOARD", fill="white", font=("Helvetica", 24, "bold"))
    root.after(3000, draw_dashboard)

draw_dashboard()
root.mainloop()

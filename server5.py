import socket
import ssl
import threading
import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime
import time

HOST = "0.0.0.0"
PORT = 9999


# ---------------- BACKEND ENGINE ---------------- #

class ServerCore:
    def __init__(self):
        self.clients = []
        self.appliances = {a: False for a in ["LIGHT", "AC", "FAN 1", "FAN 2", "GYSER", "HEATER"]}
        self.schedules = []
        self.users = {"tulika": "123", "admin": "admin", "meghana": "123", "client": "client"}

        self.commands = {
            "LOGIN": self.login,
            "ADD": self.add,
            "REMOVE": self.remove,
            "STATUS": self.status,
            "TIMER": self.timer,
            "SCHEDULE": self.schedule
        }

        threading.Thread(target=self.scheduler_loop, daemon=True).start()

    # ---------- NETWORK ---------- #

    def start(self):
        threading.Thread(target=self.run_server, daemon=True).start()
        log("[SERVER STARTED]")

    def run_server(self):
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile="server.crt", keyfile="server.key")
        context.load_verify_locations("ca.crt")
        context.verify_mode = ssl.CERT_REQUIRED

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((HOST, PORT))
        server.listen(5)
        log(f"[LISTENING] {HOST}:{PORT}")

        while True:
            conn, addr = server.accept()
            try:
                ssl_conn = context.wrap_socket(conn, server_side=True)
                self.clients.append(ssl_conn)
                log(f"[NEW CLIENT] {addr}")
                threading.Thread(target=self.client_loop, args=(ssl_conn, addr), daemon=True).start()
            except:
                conn.close()

    def client_loop(self, conn, addr):
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    break
                msg = data.decode().strip()
                log(f"[{addr}] {msg}")
                self.dispatch(msg, conn)
            except:
                break

        conn.close()
        if conn in self.clients:
            self.clients.remove(conn)
        log(f"[DISCONNECTED] {addr}")

    def broadcast(self, message):
        for c in self.clients[:]:
            try:
                c.sendall(message.encode())
            except:
                self.clients.remove(c)

    # ---------- COMMAND ROUTER ---------- #

    def dispatch(self, msg, conn):
        parts = msg.split()
        if not parts:
            return

        cmd = parts[0].upper()
        if cmd in self.commands:
            self.commands[cmd](parts, conn)
        else:
            self.direct(parts)

    # ---------- COMMANDS ---------- #

    def login(self, parts, conn):
        if len(parts) != 3:
            return
        user, pwd = parts[1], parts[2]

        if self.users.get(user) == pwd:
            conn.sendall("LOGIN SUCCESS".encode())
            self.status(parts, conn)
            log(f"[LOGIN SUCCESS] {user}")
        else:
            conn.sendall("LOGIN FAILED".encode())
            log(f"[LOGIN FAILED] {user}")

    def add(self, parts, _):
        name = " ".join(parts[1:]).upper()
        if name not in self.appliances:
            self.appliances[name] = False
            appliances.append(name)
            draw_appliances()
            self.broadcast(f"ADDED {name}")

    def remove(self, parts, _):
        name = " ".join(parts[1:]).upper()
        if name in self.appliances:
            del self.appliances[name]
            if name in appliances:
                appliances.remove(name)
            draw_appliances()
            self.broadcast(f"{name} REMOVED")

    def status(self, _, conn):
        report = "\n".join([f"{k}: {'ON' if v else 'OFF'}" for k, v in self.appliances.items()])
        try:
            conn.sendall(f"[STATUS]\n{report}".encode())
        except:
            pass

    def timer(self, parts, _):
        if len(parts) < 4:
            return

        name, state, secs = parts[1].upper(), parts[2].upper(), int(parts[3])

        def task():
            if name in self.appliances:
                self.appliances[name] = (state == "ON")
                draw_appliances()
                self.broadcast(f"{name} {state}")
                log(f"[TIMER DONE] {name}")

        threading.Timer(secs, task).start()
        log(f"[TIMER SET] {name} in {secs}s")

    def schedule(self, parts, _):
        if len(parts) < 4:
            return

        name, state, t = parts[1].upper(), parts[2].upper(), parts[3]
        self.schedules.append((name, state, t))
        log(f"[SCHEDULED] {name} at {t}")

    def direct(self, parts):
        name = " ".join(parts[:-1]).upper()
        state = parts[-1].upper()

        if name in self.appliances:
            self.appliances[name] = (state == "ON")
            draw_appliances()
            self.broadcast(f"{name} {state}")

    # ---------- SCHEDULER ---------- #

    def scheduler_loop(self):
        while True:
            now = datetime.now().strftime("%H:%M")

            for item in self.schedules[:]:
                name, state, t = item
                if now >= t:
                    if name in self.appliances:
                        self.appliances[name] = (state == "ON")
                        draw_appliances()
                        self.broadcast(f"{name} {state}")
                        log(f"[SCHEDULE TRIGGERED] {name}")
                    self.schedules.remove(item)

            time.sleep(1)


core = ServerCore()


root = tk.Tk()
root.title("Home Automation Switch Server")
root.configure(bg="black")
root.geometry("360x640")

title = tk.Label(root, text="Home Automation Server", font=("Arial", 14, "bold"), fg="white", bg="black")
title.pack(pady=10)

log_box = scrolledtext.ScrolledText(root, height=10, width=58, bg="white", fg="black", font=("Arial", 10))
log_box.pack(pady=5)

appliances = ["LIGHT", "AC", "FAN 1", "FAN 2", "GYSER", "HEATER"]

appliance_frame = tk.Frame(root, bg="black")
appliance_frame.pack(pady=10)


def draw_appliances():
    for widget in appliance_frame.winfo_children():
        widget.destroy()

    for i, appliance in enumerate(appliances):
        state = core.appliances.get(appliance, False)

        tk.Label(appliance_frame, text=appliance, bg="black", fg="white",
                 font=("Arial", 10)).grid(row=i, column=0, padx=10, pady=4, sticky="w")

        btn = tk.Button(appliance_frame,
                        text="ON" if state else "OFF",
                        bg="green" if state else "red",
                        fg="white", width=6,
                        command=lambda a=appliance: toggle(a))
        btn.grid(row=i, column=1, padx=10, pady=4)


def toggle(appliance):
    core.appliances[appliance] = not core.appliances[appliance]
    draw_appliances()
    core.broadcast(f"{appliance} {'ON' if core.appliances[appliance] else 'OFF'}")


def log(message):
    print(message)
    log_box.insert(tk.END, f"{message}\n")
    log_box.see(tk.END)


btn_frame = tk.Frame(root, bg="black")
btn_frame.pack(pady=15)

start_btn = tk.Button(btn_frame, text="Start Server",
                      command=core.start,
                      bg="#4FC3F7", width=15, height=2,
                      font=("Arial", 10, "bold"))
start_btn.grid(row=0, column=0, padx=10)

stop_btn = tk.Button(btn_frame, text="Stop Server",
                     bg="#E57373", width=15, height=2,
                     font=("Arial", 10, "bold"), state="disabled")
stop_btn.grid(row=0, column=1, padx=10)

draw_appliances()
root.mainloop()
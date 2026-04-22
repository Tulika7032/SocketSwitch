import ssl
import socket
import threading
import tkinter as tk

server_ip = "192.168.1.37"
server_port = 9999

context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile="ca.crt")
context.load_cert_chain(certfile="client.crt", keyfile="client.key")
context.check_hostname = False
context.verify_mode = ssl.CERT_REQUIRED

client_socket = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=server_ip)
client_socket.connect((server_ip, server_port))

print("[CLIENT CONNECTED]")

appliances = ["LIGHT", "AC", "FAN 1", "FAN 2", "GYSER", "HEATER"]
appliance_states = {a: False for a in appliances}

# ----------------MESSAGE HANDLER ---------------- #
def handle_status(data):
    log_box.insert(tk.END, f"{data}\n")
    for line in data.splitlines()[1:]:
        name, state = line.rsplit(" ", 1)
        appliance_states[name] = (state.upper() == "ON")

def handle_added(data):
    name = data.replace("ADDED", "").strip()
    if name not in appliances:
        appliances.append(name)
        appliance_states[name] = False
        draw_appliance_buttons()

def handle_removed(data):
    name = data.replace(" REMOVED", "").strip()
    if name in appliances:
        appliances.remove(name)
        appliance_states.pop(name, None)
        draw_appliance_buttons()

def handle_update(data):
    name, state = data.rsplit(" ", 1)
    if name not in appliances:
        appliances.append(name)
    appliance_states[name] = (state.upper() == "ON")
    draw_appliance_buttons()

def handle_default(data):
    log_box.insert(tk.END, f"{data}\n")

# Dispatcher
message_router = [
    ("[STATUS]", handle_status),
    ("ADDED", handle_added),
    ("REMOVED", handle_removed)
]

def receive_messages():
    while True:
        try:
            data = client_socket.recv(1024).decode()
            if not data:
                break
            handled = False

            # Route messages 
            for key, func in message_router:
                if key in data:
                    func(data)
                    handled = True
                    break

            # fallback for ON/OFF updates
            if not handled and " " in data:
                handle_update(data)
                handled = True

            if not handled:
                handle_default(data)

            log_box.see(tk.END)

        except Exception as e:
            log_box.insert(tk.END, f"[ERROR] {e}\n")
            break

threading.Thread(target=receive_messages, daemon=True).start()

def dark_input_dialog(title, prompt, is_password=False):
    dialog = tk.Toplevel(root)
    dialog.title(title)
    dialog.configure(bg="black")
    dialog.geometry("300x130")
    dialog.resizable(False, False)

    tk.Label(dialog, text=prompt, bg="black", fg="white", font=("Arial", 11)).pack(pady=10)
    entry_var = tk.StringVar()
    entry = tk.Entry(dialog, textvariable=entry_var,
                     show="*" if is_password else "",
                     font=("Arial", 11), bg="#333", fg="white")
    entry.pack(pady=5)
    entry.focus()

    def on_submit():
        dialog.user_input = entry_var.get()
        dialog.destroy()

    tk.Button(dialog, text="OK", command=on_submit,
              bg="#4FC3F7", font=("Arial", 10, "bold")).pack(pady=5)

    dialog.user_input = None
    dialog.grab_set()
    root.wait_window(dialog)
    return dialog.user_input

def send_cmd(cmd):
    try:
        client_socket.send(cmd.encode())
        log_box.insert(tk.END, f"> {cmd}\n")
    except:
        log_box.insert(tk.END, "[ERROR] Cannot send command\n")

def toggle_appliance(appliance):
    appliance_states[appliance] = not appliance_states[appliance]
    state = "ON" if appliance_states[appliance] else "OFF"
    send_cmd(f"{appliance.upper()} {state}")
    draw_appliance_buttons()

def draw_appliance_buttons():
    for widget in appliance_frame.winfo_children():
        widget.destroy()

    for i, appliance in enumerate(appliances):
        tk.Label(appliance_frame, text=appliance,
                 bg="black", fg="white", font=("Arial", 10))\
            .grid(row=i//2, column=(i % 2)*2, padx=10, pady=5, sticky="w")

        btn = tk.Canvas(appliance_frame, width=30, height=20,
                        bg="black", highlightthickness=0)

        color = "green" if appliance_states.get(appliance, False) else "red"
        btn.create_oval(2, 2, 18, 18, fill=color)
        btn.grid(row=i//2, column=(i % 2)*2 + 1, padx=5)

        btn.bind("<Button-1>", lambda e, a=appliance: toggle_appliance(a))

def on_add():
    val = dark_input_dialog("Add Appliance", "Appliance name:")
    if val:
        send_cmd(f"ADD {val.upper()}")

def on_remove():
    val = dark_input_dialog("Remove Appliance", "Appliance name:")
    if val:
        send_cmd(f"REMOVE {val.upper()}")

def on_timer():
    a = dark_input_dialog("Timer", "Appliance?")
    s = dark_input_dialog("Timer", "ON or OFF?")
    t = dark_input_dialog("Timer", "Seconds?")
    if a and s and t:
        send_cmd(f"TIMER {a.upper()} {s.upper()} {t}")

def on_schedule():
    a = dark_input_dialog("Schedule", "Appliance?")
    s = dark_input_dialog("Schedule", "ON or OFF?")
    t = dark_input_dialog("Schedule", "Time (HH:MM)?")
    if a and s and t:
        send_cmd(f"SCHEDULE {a.upper()} {s.upper()} {t}")

def on_status():
    send_cmd("STATUS")

root = tk.Tk()
root.title("Home Automation Switch")
root.configure(bg="black")
root.geometry("360x640")

title = tk.Label(root, text="Home Automation Switch",
                 font=("Arial", 14, "bold"), fg="white", bg="black")
title.pack(pady=(10, 5))

log_box = tk.Text(root, height=5, width=44,
                  bg="white", fg="black", font=("Arial", 10))
log_box.pack(pady=(5, 10))

appliance_frame = tk.Frame(root, bg="black")
appliance_frame.pack()

btn_frame = tk.Frame(root, bg="black")
btn_frame.pack(pady=15)

def styled_button(txt, cmd, color):
    return tk.Button(btn_frame, text=txt, bg=color, fg="black",
                     font=("Arial", 11, "bold"),
                     width=12, height=2, command=cmd)

styled_button("Set Timer", on_timer, "#4FC3F7").grid(row=0, column=0, padx=5, pady=5)
styled_button("ADD NEW", on_add, "#CE93D8").grid(row=0, column=1, padx=5, pady=5)
styled_button("Get Status", on_status, "#4FC3F7").grid(row=1, column=0, padx=5, pady=5)
styled_button("REMOVE", on_remove, "#80DEEA").grid(row=1, column=1, padx=5, pady=5)
styled_button("Schedule", on_schedule, "#4FC3F7").grid(row=2, column=0, padx=5, pady=5)
styled_button("Exit", root.quit, "#EF9A9A").grid(row=2, column=1, padx=5, pady=5)

draw_appliance_buttons()
root.mainloop()
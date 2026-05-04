import customtkinter as ctk
from tkinter import messagebox
import vgamepad as vg
import sys
import time

# Set Appearance and Theme
ctk.set_appearance_mode("Dark")  # Dark mode by default
ctk.set_default_color_theme("blue")  # Modern blue accent

class ControllerRow(ctk.CTkFrame):
    def __init__(self, master, index, remove_callback, controller_type="Xbox"):
        super().__init__(master, corner_radius=10)
        self.index = index
        self.remove_callback = remove_callback
        self.controller_type = controller_type
        self.gamepad = None
        self.is_connected = False

        self.pack(fill='x', padx=20, pady=10)

        # Left: Controller Info
        self.info_label = ctk.CTkLabel(self, text="", 
                                        font=("Segoe UI", 16, "bold"), width=200, anchor='w')
        self.info_label.pack(side='left', padx=20, pady=15)
        self.update_label(index)

        # Right: Buttons (Remove, Connect/Disconnect)
        self.btn_remove = ctk.CTkButton(self, text="Remove", width=80, height=32, 
                                        fg_color="#d32f2f", hover_color="#b71c1c",
                                        command=self.remove)
        self.btn_remove.pack(side='right', padx=(5, 20))

        self.btn_toggle = ctk.CTkButton(self, text="Connect", width=120, height=32, 
                                        fg_color="#1976D2", hover_color="#1565C0",
                                        command=self.toggle_connection)
        self.btn_toggle.pack(side='right', padx=5)

    def update_label(self, new_index):
        self.index = new_index
        display_name = "Xbox 360" if self.controller_type == "Xbox" else "PS4"
        self.info_label.configure(text=f"🎮 {display_name} ({self.index + 1})")

    def toggle_connection(self, force_state=None):
        """
        force_state: True to connect, False to disconnect, None to toggle
        """
        target_state = not self.is_connected if force_state is None else force_state
        
        if target_state == self.is_connected:
            return # Already in desired state

        if target_state: # Connecting
            try:
                if self.controller_type == "Xbox":
                    self.gamepad = vg.VX360Gamepad()
                else:
                    self.gamepad = vg.VDS4Gamepad()
                
                self.gamepad.left_joystick_float(0.0, 0.0)
                self.gamepad.right_joystick_float(0.0, 0.0)
                self.gamepad.update()
                time.sleep(0.05)
                
                self.gamepad.left_joystick_float(0.01, 0.01)
                self.gamepad.update()
                time.sleep(0.05)
                
                self.gamepad.reset()
                self.gamepad.left_joystick_float(0.0, 0.0)
                self.gamepad.right_joystick_float(0.0, 0.0)
                self.gamepad.update()
                
                self.is_connected = True
                self.btn_toggle.configure(text="Disconnect", fg_color="#388E3C", hover_color="#2E7D32")
                self.btn_remove.configure(state="disabled", fg_color="#555555")
                
                print(f"[INFO] {self.controller_type} Controller {self.index + 1} connected.")
                self.start_heartbeat()
            except Exception as e:
                if force_state is None: # Only show error if manual toggle
                    messagebox.showerror("Driver Error", f"Failed to connect controller: {e}")
                print(f"[ERROR] Driver Error: {e}")
        else: # Disconnecting
            self.is_connected = False
            if self.gamepad:
                self.gamepad.reset()
                self.gamepad.update()
                del self.gamepad
            self.gamepad = None
            self.btn_toggle.configure(text="Connect", fg_color="#1976D2", hover_color="#1565C0")
            self.btn_remove.configure(state="normal", fg_color="#d32f2f")
            print(f"[INFO] {self.controller_type} Controller {self.index + 1} disconnected.")

    def start_heartbeat(self):
        if self.is_connected and self.gamepad:
            try:
                self.gamepad.left_joystick_float(0.0, 0.0)
                self.gamepad.right_joystick_float(0.0, 0.0)
                self.gamepad.update()
                self.after(1000, self.start_heartbeat)
            except Exception as e:
                print(f"[ERROR] Heartbeat failed for {self.controller_type} Controller {self.index + 1}: {e}")

    def remove(self):
        if self.is_connected:
            return
        self.remove_callback(self)
        self.destroy()

class ControllerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Virtual Controller Manager")
        self.geometry("700x750")
        
        # Main Header
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill='x', pady=(20, 10))

        self.title_label = ctk.CTkLabel(self.header_frame, text="VIRTUAL CONTROLLER HUB", 
                                        font=("Segoe UI", 24, "bold"))
        self.title_label.pack()

        # Button Container for adding different types
        self.btn_container = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.btn_container.pack(pady=15)

        self.add_xbox_btn = ctk.CTkButton(self.btn_container, text="+ ADD XBOX 360", 
                                     font=("Segoe UI", 12, "bold"), height=40,
                                     fg_color="#1976D2", hover_color="#1565C0",
                                     command=lambda: self.add_controller("Xbox"))
        self.add_xbox_btn.pack(side='left', padx=10)

        self.add_ps4_btn = ctk.CTkButton(self.btn_container, text="+ ADD PS4", 
                                     font=("Segoe UI", 12, "bold"), height=40,
                                     fg_color="#455A64", hover_color="#37474F",
                                     command=lambda: self.add_controller("PS4"))
        self.add_ps4_btn.pack(side='left', padx=10)

        # Batch Actions Row (Centered container)
        self.batch_header = ctk.CTkFrame(self, fg_color="transparent", height=40)
        self.batch_header.pack(fill='x', padx=20, pady=(0, 5))
        
        # Center container for the buttons
        self.batch_btn_container = ctk.CTkFrame(self.batch_header, fg_color="transparent")
        self.batch_btn_container.pack(expand=True)

        # Define Colors for enabled/disabled states and hover effects (Dimmed Theme)
        self.colors = {
            "conn": {
                "on": {"base": "#1B5E20", "hover": "#2E7D32"},
                "off": {"base": "#0D2B10", "hover": "#0D2B10"}
            },
            "disc": {
                "on": {"base": "#A83E00", "hover": "#E65100"},
                "off": {"base": "#3D1600", "hover": "#3D1600"}
            },
            "rem": {
                "on": {"base": "#8B0000", "hover": "#B71C1C"},
                "off": {"base": "#300000", "hover": "#300000"}
            }
        }

        self.conn_all_btn = ctk.CTkButton(self.batch_btn_container, text="CONNECT ALL", 
                                          font=("Segoe UI", 11, "bold"), height=32, width=120,
                                          command=lambda: self.batch_action(True))
        self.conn_all_btn.pack(side='left', padx=5)

        self.disc_all_btn = ctk.CTkButton(self.batch_btn_container, text="DISCONNECT ALL", 
                                          font=("Segoe UI", 11, "bold"), height=32, width=120,
                                          command=lambda: self.batch_action(False))
        self.disc_all_btn.pack(side='left', padx=5)

        self.rm_all_btn = ctk.CTkButton(self.batch_btn_container, text="REMOVE ALL", 
                                          font=("Segoe UI", 11, "bold"), height=32, width=120,
                                          command=self.remove_all)
        self.rm_all_btn.pack(side='left', padx=5)

        # Scrollable area for controllers
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        self.controllers = []
        self.update_batch_visibility() # Initial state

    def update_batch_visibility(self):
        has_controllers = len(self.controllers) > 0
        state = "normal" if has_controllers else "disabled"
        mode = "on" if has_controllers else "off"
        
        # Update Connect All
        self.conn_all_btn.configure(
            state=state,
            fg_color=self.colors["conn"][mode]["base"],
            hover_color=self.colors["conn"][mode]["hover"]
        )
        
        # Update Disconnect All
        self.disc_all_btn.configure(
            state=state,
            fg_color=self.colors["disc"][mode]["base"],
            hover_color=self.colors["disc"][mode]["hover"]
        )
        
        # Update Remove All
        self.rm_all_btn.configure(
            state=state,
            fg_color=self.colors["rem"][mode]["base"],
            hover_color=self.colors["rem"][mode]["hover"]
        )

    def add_controller(self, controller_type):
        index = len(self.controllers)
        row = ControllerRow(self.scroll_frame, index, self.remove_row, controller_type)
        self.controllers.append(row)
        self.update_batch_visibility()

    def remove_row(self, row):
        if row in self.controllers:
            self.controllers.remove(row)
        # Re-index remaining controllers
        for i, controller in enumerate(self.controllers):
            controller.update_label(i)
        self.update_batch_visibility()

    def remove_all(self):
        # Disconnect all first
        self.batch_action(False)
        # Remove each row
        for controller in list(self.controllers):
            controller.destroy()
        self.controllers = []
        self.update_batch_visibility()

    def batch_action(self, connect):
        for controller in self.controllers:
            controller.toggle_connection(force_state=connect)

if __name__ == "__main__":
    try:
        import customtkinter
        import vgamepad
    except ImportError as e:
        print(f"[ERROR] Missing library: {e}")
        print("Please run: pip install customtkinter vgamepad")
        sys.exit(1)

    app = ControllerApp()
    app.mainloop()

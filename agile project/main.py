import customtkinter as ctk
from tkinter import messagebox
from DB import DBConnector
from components import SidebarButton
from views import BaseFrame, DashboardFrame

# --- CONFIGURATION ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Roadrev | Service Management System")
        self.geometry("1200x800")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Initialize Database
        self.db = DBConnector()
        if not self.db.conn:
            messagebox.showerror("Error", "Could not connect to database.")
            self.destroy()
            return

        self.setup_sidebar()
        self.setup_content_area()
        self.show_frame("Dashboard")

    def setup_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(8, weight=1)

        ctk.CTkLabel(self.sidebar, text="Roadrev", font=(
            "Montserrat", 24, "bold")).pack(pady=30, padx=20)

        buttons = [
            ("Dashboard", "logo.png"),
            ("Clients", "client.png"),
            ("Branches", "branch.png"),
            ("Garages", "garage.png"),
            ("Cars", "car.png"),
            ("Bookings", "booking.png"),
            ("Services", "service.png")
        ]

        self.nav_buttons = []
        for text, icon in buttons:
            btn = SidebarButton(self.sidebar, text=text, image_name=icon,
                                command=lambda t=text: self.show_frame(t))
            btn.pack(pady=5, padx=10, fill="x")
            self.nav_buttons.append(btn)

        ctk.CTkSwitch(self.sidebar, text="Dark Mode", command=self.toggle_theme).pack(
            side="bottom", pady=20, padx=20)

    def setup_content_area(self):
        self.content_area = ctk.CTkFrame(
            self, corner_radius=0, fg_color="transparent")
        self.content_area.grid(row=0, column=1, sticky="nsew")

    def toggle_theme(self):
        if ctk.get_appearance_mode() == "Dark":
            ctk.set_appearance_mode("Light")
        else:
            ctk.set_appearance_mode("Dark")

    def show_frame(self, name):
        # Clear current content
        for widget in self.content_area.winfo_children():
            widget.destroy()

        # Update Sidebar visual state
        for btn in self.nav_buttons:
            if btn.cget("text") == name:
                btn.configure(fg_color=("gray75", "gray25"))
            else:
                btn.configure(fg_color="transparent")

        # Route logic
        if name == "Dashboard":
            DashboardFrame(self.content_area, self.db).pack(
                fill="both", expand=True)
        else:
            self.load_crud_view(name)

    def load_crud_view(self, name):
        configs = {
            "Clients": ("Client", ["SSN", "Fname", "Middle", "Lname", "Address", "Phone_num"]),
            "Branches": ("Branch", ["Branchno", "Blocation", "License_no"]),
            "Garages": ("Garage", ["Garageno", "Capacity", "Glocation", "Branch_no"]),
            "Cars": ("Car", ["MotorID", "License_no", "Year_Model", "CName", "Shade_num", "Color_name", "Garage_no", "ClientID"]),
            "Bookings": ("Booking", ["BookingID", "Booking_Date", "Booking_time", "BranchID", "ClientID"]),
            "Services": ("Service", ["ServiceID", "SName", "Cost"])
        }

        if name in configs:
            entity, fields = configs[name]
            BaseFrame(self.content_area, self.db, name, entity,
                      fields).pack(fill="both", expand=True)


if __name__ == "__main__":
    app = App()
    app.mainloop()

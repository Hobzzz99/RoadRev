import customtkinter as ctk
from tkinter import messagebox
from components import ModernTreeview  # Import from components file
from datetime import datetime


class BaseFrame(ctk.CTkFrame):
    def __init__(self, master, db, title, entity_name, fields):
        super().__init__(master, fg_color="transparent")
        self.db = db
        self.entity_name = entity_name
        self.fields = fields

        self.create_header(title)
        self.create_content_area()
        self.load_data()

    def create_header(self, title):
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(self.header, text=f"{title} Management",
                     font=("Roboto", 24, "bold")).pack(side="left")

        # Search Bar
        self.search_var = ctk.StringVar()
        ctk.CTkEntry(self.header, textvariable=self.search_var,
                     placeholder_text="Search...", width=250).pack(side="right", padx=10)

        ctk.CTkButton(self.header, text="Search", width=80,
                      command=self.search_records).pack(side="right")

    def create_content_area(self):
        self.content = ctk.CTkFrame(self, fg_color=("gray90", "gray16"))
        self.content.pack(fill="both", expand=True, padx=20, pady=10)

        # 1. Form
        self.form_frame = ctk.CTkScrollableFrame(
            self.content, height=150, fg_color="transparent", orientation="horizontal")
        self.form_frame.pack(fill="x", padx=10, pady=10)

        self.entries = {}
        for field in self.fields:
            f_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
            f_frame.pack(side="left", padx=10)
            ctk.CTkLabel(f_frame, text=field.replace(
                "_", " ").title(), font=("Roboto", 12)).pack(anchor="w")

            entry = ctk.CTkEntry(f_frame, width=180)

            # --- START OF NEW CODE ---
            # If this is the Booking screen, disable Date and Time boxes
            if self.entity_name == "Booking" and field in ["Booking_Date", "Booking_time"]:
                entry.configure(placeholder_text="Auto-filled")
                entry.configure(state="disabled")  # User cannot type here
            # --- END OF NEW CODE ---

            entry.pack()
            self.entries[field] = entry

        # 2. Buttons
        self.create_buttons()

        # 3. Table
        self.table_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        self.table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree_view = ModernTreeview(self.table_frame, columns=self.fields)
        self.tree_view.pack(fill="both", expand=True)

        for col in self.fields:
            self.tree_view.heading(col, text=col.replace("_", " ").title())
            self.tree_view.column(col, width=120, anchor="center")

        self.tree_view.bind("<<TreeviewSelect>>", self.on_row_select)

    def create_buttons(self):
        btn_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=5)

        colors = {"Add": "#2CC985", "Update": "#FFA500",
                  "Delete": "#FF4747", "Clear": "gray"}

        actions = [
            ("Add Record", colors["Add"], self.add_record),
            ("Update Selected", colors["Update"], self.update_record),
            ("Delete Selected", colors["Delete"], self.delete_record),
            ("Clear Form", colors["Clear"], self.clear_form)
        ]

        for text, color, cmd in actions:
            ctk.CTkButton(btn_frame, text=text, fg_color=color, hover_color=color,
                          command=cmd).pack(side="left", padx=5)

    # --- Data Operations ---
    def load_data(self):
        self.tree_view.delete(*self.tree_view.get_children())
        records = self.db.execute_query(f"SELECT * FROM {self.entity_name}")
        if records:
            for record in records:
                self.tree_view.insert(
                    "", "end", values=[record[f] for f in self.fields])

    def on_row_select(self, _):
        selected = self.tree_view.focus()
        if selected:
            values = self.tree_view.item(selected, 'values')
            for field, value in zip(self.fields, values):
                self.entries[field].delete(0, 'end')
                self.entries[field].insert(0, str(value))

    def clear_form(self):
        for entry in self.entries.values():
            entry.delete(0, 'end')

    def add_record(self):
        # 1. Get values from the GUI
        values = [e.get() for e in self.entries.values()]

        # 2. AUTOMATIC DATE/TIME LOGIC
        if self.entity_name == "Booking":
            now = datetime.now()

            # Find the position of 'Booking_Date' and insert today's date
            if "Booking_Date" in self.fields:
                idx = self.fields.index("Booking_Date")
                values[idx] = now.strftime("%Y-%m-%d")  # Format: 2025-12-10

            # Find the position of 'Booking_time' and insert current time
            if "Booking_time" in self.fields:
                idx = self.fields.index("Booking_time")
                values[idx] = now.strftime("%H:%M")    # Format: 14:30

        # 3. Validation (Check if other fields are empty)
        # We filter out the auto-filled fields to check if the USER typed the rest
        user_inputs = [v for i, v in enumerate(values) if self.fields[i] not in [
            "Booking_Date", "Booking_time"]]
        if not any(user_inputs):
            return

        # 4. Save to Database (Existing code)
        placeholders = ", ".join(["%s"] * len(self.fields))
        cols = ", ".join(self.fields)
        query = f"INSERT INTO {self.entity_name} ({cols}) VALUES ({placeholders})"

        if self.db.execute_query(query, values):
            self.load_data()
            self.clear_form()
            self.show_toast("Record Added")

    def update_record(self):
        selected = self.tree_view.focus()
        if not selected:
            return

        values = [e.get() for e in self.entries.values()]
        set_clause = ", ".join([f"{f}=%s" for f in self.fields])
        # Using first field as PK for simplicity
        query = f"UPDATE {self.entity_name} SET {set_clause} WHERE {self.fields[0]}=%s"

        if self.db.execute_query(query, values + [values[0]]):
            self.load_data()
            self.show_toast("Record Updated")

    def delete_record(self):
        selected = self.tree_view.focus()
        if not selected:
            return

        val = self.tree_view.item(selected, 'values')[0]
        if messagebox.askyesno("Confirm", "Delete this record?"):
            query = f"DELETE FROM {self.entity_name} WHERE {self.fields[0]}=%s"
            if self.db.execute_query(query, (val,)):
                self.load_data()
                self.clear_form()
                self.show_toast("Record Deleted")

    def search_records(self):
        term = self.search_var.get()
        if not term:
            self.load_data()
            return

        self.tree_view.delete(*self.tree_view.get_children())
        conditions = " OR ".join([f"{f} LIKE %s" for f in self.fields])
        query = f"SELECT * FROM {self.entity_name} WHERE {conditions}"
        params = [f"%{term}%"] * len(self.fields)

        records = self.db.execute_query(query, params)
        if records:
            for record in records:
                self.tree_view.insert(
                    "", "end", values=[record[f] for f in self.fields])

    def show_toast(self, message):
        lbl = ctk.CTkLabel(self, text=message, fg_color="#2CC985",
                           text_color="white", corner_radius=5)
        lbl.place(relx=0.5, rely=0.9, anchor="center")
        self.after(2000, lbl.destroy)


class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, db):
        super().__init__(master, fg_color="transparent")
        self.db = db

        ctk.CTkLabel(self, text="Dashboard Overview", font=(
            "Roboto", 28, "bold")).pack(pady=20, anchor="w", padx=20)

        self.cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_frame.pack(fill="x", padx=20)
        self.cards_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        stats = [
            ("Total Clients", "SELECT COUNT(*) as c FROM Client", "#3B8ED0"),
            ("Total Branches", "SELECT COUNT(*) as c FROM Branch", "#E04F5F"),
            ("Active Bookings", "SELECT COUNT(*) as c FROM Booking", "#8257E5"),
            ("Available Cars", "SELECT COUNT(*) as c FROM Car", "#E89E23")
        ]

        for i, (title, query, color) in enumerate(stats):
            self.create_card(i, title, query, color)

    def create_card(self, col, title, query, color):
        card = ctk.CTkFrame(self.cards_frame, fg_color=color, corner_radius=10)
        card.grid(row=0, column=col, padx=10, sticky="ew")

        ctk.CTkLabel(card, text=title, font=("Roboto", 14),
                     text_color="white").pack(pady=(15, 0))

        res = self.db.execute_query(query)
        count = res[0]['c'] if res else 0

        ctk.CTkLabel(card, text=str(count), font=(
            "Roboto", 36, "bold"), text_color="white").pack(pady=(5, 15))

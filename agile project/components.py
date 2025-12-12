import customtkinter as ctk
from tkinter import ttk
from PIL import Image
import os


class ModernTreeview(ctk.CTkFrame):
    """Wraps ttk.Treeview to look modern in CustomTkinter"""

    def __init__(self, master, columns, **kwargs):
        super().__init__(master, **kwargs)

        # Style configuration for Dark Mode
        style = ttk.Style()
        style.theme_use("clam")

        # Configure colors to match CustomTkinter Dark Mode
        bg_color = "#2b2b2b"
        fg_color = "white"
        header_bg = "#1f6aa5"
        header_fg = "white"

        style.configure("Treeview",
                        background=bg_color,
                        foreground=fg_color,
                        fieldbackground=bg_color,
                        rowheight=35,
                        font=("Roboto", 11),
                        borderwidth=0)

        style.configure("Treeview.Heading",
                        background=header_bg,
                        foreground=header_fg,
                        font=("Roboto", 12, "bold"),
                        relief="flat")

        style.map("Treeview", background=[('selected', '#1f538d')])

        self.tree = ttk.Treeview(self, columns=columns, show="headings")

        # Scrollbars
        self.vsb = ctk.CTkScrollbar(
            self, orientation="vertical", command=self.tree.yview)
        self.hsb = ctk.CTkScrollbar(
            self, orientation="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.vsb.set,
                            xscrollcommand=self.hsb.set)

        # Grid Layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.vsb.grid(row=0, column=1, sticky="ns")
        self.hsb.grid(row=1, column=0, sticky="ew")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

    # Proxy methods to access the underlying treeview
    def insert(self, *args, **kwargs): return self.tree.insert(*args, **kwargs)
    def delete(self, *args): self.tree.delete(*args)
    def get_children(self): return self.tree.get_children()
    def heading(self, col, text): self.tree.heading(col, text=text)
    def column(self, col, **kwargs): self.tree.column(col, **kwargs)
    def focus(self): return self.tree.focus()
    def item(self, item, option=None): return self.tree.item(item, option)
    def bind(self, sequence, func): self.tree.bind(sequence, func)


class SidebarButton(ctk.CTkButton):
    def __init__(self, master, text, image_name=None, command=None):
        icon = None
        if image_name:
            try:
                img_path = os.path.join("icons", image_name)
                if os.path.exists(img_path):
                    icon = ctk.CTkImage(light_image=Image.open(img_path),
                                        dark_image=Image.open(img_path),
                                        size=(20, 20))
            except Exception:
                pass

        super().__init__(master,
                         text=text,
                         image=icon,
                         command=command,
                         height=40,
                         corner_radius=6,
                         fg_color="transparent",
                         text_color=("gray10", "gray90"),
                         hover_color=("gray70", "gray30"),
                         anchor="w",
                         font=("Roboto Medium", 14))

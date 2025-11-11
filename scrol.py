import tkinter as tk
from tkinter import ttk
import sys

class ScrollableFrame(ttk.Frame):
    """A scrollable frame that allows adding child widgets to `self.inner`."""
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)

        # 1) Create canvas + vertical scrollbar
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        self.vscroll = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vscroll.set)

        # 2) Place them
        self.vscroll.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # 3) Create an interior frame to hold widgets
        self.inner = ttk.Frame(self.canvas)
        self.inner_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")

        # 4) Sync canvas scrollregion when inner frame changes size
        def _on_frame_config(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.inner.bind("<Configure>", _on_frame_config)

        # 5) Make inner frame width follow canvas width
        def _on_canvas_config(event):
            # update the inner frame's width to fill the canvas
            canvas_width = event.width
            self.canvas.itemconfigure(self.inner_id, width=canvas_width)
        self.canvas.bind("<Configure>", _on_canvas_config)

        # 6) Mousewheel support (cross-platform)
        self._bind_mousewheel_events()

    def _on_mousewheel_windows(self, event):
        # event.delta is multiple of 120 on Windows
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_mousewheel_macos(self, event):
        # On macOS event.delta is small (often 1 or -1); use it directly
        self.canvas.yview_scroll(int(-1 * event.delta), "units")

    def _on_mousewheel_linux_up(self, event):
        self.canvas.yview_scroll(-1, "units")

    def _on_mousewheel_linux_down(self, event):
        self.canvas.yview_scroll(1, "units")

    def _bind_mousewheel_events(self):
        platform = sys.platform
        if platform == "darwin":
            # macOS
            self.canvas.bind_all("<MouseWheel>", self._on_mousewheel_macos)
        elif platform.startswith("linux"):
            # Linux (X11) using Button-4 and Button-5
            self.canvas.bind_all("<Button-4>", self._on_mousewheel_linux_up)
            self.canvas.bind_all("<Button-5>", self._on_mousewheel_linux_down)
        else:
            # Windows
            self.canvas.bind_all("<MouseWheel>", self._on_mousewheel_windows)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Scrollable Frame Demo")
    root.geometry("400x300")

    # Put the scrollable frame in the window
    sf = ScrollableFrame(root)
    sf.pack(fill="both", expand=True)

    # Add many widgets to demonstrate scrolling
    for i in range(40):
        row = ttk.Frame(sf.inner, padding=4)
        row.grid(row=i, column=0, sticky="ew", padx=4, pady=2)
        row.columnconfigure(1, weight=1)
        ttk.Label(row, text=f"Label {i}").grid(row=0, column=0, sticky="w")
        ttk.Entry(row).grid(row=0, column=1, sticky="ew")

    # Add a bottom button outside the scrollable area to show layout
    ttk.Button(root, text="Bottom button (not scrolled)").pack(pady=6)

    root.mainloop()
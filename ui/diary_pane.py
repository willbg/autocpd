"""Centre pane – CPD diary data-table with row selection and checkboxes."""

from __future__ import annotations

from tkinter import ttk, StringVar
import customtkinter as ctk

from models import Activity
import storage


class DiaryPane(ctk.CTkFrame):
    """Scrollable data-table that lists all CPD diary entries.

    Features
    --------
    * Row selection → fires *on_select_callback* so the entry pane can populate.
    * Checkbox column → marks records for bulk upload.
    * Delete button removes the currently selected record.
    """

    def __init__(self, master, on_select_callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self._on_select = on_select_callback
        self._activities: list[Activity] = []

        self._build_widgets()
        self.refresh()

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build_widgets(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # -- Header -------------------------------------------------------
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        header_frame.columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header_frame,
            text="CPD Diary",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, sticky="w")

        # Toolbar: select-all & delete
        tb = ctk.CTkFrame(header_frame, fg_color="transparent")
        tb.grid(row=0, column=1, sticky="e")

        self._select_all_var = StringVar(value="off")
        self._select_all_cb = ctk.CTkCheckBox(
            tb, text="Select all", variable=self._select_all_var,
            onvalue="on", offvalue="off",
            command=self._toggle_select_all,
            checkbox_width=18, checkbox_height=18,
        )
        self._select_all_cb.grid(row=0, column=0, padx=(0, 8))

        self._delete_btn = ctk.CTkButton(
            tb, text="Delete", width=70,
            fg_color="#c0392b", hover_color="#96281b",
            command=self._delete_selected,
        )
        self._delete_btn.grid(row=0, column=1)

        # -- Treeview (styled) --------------------------------------------
        style = ttk.Style()
        style.theme_use("default")

        bg = "#2b2b2b"
        fg = "#dcdcdc"
        sel_bg = "#1f6fa5"

        style.configure(
            "Diary.Treeview",
            background=bg,
            foreground=fg,
            fieldbackground=bg,
            borderwidth=0,
            rowheight=28,
            font=("Helvetica", 12),
        )
        style.configure(
            "Diary.Treeview.Heading",
            background="#3a3a3a",
            foreground=fg,
            relief="flat",
            font=("Helvetica", 12, "bold"),
        )
        style.map(
            "Diary.Treeview",
            background=[("selected", sel_bg)],
            foreground=[("selected", "#ffffff")],
        )

        columns = ("sel", "status", "title", "date", "hours", "category")
        self._tree = ttk.Treeview(
            self,
            columns=columns,
            show="headings",
            selectmode="browse",
            style="Diary.Treeview",
        )

        self._tree.heading("sel",      text="☐")
        self._tree.heading("status",   text="Status")
        self._tree.heading("title",    text="Title")
        self._tree.heading("date",     text="Date")
        self._tree.heading("hours",    text="Hours")
        self._tree.heading("category", text="Category")

        self._tree.column("sel",      width=36,  minwidth=36,  stretch=False, anchor="center")
        self._tree.column("status",   width=72,  minwidth=60,  stretch=False, anchor="center")
        self._tree.column("title",    width=200, minwidth=120, stretch=True)
        self._tree.column("date",     width=100, minwidth=90,  stretch=False, anchor="center")
        self._tree.column("hours",    width=60,  minwidth=50,  stretch=False, anchor="center")
        self._tree.column("category", width=180, minwidth=100, stretch=True)

        # Scrollbar
        scrollbar = ctk.CTkScrollbar(self, command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)

        self._tree.grid(row=1, column=0, sticky="nsew", padx=(8, 0), pady=(0, 8))
        scrollbar.grid(row=1, column=1, sticky="ns", pady=(0, 8), padx=(0, 8))

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)

        # Bindings
        self._tree.bind("<<TreeviewSelect>>", self._on_row_select)
        self._tree.bind("<Button-1>", self._on_click)

    # ------------------------------------------------------------------
    # Data
    # ------------------------------------------------------------------

    def refresh(self):
        """Reload activities from disk and repopulate the table."""
        self._activities = storage.load_activities()
        self._tree.delete(*self._tree.get_children())
        for act in self._activities:
            sel_mark = "☑" if act.selected else "☐"
            status_mark = "✓ Uploaded" if act.status == "Uploaded" else "● Pending"
            self._tree.insert(
                "", "end",
                iid=act.id,
                values=(sel_mark, status_mark, act.title, act.date, act.hours, act.category),
            )

    def get_selected_activities(self) -> list[Activity]:
        """Return activities whose checkbox is ticked."""
        return [a for a in self._activities if a.selected]

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------

    def _on_row_select(self, _event):
        sel = self._tree.selection()
        if not sel:
            return
        act_id = sel[0]
        act = next((a for a in self._activities if a.id == act_id), None)
        if act and self._on_select:
            self._on_select(act)

    def _on_click(self, event):
        """Toggle the checkbox when the user clicks the 'sel' column."""
        region = self._tree.identify_region(event.x, event.y)
        if region != "cell":
            return
        col = self._tree.identify_column(event.x)
        if col != "#1":  # first column = sel
            return
        row_id = self._tree.identify_row(event.y)
        if not row_id:
            return
        act = next((a for a in self._activities if a.id == row_id), None)
        if act:
            act.selected = not act.selected
            storage.update_activity(act.id, selected=act.selected)
            # Update the display
            sel_mark = "☑" if act.selected else "☐"
            vals = list(self._tree.item(row_id, "values"))
            vals[0] = sel_mark
            self._tree.item(row_id, values=vals)

    def _toggle_select_all(self):
        """Select or deselect all records for upload."""
        state = self._select_all_var.get() == "on"
        for act in self._activities:
            act.selected = state
            storage.update_activity(act.id, selected=state)
        self.refresh()

    def _delete_selected(self):
        """Delete the currently highlighted (selected) row."""
        sel = self._tree.selection()
        if not sel:
            return
        act_id = sel[0]
        storage.delete_activity(act_id)
        self.refresh()

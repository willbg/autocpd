"""Left pane – CPD activity entry / edit form."""

from __future__ import annotations

import os
from datetime import date
from tkinter import filedialog, StringVar

import customtkinter as ctk

from models import Activity, EA_CATEGORIES, PA_CATEGORIES


class EntryPane(ctk.CTkFrame):
    """Input form for creating and editing CPD diary entries.

    Each entry maps to **both** EA and PA portals, so the form shows two
    category dropdowns side-by-side.

    When a row is selected in the diary table the form is populated with that
    record's data, the header shows "Editing: <title>", and the primary
    button switches to **Update**.  A **Delete** button also appears.
    Clicking *Clear* resets back to *Add* mode.
    """

    def __init__(self, master, on_save_callback=None, on_delete_callback=None,
                 log_callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self._on_save = on_save_callback      # called after add / update
        self._on_delete = on_delete_callback  # called after delete
        self._log = log_callback              # write to the activity log
        self._editing_id: str | None = None   # set when editing an existing record

        self._build_widgets()

    # ------------------------------------------------------------------
    # Widget construction
    # ------------------------------------------------------------------

    def _build_widgets(self):
        self.columnconfigure(0, weight=1)

        pad = {"padx": 12, "pady": (4, 0), "sticky": "w"}
        entry_pad = {"padx": 12, "pady": (0, 6), "sticky": "ew"}

        row = 0

        # -- Header -------------------------------------------------------
        self._header_label = ctk.CTkLabel(
            self, text="CPD Entry", font=ctk.CTkFont(size=18, weight="bold"),
        )
        self._header_label.grid(row=row, column=0, padx=12, pady=(12, 2), sticky="w")
        row += 1

        # -- Editing indicator (hidden by default) -------------------------
        self._editing_label = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=12, slant="italic"),
            text_color="#5dade2",
        )
        self._editing_label.grid(row=row, column=0, padx=12, pady=(0, 6), sticky="w")
        row += 1

        # -- Title ---------------------------------------------------------
        ctk.CTkLabel(self, text="Title *").grid(row=row, column=0, **pad)
        row += 1
        self._title_entry = ctk.CTkEntry(self, placeholder_text="e.g. Bridge Design Seminar")
        self._title_entry.grid(row=row, column=0, **entry_pad)
        row += 1

        # -- Date & Hours (combining to one row to save space) --------------
        dt_hr_frame = ctk.CTkFrame(self, fg_color="transparent")
        dt_hr_frame.grid(row=row, column=0, padx=12, pady=(4, 6), sticky="ew")
        dt_hr_frame.columnconfigure((0, 1), weight=1)

        # Date column (0)
        ctk.CTkLabel(dt_hr_frame, text="Date (YYYY-MM-DD) *").grid(row=0, column=0, sticky="w")
        self._date_entry = ctk.CTkEntry(dt_hr_frame)
        self._date_entry.insert(0, date.today().isoformat())
        self._date_entry.grid(row=1, column=0, sticky="ew", padx=(0, 6), pady=(2, 0))

        # Hours column (1)
        ctk.CTkLabel(dt_hr_frame, text="Hours *").grid(row=0, column=1, sticky="w")
        self._hours_entry = ctk.CTkEntry(dt_hr_frame, placeholder_text="e.g. 1.5")
        self._hours_entry.grid(row=1, column=1, sticky="ew", pady=(2, 0))
        row += 1

        # -- EA Category ---------------------------------------------------
        ctk.CTkLabel(self, text="EA Category *").grid(row=row, column=0, **pad)
        row += 1
        self._ea_category_var = StringVar(value=EA_CATEGORIES[0])
        self._ea_category_menu = ctk.CTkOptionMenu(
            self,
            variable=self._ea_category_var,
            values=EA_CATEGORIES,
        )
        self._ea_category_menu.grid(row=row, column=0, **entry_pad)
        row += 1

        # -- PA Category ---------------------------------------------------
        ctk.CTkLabel(self, text="PA Category *").grid(row=row, column=0, **pad)
        row += 1
        self._pa_category_var = StringVar(value=PA_CATEGORIES[0])
        self._pa_category_menu = ctk.CTkOptionMenu(
            self,
            variable=self._pa_category_var,
            values=PA_CATEGORIES,
        )
        self._pa_category_menu.grid(row=row, column=0, **entry_pad)
        row += 1

        # -- Notes ---------------------------------------------------------
        ctk.CTkLabel(self, text="Notes *").grid(row=row, column=0, **pad)
        row += 1
        self._notes_entry = ctk.CTkTextbox(
            self, height=150,
            font=ctk.CTkFont(size=12),
            wrap="word",
        )
        self._notes_entry.grid(row=row, column=0, **entry_pad)
        row += 1

        # -- Evidence file path --------------------------------------------
        ctk.CTkLabel(self, text="Evidence File *").grid(row=row, column=0, **pad)
        row += 1

        evidence_frame = ctk.CTkFrame(self, fg_color="transparent")
        evidence_frame.grid(row=row, column=0, **entry_pad)
        evidence_frame.columnconfigure(0, weight=1)

        self._evidence_entry = ctk.CTkEntry(
            evidence_frame,
            placeholder_text="Drag & drop or browse…",
        )
        self._evidence_entry.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        browse_btn = ctk.CTkButton(
            evidence_frame, text="Browse", width=70,
            command=self._browse_evidence,
        )
        browse_btn.grid(row=0, column=1)
        row += 1

        # -- Drop target overlay (visual cue) -----------------------------
        self._drop_label = ctk.CTkLabel(
            self,
            text="↓  Drop evidence file here  ↓",
            font=ctk.CTkFont(size=11),
            text_color="gray60",
        )
        self._drop_label.grid(row=row, column=0, padx=12, pady=(0, 4))
        row += 1

        # -- Action buttons ------------------------------------------------
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=row, column=0, padx=12, pady=(8, 4), sticky="ew")
        btn_frame.columnconfigure((0, 1), weight=1)

        self._action_btn = ctk.CTkButton(
            btn_frame,
            text="Add Entry",
            command=self._on_action,
            fg_color="#2fa572",
            hover_color="#26855c",
        )
        self._action_btn.grid(row=0, column=0, padx=(0, 4), sticky="ew")

        self._clear_btn = ctk.CTkButton(
            btn_frame,
            text="Clear",
            command=self.clear_form,
            fg_color="gray40",
            hover_color="gray30",
        )
        self._clear_btn.grid(row=0, column=1, padx=(4, 0), sticky="ew")
        row += 1

        # -- Delete button (only visible when editing) ---------------------
        self._delete_btn = ctk.CTkButton(
            self,
            text="🗑  Delete Entry",
            command=self._on_delete_clicked,
            fg_color="#c0392b",
            hover_color="#96281b",
        )
        # Hidden initially — shown via populate(), hidden via clear_form()
        row += 1

        # -- Validation feedback -------------------------------------------
        self._error_label = ctk.CTkLabel(
            self, text="", text_color="#e05050", font=ctk.CTkFont(size=11),
        )
        self._error_label.grid(row=row, column=0, padx=12, sticky="w")
        self._delete_row = row - 1  # remember which row the delete btn goes in

        # -- Enable drag-and-drop if tkdnd is available --------------------
        self._setup_dnd()

        # -- Spacer to push controls to the bottom -------------------------
        spacer = ctk.CTkFrame(self, fg_color="transparent", height=0)
        spacer.grid(row=row, column=0, sticky="nsew")
        self.rowconfigure(row, weight=1)
        row += 1

        # -- Control buttons (portal sync) ---------------------------------
        ctrl_sep = ctk.CTkLabel(
            self, text="Controls",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        ctrl_sep.grid(row=row, column=0, padx=12, pady=(8, 4), sticky="w")
        row += 1

        ctrl_pad = {"padx": 12, "sticky": "ew"}

        self._sync_pa_btn = ctk.CTkButton(
            self, text="⬆  Sync to PA",
            command=lambda: self._emit_log("Sync to PA clicked (Selenium not yet wired)."),
            fg_color="#8e44ad", hover_color="#6c3483",
        )
        self._sync_pa_btn.grid(row=row, column=0, pady=4, **ctrl_pad)
        row += 1

        self._sync_ea_btn = ctk.CTkButton(
            self, text="⬆  Sync to EA",
            command=lambda: self._emit_log("Sync to EA clicked (Selenium not yet wired)."),
            fg_color="#d35400", hover_color="#a04000",
        )
        self._sync_ea_btn.grid(row=row, column=0, pady=(4, 12), **ctrl_pad)

    # ------------------------------------------------------------------
    # Drag-and-drop support
    # ------------------------------------------------------------------

    def _setup_dnd(self):
        """Register the evidence entry as a file drop target using tkdnd."""
        try:
            self._evidence_entry.drop_target_register("DND_Files")  # type: ignore[attr-defined]
            self._evidence_entry.dnd_bind("<<Drop>>", self._on_drop)  # type: ignore[attr-defined]
        except (AttributeError, Exception):
            # tkdnd / tkinterdnd2 not available — silently fall back to browse-only
            pass

    def _on_drop(self, event):
        """Handle a file drop onto the evidence entry."""
        path = event.data.strip().strip("{}")  # tkdnd wraps paths in braces on some platforms
        self._evidence_entry.delete(0, "end")
        self._evidence_entry.insert(0, path)

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------

    def _emit_log(self, message: str):
        """Forward a message to the activity log (if callback is set)."""
        if self._log:
            self._log(message)

    def _browse_evidence(self):
        path = filedialog.askopenfilename(
            title="Select evidence file",
            filetypes=[("All files", "*.*"), ("PDF", "*.pdf"), ("Images", "*.png *.jpg *.jpeg")],
        )
        if path:
            self._evidence_entry.delete(0, "end")
            self._evidence_entry.insert(0, path)

    def _on_action(self):
        """Validate and either add a new entry or update the selected one."""
        title = self._title_entry.get().strip()
        date_str = self._date_entry.get().strip()
        hours_str = self._hours_entry.get().strip()
        ea_cat = self._ea_category_var.get()
        pa_cat = self._pa_category_var.get()
        notes = self._notes_entry.get("1.0", "end-1c").strip()
        evidence = self._evidence_entry.get().strip()

        # --- validation ---------------------------------------------------
        errors: list[str] = []
        if not title:
            errors.append("Title is required.")
        if not Activity.validate_date(date_str):
            errors.append("Date must be YYYY-MM-DD.")
        if not Activity.validate_hours(hours_str):
            errors.append("Hours must be a positive number.")
        if not ea_cat:
            errors.append("Select an EA category.")
        if not pa_cat:
            errors.append("Select a PA category.")
        if not notes:
            errors.append("Notes are required.")
        if not evidence:
            errors.append("Evidence file is required.")
        if errors:
            self._error_label.configure(text="  •  ".join(errors))
            return
        self._error_label.configure(text="")

        hours = float(hours_str)

        if self._editing_id:
            # Update existing record
            from storage import update_activity
            update_activity(
                self._editing_id,
                title=title,
                date=date_str,
                hours=hours,
                ea_category=ea_cat,
                pa_category=pa_cat,
                notes=notes,
                evidence_path=evidence,
            )
        else:
            # Add new record
            from storage import add_activity
            activity = Activity(
                title=title,
                date=date_str,
                hours=hours,
                ea_category=ea_cat,
                pa_category=pa_cat,
                notes=notes,
                evidence_path=evidence,
            )
            add_activity(activity)

        self.clear_form()
        if self._on_save:
            self._on_save()

    def _on_delete_clicked(self):
        """Delete the currently-loaded record."""
        if not self._editing_id:
            return
        from storage import delete_activity
        delete_activity(self._editing_id)
        self.clear_form()
        if self._on_delete:
            self._on_delete()

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def populate(self, activity: Activity):
        """Fill the form with an existing activity for editing."""
        self._editing_id = activity.id
        self._header_label.configure(text="Edit Entry")
        self._editing_label.configure(text=f"Editing: {activity.title}")
        self._action_btn.configure(
            text="Update Entry", fg_color="#2980b9", hover_color="#1f6fa5",
        )

        # Show delete button
        self._delete_btn.grid(
            row=self._delete_row, column=0, padx=12, pady=(0, 4), sticky="ew",
        )

        self._title_entry.delete(0, "end")
        self._title_entry.insert(0, activity.title)

        self._date_entry.delete(0, "end")
        self._date_entry.insert(0, activity.date)

        self._hours_entry.delete(0, "end")
        self._hours_entry.insert(0, str(activity.hours))

        self._evidence_entry.delete(0, "end")
        self._evidence_entry.insert(0, activity.evidence_path)

        self._notes_entry.delete("1.0", "end")
        self._notes_entry.insert("1.0", activity.notes)

        self._ea_category_var.set(activity.ea_category)
        self._pa_category_var.set(activity.pa_category)

    def clear_form(self):
        """Reset all fields and return to Add mode."""
        self._editing_id = None
        self._header_label.configure(text="CPD Entry")
        self._editing_label.configure(text="")
        self._action_btn.configure(
            text="Add Entry", fg_color="#2fa572", hover_color="#26855c",
        )
        self._error_label.configure(text="")

        # Hide delete button
        self._delete_btn.grid_forget()

        self._title_entry.delete(0, "end")
        self._date_entry.delete(0, "end")
        self._date_entry.insert(0, date.today().isoformat())
        self._hours_entry.delete(0, "end")
        self._notes_entry.delete("1.0", "end")
        self._evidence_entry.delete(0, "end")
        self._ea_category_var.set(EA_CATEGORIES[0])
        self._pa_category_var.set(PA_CATEGORIES[0])

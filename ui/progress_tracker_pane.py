"""Progress Tracker showing CPD accumulation statistics via Matplotlib."""

from __future__ import annotations

from datetime import datetime, date
from collections import defaultdict

import customtkinter as ctk
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np

import storage
from models import UNIFIED_CATEGORIES

# Ensure TkAgg is used for matplotlib
matplotlib.use('TkAgg')


class ProgressTrackerPane(ctk.CTkFrame):
    """Pane rendering matplotlib charts for tracking progress."""

    def __init__(self, master, target_hours: float = 150.0, **kwargs):
        super().__init__(master, **kwargs)
        self.target_hours = target_hours
        
        # Build the matplotlib figure architecture
        self._build_charts()
        
        # Load data and render initially
        self.refresh()
        
        # Bind resize event for responsive scaling
        self.bind("<Configure>", self._on_resize)

    def _on_resize(self, event):
        """Redraw when the widget is resized."""
        # Check if the figure still exists to avoid errors on shutdown
        if hasattr(self, 'fig') and plt.fignum_exists(self.fig.number):
            self.fig.tight_layout()
            self.canvas.draw()

    def shutdown(self):
        """Explicitly close the matplotlib figure to prevent residue errors."""
        if hasattr(self, 'fig'):
            plt.close(self.fig)

    def _build_charts(self):
        # Configure layout for a dark-themed integrated look
        plt.style.use('dark_background')
        
        # Get frame background color safely (often a tuple of 2 for light/dark mode)
        frame_bg = self.cget("fg_color")
        if isinstance(frame_bg, tuple):
            frame_bg = frame_bg[1] # Dark mode color
        
        # Override to match customtkinter dark grey if it failed
        bg_color = frame_bg if frame_bg and isinstance(frame_bg, str) else '#242424'
        
        # Use a smaller initial figsize and set the facecolor explicitly here
        self.fig, (self.ax_pie, self.ax_bar) = plt.subplots(
            1, 2, figsize=(6, 2.5), facecolor=bg_color
        )
        self.fig.patch.set_facecolor(bg_color)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        
        # CRITICAL: Set the underlying Tkinter widget background to match
        self.canvas_widget.configure(bg=bg_color, highlightthickness=0)
        
        # Ensure the canvas doesn't force a minimum size on the parent
        self.canvas_widget.configure(width=1, height=1)
        self.canvas_widget.pack(fill="both", expand=True, padx=4, pady=4)
        
    def refresh(self):
        """Re-read activities from storage and update the charts."""
        activities = storage.load_activities()
        
        # Clear existing plots and set background
        self.ax_pie.clear()
        self.ax_bar.clear()
        
        # Pull background color from the figure
        bg_color = self.fig.get_facecolor()
        self.ax_pie.set_facecolor(bg_color)
        self.ax_bar.set_facecolor(bg_color)
        
        # --- Data Filtering (Rolling 3 Years) ---
        today = date.today()
        three_years_ago = today.replace(year=today.year - 3)
        
        recent_activities = []
        yearly_totals = defaultdict(float)
        category_totals = defaultdict(float)
        
        total_recent_hours = 0.0
        
        for act in activities:
            try:
                act_date = datetime.strptime(act.date, "%Y-%m-%d").date()
            except ValueError:
                continue # Skip invalid dates
            
            # Check if within rolling 3-year window
            if three_years_ago <= act_date <= today:
                recent_activities.append(act)
                total_recent_hours += act.hours
                yearly_totals[act_date.year] += act.hours
                category_totals[act.category] += act.hours
                
        # --- 1. Category Pie Chart ---
        if category_totals:
            labels = list(category_totals.keys())
            sizes = list(category_totals.values())
            
            # Dynamic colors based on number of categories
            cmap = plt.get_cmap("tab10")
            colors = [cmap(i % 10) for i in range(len(labels))]
            
            self.ax_pie.pie(
                sizes, labels=labels, autopct='%1.1f%%',
                startangle=90, colors=colors, textprops={'color': "w", 'fontsize': 9}
            )
        else:
            # Empty state
            self.ax_pie.text(0.5, 0.5, 'No Recent Data', ha='center', va='center', color='gray')
            self.ax_pie.axis('off')
            
        self.ax_pie.set_title('CPD by Category (3 Years)', color='white')
        
        # --- 2. Completion Bar Chart ---
        if yearly_totals:
            years = sorted(yearly_totals.keys())
            hours_data = [yearly_totals[y] for y in years]
            labels_bar = [f"{y}\n({h:g}h)" for y, h in zip(years, hours_data)]
            
            y_pos = np.arange(1)
            left = 0
            cmap_bar = plt.get_cmap("Set2")
            colors_bar = [cmap_bar(i % 8) for i in range(len(years))]
            
            for i, h in enumerate(hours_data):
                self.ax_bar.barh(y_pos, h, left=left, color=colors_bar[i], label=labels_bar[i], height=0.4)
                # Text inside bar
                self.ax_bar.text(left + h/2, 0, f'{h:g}h', ha='center', va='center', color='white', fontweight='bold', fontsize=9)
                left += h
        else:
            left = 0
            
        # Remainder bar
        remainder = max(0, self.target_hours - total_recent_hours)
        if remainder > 0:
            self.ax_bar.barh(y_pos if yearly_totals else 0, remainder, left=left, color='#444444', height=0.4)
            self.ax_bar.text(left + remainder/2, 0, f'{remainder:g}h left', ha='center', va='center', color='lightgray', fontsize=9)
            
        self.ax_bar.set_xlim(0, max(self.target_hours, total_recent_hours + 10))
        self.ax_bar.set_yticks([])
        
        title_color = '#2ecc71' if total_recent_hours >= self.target_hours else 'white'
        self.ax_bar.set_title(f'Rolling 3-Year Target: {total_recent_hours:g}/{self.target_hours:g} hrs', color=title_color)
        
        self.fig.tight_layout()
        self.canvas.draw()

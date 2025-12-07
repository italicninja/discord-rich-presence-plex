"""
GUI Configuration Window for Discord Rich Presence for Plex
Provides a user-friendly interface for editing common configuration options
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Callable, Optional
import sys

class ConfigWindow:
	"""Tkinter-based configuration window"""

	def __init__(self, config: dict, on_save: Callable[[dict], None]):
		"""
		Initialize the configuration window

		Args:
			config: Current configuration dictionary
			on_save: Callback function called when user saves changes
		"""
		self.config = config.copy()  # Work with a copy
		self.on_save = on_save
		self.window: Optional[tk.Tk] = None

	def show(self):
		"""Display the configuration window"""
		if self.window is not None:
			# Window already exists, just bring it to front
			self.window.lift()
			self.window.focus_force()
			return

		self.window = tk.Tk()
		self.window.title("Discord Rich Presence for Plex - Settings")
		self.window.geometry("600x700")
		self.window.resizable(True, True)

		# Make window modal-ish (stays on top)
		self.window.attributes('-topmost', True)
		self.window.after(100, lambda: self.window.attributes('-topmost', False))

		# Create notebook (tabbed interface)
		notebook = ttk.Notebook(self.window)
		notebook.pack(fill='both', expand=True, padx=10, pady=10)

		# Create tabs
		display_tab = ttk.Frame(notebook)
		posters_tab = ttk.Frame(notebook)
		logging_tab = ttk.Frame(notebook)

		notebook.add(display_tab, text='Display Settings')
		notebook.add(posters_tab, text='Posters & Images')
		notebook.add(logging_tab, text='Logging')

		# Build each tab
		self._build_display_tab(display_tab)
		self._build_posters_tab(posters_tab)
		self._build_logging_tab(logging_tab)

		# Bottom buttons
		button_frame = ttk.Frame(self.window)
		button_frame.pack(fill='x', padx=10, pady=(0, 10))

		ttk.Button(button_frame, text="Save & Restart Required", command=self._save_config).pack(side='right', padx=5)
		ttk.Button(button_frame, text="Cancel", command=self._cancel).pack(side='right')

		# Handle window close
		self.window.protocol("WM_DELETE_WINDOW", self._cancel)

		# Center window on screen
		self.window.update_idletasks()
		width = self.window.winfo_width()
		height = self.window.winfo_height()
		x = (self.window.winfo_screenwidth() // 2) - (width // 2)
		y = (self.window.winfo_screenheight() // 2) - (height // 2)
		self.window.geometry(f'{width}x{height}+{x}+{y}')

		self.window.mainloop()

	def _build_display_tab(self, parent):
		"""Build the Display Settings tab"""
		# Create scrollable frame
		canvas = tk.Canvas(parent)
		scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
		scrollable_frame = ttk.Frame(canvas)

		scrollable_frame.bind(
			"<Configure>",
			lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
		)

		canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
		canvas.configure(yscrollcommand=scrollbar.set)

		canvas.pack(side="left", fill="both", expand=True)
		scrollbar.pack(side="right", fill="y")

		display = self.config.get('display', {})

		# Metadata Display Section
		section = ttk.LabelFrame(scrollable_frame, text="Metadata Display", padding=10)
		section.pack(fill='x', padx=10, pady=5)

		self.duration_var = tk.BooleanVar(value=display.get('duration', True))
		ttk.Checkbutton(section, text="Show duration (movies & TV shows)", variable=self.duration_var).pack(anchor='w', pady=2)

		self.year_var = tk.BooleanVar(value=display.get('year', True))
		ttk.Checkbutton(section, text="Show release year", variable=self.year_var).pack(anchor='w', pady=2)

		self.genres_var = tk.BooleanVar(value=display.get('genres', True))
		ttk.Checkbutton(section, text="Show genres (movies only)", variable=self.genres_var).pack(anchor='w', pady=2)

		# Music Display Section
		section = ttk.LabelFrame(scrollable_frame, text="Music Display", padding=10)
		section.pack(fill='x', padx=10, pady=5)

		self.album_var = tk.BooleanVar(value=display.get('album', True))
		ttk.Checkbutton(section, text="Show album name", variable=self.album_var).pack(anchor='w', pady=2)

		self.artist_var = tk.BooleanVar(value=display.get('artist', True))
		ttk.Checkbutton(section, text="Show artist name", variable=self.artist_var).pack(anchor='w', pady=2)

		self.album_image_var = tk.BooleanVar(value=display.get('albumImage', True))
		ttk.Checkbutton(section, text="Show album image", variable=self.album_image_var).pack(anchor='w', pady=2)

		self.artist_image_var = tk.BooleanVar(value=display.get('artistImage', True))
		ttk.Checkbutton(section, text="Show artist image", variable=self.artist_image_var).pack(anchor='w', pady=2)

		# Progress Display Section
		section = ttk.LabelFrame(scrollable_frame, text="Progress Display", padding=10)
		section.pack(fill='x', padx=10, pady=5)

		ttk.Label(section, text="Progress Mode:").pack(anchor='w', pady=2)
		self.progress_mode_var = tk.StringVar(value=display.get('progressMode', 'bar'))

		progress_modes = [
			('Progress bar', 'bar'),
			('Elapsed time', 'elapsed'),
			('Remaining time', 'remaining'),
			('Off', 'off')
		]

		for text, value in progress_modes:
			ttk.Radiobutton(section, text=text, variable=self.progress_mode_var, value=value).pack(anchor='w', padx=20, pady=2)

		self.paused_var = tk.BooleanVar(value=display.get('paused', False))
		ttk.Checkbutton(section, text="Show Rich Presence while paused", variable=self.paused_var).pack(anchor='w', pady=5)

		self.status_icon_var = tk.BooleanVar(value=display.get('statusIcon', False))
		ttk.Checkbutton(section, text="Show status icon (playing/paused/buffering)", variable=self.status_icon_var).pack(anchor='w', pady=2)

	def _build_posters_tab(self, parent):
		"""Build the Posters & Images tab"""
		# Create scrollable frame
		canvas = tk.Canvas(parent)
		scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
		scrollable_frame = ttk.Frame(canvas)

		scrollable_frame.bind(
			"<Configure>",
			lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
		)

		canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
		canvas.configure(yscrollcommand=scrollbar.set)

		canvas.pack(side="left", fill="both", expand=True)
		scrollbar.pack(side="right", fill="y")

		display = self.config.get('display', {})
		posters = display.get('posters', {})

		# Poster Settings Section
		section = ttk.LabelFrame(scrollable_frame, text="Poster Settings", padding=10)
		section.pack(fill='x', padx=10, pady=5)

		self.posters_enabled_var = tk.BooleanVar(value=posters.get('enabled', False))
		ttk.Checkbutton(
			section,
			text="Enable poster display (requires Imgur Client ID)",
			variable=self.posters_enabled_var,
			command=self._toggle_imgur_fields
		).pack(anchor='w', pady=5)

		# Imgur Client ID
		ttk.Label(section, text="Imgur Client ID:").pack(anchor='w', pady=(10, 2))

		self.imgur_client_id_var = tk.StringVar(value=posters.get('imgurClientID', ''))
		self.imgur_entry = ttk.Entry(section, textvariable=self.imgur_client_id_var, width=50)
		self.imgur_entry.pack(anchor='w', pady=2)

		# Help text
		help_frame = ttk.Frame(section)
		help_frame.pack(fill='x', pady=5)

		help_text = tk.Text(help_frame, height=4, wrap='word', bg='#f0f0f0', relief='flat', font=('TkDefaultFont', 9))
		help_text.pack(fill='x')
		help_text.insert('1.0',
			"To get an Imgur Client ID:\n"
			"1. Go to https://api.imgur.com/oauth2/addclient\n"
			"2. Enter any name and select 'OAuth 2 authorization without a callback URL'\n"
			"3. Copy the Client ID here"
		)
		help_text.config(state='disabled')

		# Max Size
		ttk.Label(section, text="Maximum poster size (width/height in pixels):").pack(anchor='w', pady=(10, 2))

		self.max_size_var = tk.IntVar(value=posters.get('maxSize', 256))
		size_frame = ttk.Frame(section)
		size_frame.pack(anchor='w', pady=2)

		self.max_size_spinbox = ttk.Spinbox(size_frame, from_=64, to=1024, textvariable=self.max_size_var, width=10)
		self.max_size_spinbox.pack(side='left')
		ttk.Label(size_frame, text="px (larger = better quality, slower upload)").pack(side='left', padx=5)

		self._toggle_imgur_fields()

	def _build_logging_tab(self, parent):
		"""Build the Logging tab"""
		# Create scrollable frame
		canvas = tk.Canvas(parent)
		scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
		scrollable_frame = ttk.Frame(canvas)

		scrollable_frame.bind(
			"<Configure>",
			lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
		)

		canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
		canvas.configure(yscrollcommand=scrollbar.set)

		canvas.pack(side="left", fill="both", expand=True)
		scrollbar.pack(side="right", fill="y")

		logging = self.config.get('logging', {})

		# Logging Settings Section
		section = ttk.LabelFrame(scrollable_frame, text="Logging Settings", padding=10)
		section.pack(fill='x', padx=10, pady=5)

		self.debug_var = tk.BooleanVar(value=logging.get('debug', True))
		ttk.Checkbutton(section, text="Enable debug logging", variable=self.debug_var).pack(anchor='w', pady=5)

		ttk.Label(section, text="Debug mode provides detailed information for troubleshooting.", font=('TkDefaultFont', 9)).pack(anchor='w', padx=20, pady=2)

		self.write_to_file_var = tk.BooleanVar(value=logging.get('writeToFile', False))
		ttk.Checkbutton(section, text="Write logs to file", variable=self.write_to_file_var).pack(anchor='w', pady=5)

		ttk.Label(section, text="Note: System tray mode always writes logs to file.", font=('TkDefaultFont', 9)).pack(anchor='w', padx=20, pady=2)

	def _toggle_imgur_fields(self):
		"""Enable/disable Imgur-related fields based on checkbox"""
		state = 'normal' if self.posters_enabled_var.get() else 'disabled'
		self.imgur_entry.config(state=state)
		self.max_size_spinbox.config(state=state)

	def _save_config(self):
		"""Save configuration and call the callback"""
		# Update config dictionary with form values

		# Display settings
		if 'display' not in self.config:
			self.config['display'] = {}

		self.config['display']['duration'] = self.duration_var.get()
		self.config['display']['year'] = self.year_var.get()
		self.config['display']['genres'] = self.genres_var.get()
		self.config['display']['album'] = self.album_var.get()
		self.config['display']['artist'] = self.artist_var.get()
		self.config['display']['albumImage'] = self.album_image_var.get()
		self.config['display']['artistImage'] = self.artist_image_var.get()
		self.config['display']['progressMode'] = self.progress_mode_var.get()
		self.config['display']['paused'] = self.paused_var.get()
		self.config['display']['statusIcon'] = self.status_icon_var.get()

		# Poster settings
		if 'posters' not in self.config['display']:
			self.config['display']['posters'] = {}

		self.config['display']['posters']['enabled'] = self.posters_enabled_var.get()
		self.config['display']['posters']['imgurClientID'] = self.imgur_client_id_var.get()
		self.config['display']['posters']['maxSize'] = self.max_size_var.get()

		# Logging settings
		if 'logging' not in self.config:
			self.config['logging'] = {}

		self.config['logging']['debug'] = self.debug_var.get()
		self.config['logging']['writeToFile'] = self.write_to_file_var.get()

		# Validate
		if self.posters_enabled_var.get() and not self.imgur_client_id_var.get().strip():
			messagebox.showwarning(
				"Validation Error",
				"Imgur Client ID is required when poster display is enabled.\n\n"
				"Please provide a Client ID or disable poster display."
			)
			return

		# Close window
		self.window.destroy()
		self.window = None

		# Call the save callback
		self.on_save(self.config)

	def _cancel(self):
		"""Cancel and close the window"""
		self.window.destroy()
		self.window = None

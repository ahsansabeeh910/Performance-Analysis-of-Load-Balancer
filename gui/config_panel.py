"""Configuration panel for the load balancer simulation GUI."""
import tkinter as tk
from tkinter import ttk
from typing import Callable, Dict, List, Optional


class ConfigPanel(ttk.LabelFrame):
    """Left panel containing simulation configuration controls.
    
    Provides controls for:
    - Number of servers (slider)
    - Number of requests (entry)
    - Arrival rate (slider)
    - Service rate (slider)
    - Algorithm selection (checkboxes)
    - Server weight configuration
    - Run button and progress bar
    """

    def __init__(self, parent, on_run_callback: Callable, **kwargs):
        super().__init__(parent, text="  ⚙  Simulation Configuration  ", **kwargs)
        self.on_run_callback = on_run_callback
        self._weight_entries: List[tk.Entry] = []
        self._setup_ui()

    def _setup_ui(self):
        """Set up all configuration controls."""
        # Main container with padding
        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        row = 0

        # --- Server Configuration ---
        ttk.Label(container, text="Server Configuration",
                  font=('Segoe UI', 11, 'bold')).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 8))
        row += 1

        # Number of servers
        ttk.Label(container, text="Number of Servers:").grid(
            row=row, column=0, sticky=tk.W, pady=4)
        self.num_servers_var = tk.IntVar(value=4)
        self.num_servers_slider = ttk.Scale(
            container, from_=2, to=10, variable=self.num_servers_var,
            orient=tk.HORIZONTAL, command=self._on_server_count_change)
        self.num_servers_slider.grid(row=row, column=1, sticky=tk.EW, padx=(10, 0), pady=4)
        self.num_servers_label = ttk.Label(container, text="4")
        self.num_servers_label.grid(row=row, column=2, padx=(5, 0))
        row += 1

        # Server capacity
        ttk.Label(container, text="Server Capacity:").grid(
            row=row, column=0, sticky=tk.W, pady=4)
        self.capacity_var = tk.IntVar(value=3)
        capacity_spin = ttk.Spinbox(container, from_=1, to=20,
                                     textvariable=self.capacity_var, width=8)
        capacity_spin.grid(row=row, column=1, sticky=tk.W, padx=(10, 0), pady=4)
        row += 1

        # Separator
        ttk.Separator(container, orient=tk.HORIZONTAL).grid(
            row=row, column=0, columnspan=3, sticky=tk.EW, pady=10)
        row += 1

        # --- Traffic Configuration ---
        ttk.Label(container, text="Traffic Configuration",
                  font=('Segoe UI', 11, 'bold')).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 8))
        row += 1

        # Number of requests
        ttk.Label(container, text="Number of Requests:").grid(
            row=row, column=0, sticky=tk.W, pady=4)
        self.num_requests_var = tk.IntVar(value=500)
        requests_spin = ttk.Spinbox(container, from_=50, to=5000, increment=50,
                                     textvariable=self.num_requests_var, width=8)
        requests_spin.grid(row=row, column=1, sticky=tk.W, padx=(10, 0), pady=4)
        row += 1

        # Arrival rate
        ttk.Label(container, text="Arrival Rate (req/s):").grid(
            row=row, column=0, sticky=tk.W, pady=4)
        self.arrival_rate_var = tk.DoubleVar(value=20.0)
        self.arrival_slider = ttk.Scale(
            container, from_=1, to=100, variable=self.arrival_rate_var,
            orient=tk.HORIZONTAL, command=self._on_arrival_change)
        self.arrival_slider.grid(row=row, column=1, sticky=tk.EW, padx=(10, 0), pady=4)
        self.arrival_label = ttk.Label(container, text="20.0")
        self.arrival_label.grid(row=row, column=2, padx=(5, 0))
        row += 1

        # Service rate
        ttk.Label(container, text="Service Rate (req/s):").grid(
            row=row, column=0, sticky=tk.W, pady=4)
        self.service_rate_var = tk.DoubleVar(value=8.0)
        self.service_slider = ttk.Scale(
            container, from_=1, to=50, variable=self.service_rate_var,
            orient=tk.HORIZONTAL, command=self._on_service_change)
        self.service_slider.grid(row=row, column=1, sticky=tk.EW, padx=(10, 0), pady=4)
        self.service_label = ttk.Label(container, text="8.0")
        self.service_label.grid(row=row, column=2, padx=(5, 0))
        row += 1

        # Separator
        ttk.Separator(container, orient=tk.HORIZONTAL).grid(
            row=row, column=0, columnspan=3, sticky=tk.EW, pady=10)
        row += 1

        # --- Algorithm Selection ---
        ttk.Label(container, text="Algorithms to Compare",
                  font=('Segoe UI', 11, 'bold')).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 8))
        row += 1

        self.algo_vars = {}
        algorithms = ["Round Robin", "Least Connections", "Weighted Round Robin"]
        for algo in algorithms:
            var = tk.BooleanVar(value=True)
            self.algo_vars[algo] = var
            cb = ttk.Checkbutton(container, text=algo, variable=var)
            cb.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2)
            row += 1

        # Separator
        ttk.Separator(container, orient=tk.HORIZONTAL).grid(
            row=row, column=0, columnspan=3, sticky=tk.EW, pady=10)
        row += 1

        # --- Server Weights (for WRR) ---
        ttk.Label(container, text="Server Weights (WRR)",
                  font=('Segoe UI', 11, 'bold')).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 8))
        row += 1

        self.weights_frame = ttk.Frame(container)
        self.weights_frame.grid(row=row, column=0, columnspan=3, sticky=tk.EW)
        self._build_weight_entries()
        row += 1

        # Separator
        ttk.Separator(container, orient=tk.HORIZONTAL).grid(
            row=row, column=0, columnspan=3, sticky=tk.EW, pady=10)
        row += 1

        # --- Run Button ---
        self.run_btn = ttk.Button(container, text="▶  Run Simulation",
                                   command=self._on_run, style='Accent.TButton')
        self.run_btn.grid(row=row, column=0, columnspan=3, sticky=tk.EW, pady=(5, 8), ipady=8)
        row += 1

        # Progress bar
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(container, variable=self.progress_var,
                                             maximum=100, mode='determinate')
        self.progress_bar.grid(row=row, column=0, columnspan=3, sticky=tk.EW, pady=(0, 5))
        row += 1

        self.status_label = ttk.Label(container, text="Ready", foreground='#A6E3A1')
        self.status_label.grid(row=row, column=0, columnspan=3, sticky=tk.W)

        # Configure column weights
        container.columnconfigure(1, weight=1)

    def _build_weight_entries(self):
        """Build weight entry fields based on server count."""
        for widget in self.weights_frame.winfo_children():
            widget.destroy()
        self._weight_entries.clear()

        num = self.num_servers_var.get()
        default_weights = [5, 3, 2, 1, 1, 1, 1, 1, 1, 1]

        for i in range(num):
            frame = ttk.Frame(self.weights_frame)
            frame.pack(side=tk.LEFT, padx=2)
            ttk.Label(frame, text=f"S{i}", font=('Segoe UI', 8)).pack()
            entry = ttk.Entry(frame, width=3, justify=tk.CENTER)
            entry.insert(0, str(default_weights[i] if i < len(default_weights) else 1))
            entry.pack()
            self._weight_entries.append(entry)

    def _on_server_count_change(self, *args):
        """Handle server count slider change."""
        val = int(float(self.num_servers_var.get()))
        self.num_servers_var.set(val)
        self.num_servers_label.config(text=str(val))
        self._build_weight_entries()

    def _on_arrival_change(self, *args):
        """Handle arrival rate slider change."""
        val = round(float(self.arrival_rate_var.get()), 1)
        self.arrival_label.config(text=str(val))

    def _on_service_change(self, *args):
        """Handle service rate slider change."""
        val = round(float(self.service_rate_var.get()), 1)
        self.service_label.config(text=str(val))

    def _on_run(self):
        """Validate inputs and trigger simulation."""
        selected_algos = [name for name, var in self.algo_vars.items() if var.get()]
        if not selected_algos:
            self.status_label.config(text="⚠ Select at least one algorithm!",
                                     foreground='#F38BA8')
            return

        weights = []
        for entry in self._weight_entries:
            try:
                w = int(entry.get())
                if w < 1:
                    raise ValueError
                weights.append(w)
            except ValueError:
                self.status_label.config(text="⚠ Weights must be positive integers!",
                                         foreground='#F38BA8')
                return

        config = {
            'num_servers': self.num_servers_var.get(),
            'num_requests': self.num_requests_var.get(),
            'arrival_rate': self.arrival_rate_var.get(),
            'service_rate': self.service_rate_var.get(),
            'server_capacity': self.capacity_var.get(),
            'algorithms': selected_algos,
            'weights': weights,
        }

        self.run_btn.config(state=tk.DISABLED)
        self.status_label.config(text="⏳ Running simulation...", foreground='#FAB387')
        self.progress_var.set(0)

        self.on_run_callback(config)

    def set_progress(self, value: float, status: str = ""):
        """Update progress bar and status."""
        self.progress_var.set(value)
        if status:
            self.status_label.config(text=status)
        self.update_idletasks()

    def simulation_complete(self):
        """Reset UI state after simulation completes."""
        self.run_btn.config(state=tk.NORMAL)
        self.progress_var.set(100)
        self.status_label.config(text="✅ Simulation complete!", foreground='#A6E3A1')

    def get_config(self) -> Dict:
        """Get current configuration values."""
        weights = []
        for entry in self._weight_entries:
            try:
                weights.append(int(entry.get()))
            except ValueError:
                weights.append(1)

        return {
            'num_servers': self.num_servers_var.get(),
            'num_requests': self.num_requests_var.get(),
            'arrival_rate': self.arrival_rate_var.get(),
            'service_rate': self.service_rate_var.get(),
            'server_capacity': self.capacity_var.get(),
            'algorithms': [name for name, var in self.algo_vars.items() if var.get()],
            'weights': weights,
        }

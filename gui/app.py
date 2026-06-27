"""Main application window for Load Balancer Performance Analysis."""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import sys
import os
import json
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulation.engine import SimulationEngine
from metrics.collector import MetricsCollector
from gui.config_panel import ConfigPanel
from gui.results_panel import ResultsPanel
from gui.chart_panel import ChartPanel


class LoadBalancerApp:
    """Main Tkinter application for Load Balancer Performance Analysis.
    
    Provides a three-panel layout:
    - Left: Configuration panel
    - Right: Results panel with metrics table
    - Bottom: Chart panel with tabbed visualizations
    """

    APP_TITLE = "Performance Analysis of Load Balancers"
    MIN_WIDTH = 1280
    MIN_HEIGHT = 800

    def __init__(self):
        self.root = tk.Tk()
        self.root.title(self.APP_TITLE)
        self.root.geometry(f"{self.MIN_WIDTH}x{self.MIN_HEIGHT}")
        self.root.minsize(self.MIN_WIDTH, self.MIN_HEIGHT)

        # Store simulation results
        self.all_metrics = {}
        self.all_summaries = {}
        self.all_requests = {}

        self._setup_theme()
        self._setup_menu()
        self._setup_layout()

    def _setup_theme(self):
        """Configure the application theme with a modern dark look."""
        style = ttk.Style()
        
        # Try to use a modern theme
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')
        
        # Dark color palette (Catppuccin Mocha inspired)
        bg = '#1E1E2E'
        fg = '#CDD6F4'
        surface = '#313244'
        overlay = '#45475A'
        accent = '#89B4FA'
        green = '#A6E3A1'
        red = '#F38BA8'
        yellow = '#F9E2AF'

        self.root.configure(bg=bg)

        # Configure styles
        style.configure('.', background=bg, foreground=fg, fieldbackground=surface,
                       bordercolor=overlay, troughcolor=surface,
                       selectbackground=accent, selectforeground=bg)
        
        style.configure('TFrame', background=bg)
        style.configure('TLabel', background=bg, foreground=fg, font=('Segoe UI', 10))
        style.configure('TLabelframe', background=bg, foreground=accent,
                       font=('Segoe UI', 11, 'bold'))
        style.configure('TLabelframe.Label', background=bg, foreground=accent,
                       font=('Segoe UI', 11, 'bold'))
        style.configure('TButton', background=surface, foreground=fg,
                       font=('Segoe UI', 10, 'bold'), padding=6)
        style.map('TButton',
                 background=[('active', overlay), ('pressed', accent)],
                 foreground=[('active', fg), ('pressed', bg)])
        
        style.configure('Accent.TButton', background=accent, foreground=bg,
                       font=('Segoe UI', 11, 'bold'), padding=8)
        style.map('Accent.TButton',
                 background=[('active', '#74C7EC'), ('pressed', '#89B4FA'),
                            ('disabled', overlay)],
                 foreground=[('disabled', '#585B70')])
        
        style.configure('TCheckbutton', background=bg, foreground=fg,
                       font=('Segoe UI', 10))
        style.map('TCheckbutton', background=[('active', bg)])
        
        style.configure('TScale', background=bg, troughcolor=surface)
        
        style.configure('TNotebook', background=bg, bordercolor=overlay)
        style.configure('TNotebook.Tab', background=surface, foreground=fg,
                       font=('Segoe UI', 9, 'bold'), padding=[12, 6])
        style.map('TNotebook.Tab',
                 background=[('selected', accent)],
                 foreground=[('selected', bg)])
        
        style.configure('Treeview', background=surface, foreground=fg,
                       fieldbackground=surface, font=('Segoe UI', 9),
                       rowheight=28)
        style.configure('Treeview.Heading', background=overlay, foreground=fg,
                       font=('Segoe UI', 9, 'bold'))
        style.map('Treeview', background=[('selected', accent)],
                 foreground=[('selected', bg)])
        
        style.configure('TProgressbar', background=accent, troughcolor=surface,
                       bordercolor=overlay, lightcolor=accent, darkcolor=accent)
        
        style.configure('TSeparator', background=overlay)
        
        style.configure('TSpinbox', fieldbackground=surface, foreground=fg,
                       background=surface, arrowcolor=fg)
        
        style.configure('TEntry', fieldbackground=surface, foreground=fg)

    def _setup_menu(self):
        """Create the application menu bar."""
        menubar = tk.Menu(self.root, bg='#313244', fg='#CDD6F4',
                         activebackground='#89B4FA', activeforeground='#1E1E2E')
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg='#313244', fg='#CDD6F4',
                           activebackground='#89B4FA', activeforeground='#1E1E2E')
        file_menu.add_command(label="Export Results as JSON",
                             command=self._export_json)
        file_menu.add_command(label="Export Results as CSV",
                             command=self._export_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, bg='#313244', fg='#CDD6F4',
                           activebackground='#89B4FA', activeforeground='#1E1E2E')
        help_menu.add_command(label="About", command=self._show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)

    def _setup_layout(self):
        """Create the three-panel layout."""
        # Title bar
        title_frame = ttk.Frame(self.root)
        title_frame.pack(fill=tk.X, padx=15, pady=(10, 5))
        
        ttk.Label(title_frame, text="⚡ Performance Analysis of Load Balancers",
                  font=('Segoe UI', 18, 'bold'),
                  foreground='#89B4FA').pack(side=tk.LEFT)
        
        ttk.Label(title_frame, text="Discrete-Event Simulation Engine",
                  font=('Segoe UI', 10),
                  foreground='#6C7086').pack(side=tk.LEFT, padx=(15, 0), pady=(8, 0))

        # Main paned window (horizontal: config | results)
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Left: Config panel
        self.config_panel = ConfigPanel(main_paned, on_run_callback=self._run_simulation)
        main_paned.add(self.config_panel, weight=1)

        # Right: Vertical split (results on top, charts on bottom)
        right_paned = ttk.PanedWindow(main_paned, orient=tk.VERTICAL)
        main_paned.add(right_paned, weight=3)

        # Results panel
        self.results_panel = ResultsPanel(right_paned)
        right_paned.add(self.results_panel, weight=1)

        # Chart panel
        self.chart_panel = ChartPanel(right_paned)
        right_paned.add(self.chart_panel, weight=2)

    def _run_simulation(self, config: dict):
        """Run the simulation in a background thread.
        
        Args:
            config: Dictionary containing simulation configuration
        """
        def _simulation_thread():
            try:
                self.all_metrics = {}
                self.all_summaries = {}
                self.all_requests = {}

                algorithms = config['algorithms']
                total_algos = len(algorithms)

                for idx, algo in enumerate(algorithms):
                    # Update progress
                    self.root.after(0, self.config_panel.set_progress,
                                  (idx / total_algos) * 100,
                                  f"⏳ Running {algo}...")

                    # Create and run simulation
                    engine = SimulationEngine(
                        num_servers=config['num_servers'],
                        num_requests=config['num_requests'],
                        arrival_rate=config['arrival_rate'],
                        service_rate=config['service_rate'],
                        algorithm=algo,
                        server_weights=config['weights'],
                        server_capacity=config['server_capacity'],
                    )

                    results = engine.run()

                    # Collect metrics
                    collector = MetricsCollector(
                        results['requests'],
                        results['servers'],
                        results['simulation_time']
                    )

                    self.all_metrics[algo] = collector.compute_all()
                    self.all_summaries[algo] = collector.get_summary()
                    self.all_requests[algo] = results['requests']

                # Update UI on main thread
                self.root.after(0, self._update_ui)

            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(
                    "Simulation Error", f"An error occurred:\n{str(e)}"))
                self.root.after(0, self.config_panel.simulation_complete)

        thread = threading.Thread(target=_simulation_thread, daemon=True)
        thread.start()

    def _update_ui(self):
        """Update results and charts panels with simulation data."""
        self.results_panel.update_results(self.all_summaries, self.all_metrics)
        self.chart_panel.update_charts(self.all_metrics, self.all_requests)
        self.config_panel.simulation_complete()

    def _export_json(self):
        """Export results to a JSON file."""
        if not self.all_metrics:
            messagebox.showwarning("No Data", "Run a simulation first!")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension='.json',
            filetypes=[('JSON files', '*.json')],
            initialfile=f'lb_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        )
        if filepath:
            data = {
                'timestamp': datetime.now().isoformat(),
                'config': self.config_panel.get_config(),
                'metrics': self.all_metrics,
                'summaries': self.all_summaries,
            }
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            messagebox.showinfo("Exported", f"Results saved to {filepath}")

    def _export_csv(self):
        """Export summary results to a CSV file."""
        if not self.all_summaries:
            messagebox.showwarning("No Data", "Run a simulation first!")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension='.csv',
            filetypes=[('CSV files', '*.csv')],
            initialfile=f'lb_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
        if filepath:
            import csv
            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Algorithm', 'Avg Response Time (s)',
                               'P95 Response Time (s)', 'Throughput (req/s)',
                               'Avg Utilization (%)', 'Load Efficiency (%)'])
                for algo, summary in self.all_summaries.items():
                    writer.writerow([
                        algo,
                        summary['avg_response_time'],
                        summary['p95_response_time'],
                        summary['throughput'],
                        summary['avg_utilization'],
                        summary['load_efficiency'],
                    ])
            messagebox.showinfo("Exported", f"Results saved to {filepath}")

    def _show_about(self):
        """Show about dialog."""
        messagebox.showinfo(
            "About",
            f"{self.APP_TITLE}\n\n"
            "A discrete-event simulation tool for evaluating\n"
            "and comparing load balancing algorithms.\n\n"
            "Algorithms: Round Robin, Least Connections,\n"
            "Weighted Round Robin\n\n"
            "Built with Python, SimPy, NumPy, Matplotlib & Tkinter\n\n"
            "Performance Engineering Lab [17M15CS122]"
        )

    def run(self):
        """Start the application main loop."""
        # Center window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - self.MIN_WIDTH) // 2
        y = (self.root.winfo_screenheight() - self.MIN_HEIGHT) // 2
        self.root.geometry(f"+{x}+{y}")
        
        self.root.mainloop()

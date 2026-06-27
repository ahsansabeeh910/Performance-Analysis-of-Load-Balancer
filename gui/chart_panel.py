"""Chart panel for embedded Matplotlib visualizations."""
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from typing import Dict, List, Optional
from visualization.charts import ChartGenerator


class ChartPanel(ttk.LabelFrame):
    """Bottom panel with tabbed Matplotlib chart views.
    
    Displays multiple chart types in a tabbed notebook, each with
    embedded Matplotlib figures and navigation toolbars.
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, text="  📈  Performance Charts  ", **kwargs)
        self._canvases: List[FigureCanvasTkAgg] = []
        self._setup_ui()

    def _setup_ui(self):
        """Set up the tabbed chart view."""
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Placeholder
        placeholder = ttk.Frame(self.notebook)
        ttk.Label(placeholder, text="Run a simulation to generate charts.",
                  font=('Segoe UI', 12)).pack(expand=True)
        self.notebook.add(placeholder, text="  Charts  ")

    def update_charts(self, all_metrics: Dict[str, Dict],
                      all_requests: Dict[str, list]):
        """Update all charts with new simulation data.
        
        Args:
            all_metrics: Dict mapping algorithm name -> computed metrics
            all_requests: Dict mapping algorithm name -> list of Request objects
        """
        # Clear existing tabs and canvases
        self._cleanup()

        # Generate and embed each chart type
        charts = [
            ("Response Time", ChartGenerator.plot_response_time_comparison(all_metrics)),
            ("Throughput", ChartGenerator.plot_throughput_comparison(all_metrics)),
            ("Server Utilization", ChartGenerator.plot_server_utilization(all_metrics)),
            ("Load Distribution", ChartGenerator.plot_load_distribution(all_metrics)),
            ("RT Distribution", ChartGenerator.plot_response_time_distribution(
                all_metrics, all_requests)),
        ]

        for title, fig in charts:
            tab = ttk.Frame(self.notebook)
            self.notebook.add(tab, text=f"  {title}  ")

            canvas = FigureCanvasTkAgg(fig, master=tab)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            self._canvases.append(canvas)

            # Navigation toolbar
            toolbar_frame = ttk.Frame(tab)
            toolbar_frame.pack(fill=tk.X)
            toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
            toolbar.update()

    def _cleanup(self):
        """Clean up existing charts and tabs."""
        import matplotlib.pyplot as plt
        for canvas in self._canvases:
            plt.close(canvas.figure)
            canvas.get_tk_widget().destroy()
        self._canvases.clear()

        for tab_id in self.notebook.tabs():
            self.notebook.forget(tab_id)

    def clear(self):
        """Clear all charts."""
        self._cleanup()
        placeholder = ttk.Frame(self.notebook)
        ttk.Label(placeholder, text="Run a simulation to generate charts.",
                  font=('Segoe UI', 12)).pack(expand=True)
        self.notebook.add(placeholder, text="  Charts  ")

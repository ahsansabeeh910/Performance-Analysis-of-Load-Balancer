"""Results panel for displaying simulation metrics."""
import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional


class ResultsPanel(ttk.LabelFrame):
    """Right panel displaying simulation metrics in a table.
    
    Shows a Treeview table with columns for each performance metric.
    Highlights the best-performing algorithm for each metric.
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, text="  📊  Simulation Results  ", **kwargs)
        self._setup_ui()

    def _setup_ui(self):
        """Set up the results table and summary."""
        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Header
        ttk.Label(container, text="Performance Metrics Comparison",
                  font=('Segoe UI', 12, 'bold')).pack(anchor=tk.W, pady=(0, 10))

        # Treeview table
        columns = ('algorithm', 'avg_rt', 'p95_rt', 'throughput',
                   'avg_util', 'load_eff')
        self.tree = ttk.Treeview(container, columns=columns, show='headings',
                                 height=5, selectmode='browse')

        self.tree.heading('algorithm', text='Algorithm')
        self.tree.heading('avg_rt', text='Avg Response (s)')
        self.tree.heading('p95_rt', text='P95 Response (s)')
        self.tree.heading('throughput', text='Throughput (req/s)')
        self.tree.heading('avg_util', text='Avg Util (%)')
        self.tree.heading('load_eff', text='Load Efficiency (%)')

        self.tree.column('algorithm', width=160, anchor=tk.W)
        self.tree.column('avg_rt', width=120, anchor=tk.CENTER)
        self.tree.column('p95_rt', width=120, anchor=tk.CENTER)
        self.tree.column('throughput', width=120, anchor=tk.CENTER)
        self.tree.column('avg_util', width=100, anchor=tk.CENTER)
        self.tree.column('load_eff', width=120, anchor=tk.CENTER)

        self.tree.pack(fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL,
                                   command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Summary frame
        self.summary_frame = ttk.LabelFrame(container, text="  🏆  Best Algorithm  ")
        self.summary_frame.pack(fill=tk.X, pady=(10, 0))

        self.summary_label = ttk.Label(
            self.summary_frame,
            text="Run a simulation to see results.",
            font=('Segoe UI', 10),
            wraplength=450
        )
        self.summary_label.pack(padx=10, pady=8)

        # Details frame
        self.details_frame = ttk.LabelFrame(container, text="  📋  Detailed Metrics  ")
        self.details_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        self.details_text = tk.Text(
            self.details_frame, height=10, wrap=tk.WORD,
            font=('Consolas', 9), bg='#1E1E2E', fg='#CDD6F4',
            insertbackground='#CDD6F4', selectbackground='#45475A',
            relief=tk.FLAT, padx=10, pady=8
        )
        self.details_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.details_text.config(state=tk.DISABLED)

    def update_results(self, all_summaries: Dict[str, Dict],
                       all_metrics: Dict[str, Dict]):
        """Update the results table with new simulation data.
        
        Args:
            all_summaries: Dict mapping algorithm name -> summary metrics
            all_metrics: Dict mapping algorithm name -> full computed metrics
        """
        # Clear existing rows
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Configure tags for highlighting
        self.tree.tag_configure('best', background='#2D4F2D')
        self.tree.tag_configure('normal', background='')

        # Find best values
        if all_summaries:
            best_rt = min(all_summaries.values(), key=lambda x: x['avg_response_time'])
            best_throughput = max(all_summaries.values(), key=lambda x: x['throughput'])
            best_efficiency = max(all_summaries.values(), key=lambda x: x['load_efficiency'])

        # Insert rows
        for algo, summary in all_summaries.items():
            tags = []
            # Determine if this is the overall best (lowest avg response time)
            if summary['avg_response_time'] == best_rt['avg_response_time']:
                tags.append('best')

            self.tree.insert('', tk.END, values=(
                algo,
                f"{summary['avg_response_time']:.4f}",
                f"{summary['p95_response_time']:.4f}",
                f"{summary['throughput']:.2f}",
                f"{summary['avg_utilization']:.2f}",
                f"{summary['load_efficiency']:.2f}",
            ), tags=tags if tags else ('normal',))

        # Update summary
        if all_summaries:
            best_algo = min(all_summaries.keys(),
                          key=lambda a: all_summaries[a]['avg_response_time'])
            best_data = all_summaries[best_algo]
            self.summary_label.config(
                text=f"🥇 {best_algo} performs best with "
                     f"avg response time of {best_data['avg_response_time']:.4f}s "
                     f"and throughput of {best_data['throughput']:.2f} req/s"
            )

        # Update detailed metrics
        self._update_details(all_metrics)

    def _update_details(self, all_metrics: Dict[str, Dict]):
        """Update the detailed metrics text view."""
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete('1.0', tk.END)

        for algo, metrics in all_metrics.items():
            self.details_text.insert(tk.END, f"{'='*50}\n")
            self.details_text.insert(tk.END, f"  {algo}\n")
            self.details_text.insert(tk.END, f"{'='*50}\n\n")

            rt = metrics['response_time']
            self.details_text.insert(tk.END, f"  Response Time:\n")
            self.details_text.insert(tk.END, f"    Average:  {rt['avg']:.4f}s\n")
            self.details_text.insert(tk.END, f"    Min:      {rt['min']:.4f}s\n")
            self.details_text.insert(tk.END, f"    Max:      {rt['max']:.4f}s\n")
            self.details_text.insert(tk.END, f"    P95:      {rt['p95']:.4f}s\n")
            self.details_text.insert(tk.END, f"    Median:   {rt['median']:.4f}s\n\n")

            tp = metrics['throughput']
            self.details_text.insert(tk.END, f"  Throughput:\n")
            self.details_text.insert(tk.END, f"    Total:    {tp['total_requests']} requests\n")
            self.details_text.insert(tk.END, f"    Rate:     {tp['requests_per_sec']:.2f} req/s\n")
            self.details_text.insert(tk.END, f"    Duration: {tp['simulation_time']:.2f}s\n\n")

            su = metrics['server_utilization']
            self.details_text.insert(tk.END, f"  Server Utilization:\n")
            for s in su['per_server']:
                self.details_text.insert(
                    tk.END,
                    f"    Server {s['server_id']}: {s['utilization']:.1f}% "
                    f"({s['total_requests']} requests, weight={s['weight']})\n"
                )
            self.details_text.insert(tk.END, f"    Average: {su['average']:.1f}%\n\n")

            ld = metrics['load_distribution']
            self.details_text.insert(tk.END, f"  Load Distribution:\n")
            self.details_text.insert(tk.END, f"    Std Dev:    {ld['std_deviation']:.2f}\n")
            self.details_text.insert(tk.END, f"    Efficiency: {ld['efficiency_score']:.1f}%\n\n")

        self.details_text.config(state=tk.DISABLED)

    def clear(self):
        """Clear all results."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.summary_label.config(text="Run a simulation to see results.")
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete('1.0', tk.END)
        self.details_text.config(state=tk.DISABLED)

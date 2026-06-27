"""Matplotlib chart generation for load balancer performance visualization."""
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np
from typing import Dict, List

# Style configuration for consistent, attractive charts
COLOR_PALETTE = {
    'Round Robin': '#4A90D9',
    'Least Connections': '#E85D75',
    'Weighted Round Robin': '#50C878',
}

BACKGROUND_COLOR = '#1E1E2E'
TEXT_COLOR = '#CDD6F4'
GRID_COLOR = '#45475A'
ACCENT_COLORS = ['#89B4FA', '#F38BA8', '#A6E3A1', '#FAB387', '#CBA6F7',
                  '#F5C2E7', '#94E2D5', '#F9E2AF', '#74C7EC', '#B4BEFE']


class ChartGenerator:
    """Generates Matplotlib charts for load balancer performance visualization.
    
    All charts use a consistent dark theme with color-coded algorithms.
    Charts are returned as Matplotlib Figure objects suitable for embedding
    in Tkinter via FigureCanvasTkAgg.
    """

    @staticmethod
    def _apply_style(fig: Figure, ax):
        """Apply consistent dark theme styling to a chart."""
        fig.set_facecolor(BACKGROUND_COLOR)
        ax.set_facecolor('#181825')
        ax.tick_params(colors=TEXT_COLOR, labelsize=9)
        ax.xaxis.label.set_color(TEXT_COLOR)
        ax.yaxis.label.set_color(TEXT_COLOR)
        ax.title.set_color(TEXT_COLOR)
        ax.spines['bottom'].set_color(GRID_COLOR)
        ax.spines['left'].set_color(GRID_COLOR)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(True, alpha=0.15, color=GRID_COLOR)

    @staticmethod
    def plot_response_time_comparison(all_metrics: Dict[str, Dict]) -> Figure:
        """Create a grouped bar chart comparing response time metrics.
        
        Shows avg, min, max, p95, and median response times for each algorithm.
        
        Args:
            all_metrics: Dict mapping algorithm name -> computed metrics
            
        Returns:
            Matplotlib Figure
        """
        fig, ax = plt.subplots(figsize=(8, 5))
        ChartGenerator._apply_style(fig, ax)
        
        algorithms = list(all_metrics.keys())
        metrics_labels = ['Avg', 'Min', 'Max', 'P95', 'Median']
        metrics_keys = ['avg', 'min', 'max', 'p95', 'median']
        
        x = np.arange(len(metrics_labels))
        width = 0.8 / len(algorithms)
        
        for i, algo in enumerate(algorithms):
            rt = all_metrics[algo]['response_time']
            values = [rt[k] for k in metrics_keys]
            color = COLOR_PALETTE.get(algo, ACCENT_COLORS[i % len(ACCENT_COLORS)])
            bars = ax.bar(x + i * width - (len(algorithms) - 1) * width / 2,
                         values, width, label=algo, color=color,
                         alpha=0.85, edgecolor='white', linewidth=0.5)
            # Add value labels on bars
            for bar, val in zip(bars, values):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.001,
                       f'{val:.3f}', ha='center', va='bottom', fontsize=7,
                       color=TEXT_COLOR, fontweight='bold')
        
        ax.set_xlabel('Metric', fontsize=11, fontweight='bold')
        ax.set_ylabel('Time (seconds)', fontsize=11, fontweight='bold')
        ax.set_title('Response Time Comparison', fontsize=14, fontweight='bold', pad=15)
        ax.set_xticks(x)
        ax.set_xticklabels(metrics_labels)
        legend = ax.legend(loc='upper right', fontsize=9, facecolor='#313244',
                          edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR)
        
        fig.tight_layout()
        return fig

    @staticmethod
    def plot_throughput_comparison(all_metrics: Dict[str, Dict]) -> Figure:
        """Create a bar chart comparing throughput across algorithms.
        
        Args:
            all_metrics: Dict mapping algorithm name -> computed metrics
            
        Returns:
            Matplotlib Figure
        """
        fig, ax = plt.subplots(figsize=(8, 5))
        ChartGenerator._apply_style(fig, ax)
        
        algorithms = list(all_metrics.keys())
        throughputs = [all_metrics[a]['throughput']['requests_per_sec'] for a in algorithms]
        colors = [COLOR_PALETTE.get(a, ACCENT_COLORS[i % len(ACCENT_COLORS)]) 
                  for i, a in enumerate(algorithms)]
        
        bars = ax.bar(algorithms, throughputs, color=colors, alpha=0.85,
                     edgecolor='white', linewidth=0.5, width=0.5)
        
        for bar, val in zip(bars, throughputs):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
                   f'{val:.2f}', ha='center', va='bottom', fontsize=10,
                   color=TEXT_COLOR, fontweight='bold')
        
        ax.set_xlabel('Algorithm', fontsize=11, fontweight='bold')
        ax.set_ylabel('Requests / Second', fontsize=11, fontweight='bold')
        ax.set_title('Throughput Comparison', fontsize=14, fontweight='bold', pad=15)
        
        fig.tight_layout()
        return fig

    @staticmethod
    def plot_server_utilization(all_metrics: Dict[str, Dict]) -> Figure:
        """Create a grouped bar chart showing per-server utilization.
        
        Args:
            all_metrics: Dict mapping algorithm name -> computed metrics
            
        Returns:
            Matplotlib Figure
        """
        fig, ax = plt.subplots(figsize=(8, 5))
        ChartGenerator._apply_style(fig, ax)
        
        algorithms = list(all_metrics.keys())
        
        # Get max server count across algorithms
        max_servers = max(
            len(all_metrics[a]['server_utilization']['per_server'])
            for a in algorithms
        )
        
        x = np.arange(max_servers)
        width = 0.8 / len(algorithms)
        
        for i, algo in enumerate(algorithms):
            per_server = all_metrics[algo]['server_utilization']['per_server']
            utilizations = [s['utilization'] for s in per_server]
            color = COLOR_PALETTE.get(algo, ACCENT_COLORS[i % len(ACCENT_COLORS)])
            bars = ax.bar(x[:len(utilizations)] + i * width - (len(algorithms) - 1) * width / 2,
                         utilizations, width, label=algo, color=color,
                         alpha=0.85, edgecolor='white', linewidth=0.5)
            for bar, val in zip(bars, utilizations):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                       f'{val:.1f}%', ha='center', va='bottom', fontsize=7,
                       color=TEXT_COLOR, fontweight='bold')
        
        ax.set_xlabel('Server ID', fontsize=11, fontweight='bold')
        ax.set_ylabel('Utilization (%)', fontsize=11, fontweight='bold')
        ax.set_title('Server Utilization by Algorithm', fontsize=14, fontweight='bold', pad=15)
        ax.set_xticks(x)
        ax.set_xticklabels([f'Server {i}' for i in range(max_servers)])
        legend = ax.legend(loc='upper right', fontsize=9, facecolor='#313244',
                          edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR)
        ax.set_ylim(0, 110)
        
        fig.tight_layout()
        return fig

    @staticmethod
    def plot_load_distribution(all_metrics: Dict[str, Dict]) -> Figure:
        """Create a grouped bar chart showing request distribution across servers.
        
        Args:
            all_metrics: Dict mapping algorithm name -> computed metrics
            
        Returns:
            Matplotlib Figure
        """
        fig, ax = plt.subplots(figsize=(8, 5))
        ChartGenerator._apply_style(fig, ax)
        
        algorithms = list(all_metrics.keys())
        max_servers = max(
            len(all_metrics[a]['load_distribution']['per_server_requests'])
            for a in algorithms
        )
        
        x = np.arange(max_servers)
        width = 0.8 / len(algorithms)
        
        for i, algo in enumerate(algorithms):
            requests_per_server = all_metrics[algo]['load_distribution']['per_server_requests']
            color = COLOR_PALETTE.get(algo, ACCENT_COLORS[i % len(ACCENT_COLORS)])
            bars = ax.bar(x[:len(requests_per_server)] + i * width - (len(algorithms) - 1) * width / 2,
                         requests_per_server, width, label=algo, color=color,
                         alpha=0.85, edgecolor='white', linewidth=0.5)
            for bar, val in zip(bars, requests_per_server):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                       str(int(val)), ha='center', va='bottom', fontsize=8,
                       color=TEXT_COLOR, fontweight='bold')
        
        ax.set_xlabel('Server ID', fontsize=11, fontweight='bold')
        ax.set_ylabel('Number of Requests', fontsize=11, fontweight='bold')
        ax.set_title('Load Distribution Across Servers', fontsize=14, fontweight='bold', pad=15)
        ax.set_xticks(x)
        ax.set_xticklabels([f'Server {i}' for i in range(max_servers)])
        legend = ax.legend(loc='upper right', fontsize=9, facecolor='#313244',
                          edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR)
        
        fig.tight_layout()
        return fig

    @staticmethod
    def plot_response_time_distribution(all_metrics: Dict[str, Dict],
                                         all_requests: Dict[str, list]) -> Figure:
        """Create a histogram showing response time distribution per algorithm.
        
        Args:
            all_metrics: Dict mapping algorithm name -> computed metrics
            all_requests: Dict mapping algorithm name -> list of Request objects
            
        Returns:
            Matplotlib Figure
        """
        fig, ax = plt.subplots(figsize=(8, 5))
        ChartGenerator._apply_style(fig, ax)
        
        for i, (algo, requests) in enumerate(all_requests.items()):
            response_times = [r.response_time for r in requests]
            color = COLOR_PALETTE.get(algo, ACCENT_COLORS[i % len(ACCENT_COLORS)])
            ax.hist(response_times, bins=30, alpha=0.6, label=algo,
                   color=color, edgecolor='white', linewidth=0.3)
        
        ax.set_xlabel('Response Time (seconds)', fontsize=11, fontweight='bold')
        ax.set_ylabel('Frequency', fontsize=11, fontweight='bold')
        ax.set_title('Response Time Distribution', fontsize=14, fontweight='bold', pad=15)
        legend = ax.legend(loc='upper right', fontsize=9, facecolor='#313244',
                          edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR)
        
        fig.tight_layout()
        return fig

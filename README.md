# Performance Analysis of Load Balancers

A discrete-event simulation tool for evaluating and comparing load balancing algorithms.
Built as part of the Performance Engineering Lab [17M15CS122] project.

## Features

- **Three Load Balancing Algorithms**: Round Robin, Least Connections, Weighted Round Robin
- **Discrete-Event Simulation**: Powered by SimPy with Poisson arrivals and exponential service times
- **Performance Metrics**: Response Time (avg/min/max/p95), Throughput, Server Utilization, Load Distribution Efficiency
- **Interactive GUI**: Tkinter-based interface with configuration panel, results table, and embedded charts
- **Visualization**: Matplotlib charts with dark theme for response time, throughput, utilization, and distribution comparisons
- **Export**: Save results as JSON or CSV

## Requirements

- Python 3.x
- SimPy
- NumPy
- Matplotlib

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

1. Configure simulation parameters in the left panel
2. Select algorithms to compare
3. Click "Run Simulation"
4. View results in the metrics table and charts
5. Export results via File menu

## Architecture

```
├── main.py                  # Entry point
├── simulation/
│   ├── server.py            # Server model
│   ├── request.py           # Request model
│   ├── load_balancer.py     # Load balancing algorithms
│   └── engine.py            # SimPy simulation engine
├── metrics/
│   └── collector.py         # Performance metrics computation
├── visualization/
│   └── charts.py            # Matplotlib chart generation
├── gui/
│   ├── app.py               # Main application window
│   ├── config_panel.py      # Configuration panel
│   ├── results_panel.py     # Results table panel
│   └── chart_panel.py       # Chart visualization panel
└── requirements.txt
```

## Load Balancing Algorithms

- **Round Robin**: Distributes requests sequentially across servers
- **Least Connections**: Routes to the server with the fewest active connections
- **Weighted Round Robin**: Distributes proportionally based on server weights

## Performance Metrics

- **Response Time**: Time from request arrival to completion
- **Throughput**: Requests processed per second
- **Server Utilization**: Percentage of time each server is busy
- **Load Distribution Efficiency**: Evenness of request distribution

"""Quick test to verify all modules import and simulation runs correctly."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from simulation.request import Request
from simulation.server import Server
from simulation.load_balancer import LoadBalancer
from simulation.engine import SimulationEngine
from metrics.collector import MetricsCollector

print("All imports successful!")

# Test all three algorithms
for algo in ["Round Robin", "Least Connections", "Weighted Round Robin"]:
    engine = SimulationEngine(
        num_servers=3,
        num_requests=100,
        arrival_rate=15,
        service_rate=8,
        algorithm=algo,
        server_weights=[5, 3, 1],
        server_capacity=2,
    )
    results = engine.run()
    collector = MetricsCollector(
        results['requests'],
        results['servers'],
        results['simulation_time']
    )
    summary = collector.get_summary()
    print(f"\n{algo}:")
    print(f"  Requests completed: {len(results['requests'])}")
    print(f"  Simulation time:    {results['simulation_time']:.2f}s")
    print(f"  Avg Response Time:  {summary['avg_response_time']:.4f}s")
    print(f"  Throughput:         {summary['throughput']:.2f} req/s")
    print(f"  Avg Utilization:    {summary['avg_utilization']:.1f}%")
    print(f"  Load Efficiency:    {summary['load_efficiency']:.1f}%")

print("\nAll tests passed!")

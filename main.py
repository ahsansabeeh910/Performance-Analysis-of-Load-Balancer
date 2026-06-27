"""Entry point for the Load Balancer Performance Analysis application."""
import sys
import os

# Ensure project root is in the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.app import LoadBalancerApp


def main():
    """Launch the Load Balancer Performance Analysis GUI."""
    app = LoadBalancerApp()
    app.run()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3

import sys
from src.interface.interface import main

def main():
    """Entry point for the CLI interface"""
    from src.interface.interface import main as interface_main
    interface_main()

if __name__ == "__main__":
    main()

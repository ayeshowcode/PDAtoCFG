# PDA to CFG Converter 🌀⇨📜

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![PyQt5](https://img.shields.io/badge/GUI-PyQt5-green.svg)](https://pypi.org/project/PyQt5/)

A graphical tool for converting Pushdown Automata (PDA) to equivalent Context-Free Grammars (CFG), featuring visual automaton design and grammar generation.

![Application Screenshot](screenshot.png) <!-- Add your screenshot here -->

## Key Features ✨

- **Visual PDA Design**: Intuitive GUI for creating states, transitions, and alphabet definitions
- **Real-time Visualization**: Automatic rendering of PDA state diagrams using Graphviz
- **CFG Conversion**: Transform PDA configurations to equivalent context-free grammars
- **Multi-format Export**: Save automata diagrams as SVG, PDF, PNG, or Graphviz files
- **XML Integration**: Save/load PDA configurations in standardized XML format
- **Dark Theme**: Modern dark-mode interface with sleek UI components

## Installation Guide 📦

### Prerequisites
- Python 3.8+
- Graphviz (for diagram rendering)
  - **Windows**: [Download installer](https://graphviz.org/download/)
  - **Linux**: `sudo apt install graphviz`

### Setup
```bash
# Clone repository
git clone https://github.com/yourusername/pda-to-cfg-converter.git
cd pda-to-cfg-converter

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
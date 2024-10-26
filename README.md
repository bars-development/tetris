# Tetris AI Project

## Overview

This project implements algorithms for a Tetris AI, focusing on polyomino transformations, optimal placement, and gameplay simulation. The AI recognizes and manipulates Tetris shapes, calculates effective placements, and achieves high scores through strategic decision-making.

## Features

1. **Polyomino Transformations**:

   - **Rotation**: Rotates pieces in 90-degree increments.
   - **Symmetry**: Reflects pieces horizontally and vertically.
   - **Complete Class Handling**: Manages all possible transformations for each polyomino.

2. **Game Simulation and AI Integration**:

   - **Automated Play**: The AI autonomously plays Tetris by analyzing game states and predicting optimal placements.
   - **Visualization**: Displays real-time AI decision-making through PyQt6.

3. **Custom Game Rules**:
   - **Rule Variants**: Train and run the AI with customized rules (e.g., only allowing symmetries, only rotations, both, or none).

## Requirements

To run the project, install the following dependencies:

```bash
pip install numpy pygame pyqt6
```

## Usage

1. **Training a Model**

   - Open the `colab_evolution.ipynb` notebook.
   - **Note**: Training is performed on the CPU and supports parallel execution. Adjust settings in the notebook to enable or disable parallel processing as needed.
   - **Compatibility**: The notebook includes Google Colab-specific options but can be run locally (recommended for parallel computing, as Colab typically uses dual-core CPUs).
   - Run the cells, adjusting training parameters as desired.
   - After each training epoch, outputs are displayed in the terminal and saved in a `results` folder for continued training.

2. **Running the Simulation**
   - Execute `uitest.py` to start the AI simulation.
   - **Adjust AI Settings**:
     - Experiment with parameters directly or train a model in the `colab_evolution.ipynb` notebook for specific tasks.
     - Test predefined parameter presets in `uitest.py`.

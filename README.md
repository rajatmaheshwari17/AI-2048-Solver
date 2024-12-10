
# AI-2048-Solver

**AI-2048-Solver** is an advanced Python-based AI agent designed to play the game 2048 optimally. The project features an implementation of the expectimax search algorithm along with sophisticated heuristics to make intelligent moves. The solver integrates with a graphical user interface (GUI) to provide real-time visualization of the AI's decisions and gameplay.


## Features

-   **Expectimax Search**: Implements a depth-limited search algorithm to simulate potential game states and select the best moves.
-   **Heuristic Evaluation**: Includes strategies such as:
    -   Maximizing empty cells for flexibility.
    -   Encouraging monotonicity (smooth increasing or decreasing rows/columns).
    -   Prioritizing high-value tiles in corners.
-   **Interactive GUI**: Displays the 2048 board in real-time, showing each move made by the AI.
-   **Configurable Depth**: Allows adjustment of the AI's search depth for a balance between speed and optimality.
-   **Automatic and Manual Modes**: Play the game manually or let the AI take control and play automatically.



## How It Works

The AI uses the **expectimax search algorithm**, a decision-making technique that evaluates possible future game states. At each state:

1.  The **AI’s turn** simulates moves (`up`, `down`, `left`, `right`) to maximize the score based on a heuristic evaluation.
2.  The **random tile spawn turn** simulates the placement of new tiles (`2` or `4`) by averaging possible outcomes.

The AI’s decisions are guided by a heuristic function that scores grid states based on:

-   **Empty Cells**: Encourages keeping the grid flexible with more empty spaces.
-   **Tile Monotonicity**: Prefers grids where rows/columns have smoothly increasing or decreasing values.
-   **High Tile Placement**: Rewards placing the largest tile in a corner.

----------

## Installation

### Prerequisites

-   Python 3.x
-   `tkinter` (pre-installed with most Python distributions)

### Steps

1.  Clone the repository:
    
    ```bash
    git clone git@github.com:rajatmaheshwari17/AI-2048-Solver.git
    cd AI-2048-Solver
    ```
    
2.  Run the game:
    
    ```bash
    python game.py
    ```
    

----------

## Usage

### Manual Play

-   Use the following keys to play:
    -   `W`, `A`, `S`, `D` or arrow keys for `Up`, `Left`, `Down`, `Right` moves.

### AI Auto-Play

-   Start the game in AI mode by modifying the `game.py` script:
    
    ```python
    if __name__ == '__main__':
        size = 4
        grid = Grid(size)
        panel = GamePanel(grid)
        game2048 = Game(grid, panel)
        game2048.start(auto_play=True)  # Enable AI auto-play
    
    ```
    
-   The AI will automatically take control and play the game.
    

----------

## Configuration

You can adjust the AI's behavior by modifying the following parameters:

-   **Search Depth**: Change the depth of the expectimax search in `AI.get_best_move(depth=3)`. A higher depth improves decision-making but slows performance.
-   **Heuristic Weights**: Modify the `evaluate_grid` method in the `AI` class to fine-tune how the AI evaluates grid states.


#
_This README is a part of the AI-2048-Solver Project by Rajat Maheshwari._

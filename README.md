# Professional Minesweeper Game 💣

A modern, professional implementation of the classic Minesweeper game with a beautiful GUI, optimized performance, and minimal memory usage.

## Features 🎮

### Core Game Mechanics
- **Classic Minesweeper gameplay** with left-click to reveal, right-click to flag
- **Smart first-click protection** - First click is always safe with a cleared area
- **Auto-reveal functionality** - Double-click to reveal adjacent cells when flags match mine count
- **Flood fill algorithm** - Automatically reveals empty regions
- **Three difficulty levels**:
  - Beginner: 9×9 grid with 10 mines
  - Intermediate: 16×16 grid with 40 mines
  - Expert: 16×30 grid with 99 mines

### Modern GUI Design 🎨
- **Beautiful dark theme** with carefully chosen color palette
- **Smooth hover effects** for better user feedback
- **Emoji-based indicators** for mines (💣), flags (🚩), and game states
- **Animated celebration** when you win
- **Real-time timer** and mine counter
- **Responsive controls** with instant visual feedback

### Technical Excellence 💻
- **Memory-optimized architecture** using sets and dictionaries instead of 2D arrays
- **Functional programming approach** with minimal loops and if-else statements
- **Type-safe implementation** using dataclasses and enums
- **O(1) lookups** for game state queries
- **Pre-calculated adjacent mine counts** for performance
- **Immutable position objects** for thread safety

## Installation

### Requirements
- Python 3.7 or higher
- tkinter (usually comes with Python)

### Quick Start
```bash
# Clone or download the game
git clone https://github.com/eminsk/minesweeper-game.git
cd minesweeper-game

# Run the game
python minesweeper.py
```

## How to Play 🎯

### Controls
- **Left Click**: Reveal a cell
- **Right Click**: Place/remove a flag
- **Double Click**: Auto-reveal adjacent cells (when flags match mine count)
- **Menu Bar**: Select difficulty level or start a new game
- **Smiley Button**: Quick restart

### Objective
Clear all cells without mines! Use the numbers to deduce where mines are located:
- Each number shows how many mines are in the 8 adjacent cells
- Use flags to mark suspected mine locations
- Win by revealing all non-mine cells

### Tips
1. Your first click is always safe - the game ensures no mines nearby
2. Use double-click to quickly reveal areas once you've flagged correctly
3. The mine counter shows remaining unflagged mines
4. Timer tracks your solving speed - try to beat your best time!

## Architecture Overview 🏗️

### Class Structure

```python
MinesweeperGame     # Core game logic
├── Position        # Immutable coordinate system
├── GameState       # Game state enumeration
└── CellState       # Cell state enumeration

MinesweeperGUI      # Modern GUI implementation
├── Board Display   # Dynamic cell grid
├── Header Panel    # Timer, counter, controls
└── Menu System     # Difficulty selection
```

### Key Design Patterns
- **Immutable Data**: Position objects are frozen dataclasses
- **Functional Approach**: Heavy use of map, filter, and comprehensions
- **Lazy Evaluation**: Cells created on-demand
- **Caching**: Pre-calculated adjacent mine counts
- **Event-Driven**: GUI responds to user interactions

## Performance Optimizations ⚡

1. **Memory Efficiency**
   - Uses sets instead of 2D arrays (O(1) lookups)
   - Lazy cell state initialization with defaultdict
   - Shared color constants

2. **Algorithm Optimization**
   - Iterative flood fill instead of recursive
   - Pre-cached adjacent mine counts
   - Set operations for neighbor calculations

3. **GUI Performance**
   - Batch updates using map operations
   - Efficient event binding with partial functions
   - Minimal widget recreation

## Code Quality 📊

### Professional Standards
- **Type Hints**: Full type annotations for better IDE support
- **Documentation**: Comprehensive docstrings
- **PEP 8 Compliant**: Following Python style guidelines
- **Error Handling**: Graceful handling of edge cases
- **Modular Design**: Clear separation of concerns

### Minimal Branching Philosophy
The code minimizes traditional if-else statements by using:
- Dictionary mapping for state transitions
- Set operations for logic
- Functional programming patterns
- Enum-based state management

## Future Enhancements 🚀

Potential improvements for future versions:
- [ ] High score tracking
- [ ] Custom board sizes
- [ ] Sound effects
- [ ] Multiplayer mode
- [ ] Mobile touch support
- [ ] Save/load game state
- [ ] Statistics tracking
- [ ] Daily challenges

## License 📄

MIT License - Feel free to use, modify, and distribute!

## Author 👨‍💻

Created with ❤️ by a Senior Python Developer focusing on clean, efficient, and beautiful code.

---

**Enjoy the game! May your clicks be swift and your mines be flagged! 💣🚩**
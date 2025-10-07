#!/usr/bin/env python3
"""
Professional Minesweeper Game
A modern, memory-efficient implementation with beautiful GUI
Author: Senior Python Developer
"""

import tkinter as tk
from tkinter import ttk, messagebox
import random
from functools import partial
from dataclasses import dataclass
from typing import Tuple, Set, Dict, Optional
from enum import Enum, auto
import time
from collections import defaultdict


class GameState(Enum):
    """Game state enumeration for cleaner state management."""
    READY = auto()
    PLAYING = auto()
    WON = auto()
    LOST = auto()


class CellState(Enum):
    """Cell state enumeration for type safety."""
    HIDDEN = auto()
    REVEALED = auto()
    FLAGGED = auto()
    QUESTIONED = auto()


@dataclass(frozen=True)
class Position:
    """Immutable position class for coordinate handling."""
    row: int
    col: int

    def neighbors(self, max_row: int, max_col: int) -> Set['Position']:
        """Generate valid neighbor positions using set comprehension."""
        return {
            Position(self.row + dr, self.col + dc)
            for dr in (-1, 0, 1) for dc in (-1, 0, 1)
            if (dr or dc) and 0 <= self.row + dr < max_row and 0 <= self.col + dc < max_col
        }


class MinesweeperGame:
    """Core game logic with optimized memory usage and minimal branching."""

    # Difficulty presets as class attributes for memory efficiency
    DIFFICULTY_PRESETS = {
        'Beginner': (9, 9, 10),
        'Intermediate': (16, 16, 40),
        'Expert': (16, 30, 99)
    }

    def __init__(self, rows: int = 9, cols: int = 9, mines: int = 10):
        """Initialize game with minimal memory allocation."""
        self.rows = rows
        self.cols = cols
        self.total_mines = mines
        self.state = GameState.READY
        self.start_time = 0
        self.elapsed_time = 0

        # Use sets for O(1) lookups instead of 2D arrays
        self.mines: Set[Position] = set()
        self.cell_states: Dict[Position, CellState] = defaultdict(lambda: CellState.HIDDEN)
        self.revealed: Set[Position] = set()
        self.flags: Set[Position] = set()

        # Cache for adjacent mine counts
        self.adjacent_cache: Dict[Position, int] = {}

    def reset(self):
        """Reset game state with minimal operations."""
        self.mines.clear()
        self.cell_states.clear()
        self.revealed.clear()
        self.flags.clear()
        self.adjacent_cache.clear()
        self.state = GameState.READY
        self.start_time = 0
        self.elapsed_time = 0

    def initialize_mines(self, first_click: Position):
        """Place mines ensuring first click is safe."""
        # Generate all possible positions except first click and its neighbors
        safe_zone = {first_click} | first_click.neighbors(self.rows, self.cols)
        available = {
            Position(r, c) for r in range(self.rows) for c in range(self.cols)
        } - safe_zone

        # Randomly select mine positions
        self.mines = set(random.sample(list(available),
                                      min(self.total_mines, len(available))))

        # Pre-calculate adjacent mine counts for all cells
        self._cache_adjacent_counts()

        self.state = GameState.PLAYING
        self.start_time = time.time()

    def _cache_adjacent_counts(self):
        """Pre-calculate adjacent mine counts for performance."""
        self.adjacent_cache = {
            Position(r, c): len(
                Position(r, c).neighbors(self.rows, self.cols) & self.mines
            )
            for r in range(self.rows) for c in range(self.cols)
        }

    def reveal_cell(self, pos: Position) -> bool:
        """Reveal a cell and propagate if necessary."""
        # Initialize mines on first click
        if self.state == GameState.READY:
            self.initialize_mines(pos)

        # Skip if game ended or cell already processed
        if self.state not in (GameState.PLAYING, GameState.READY) or \
           pos in self.revealed or pos in self.flags:
            return False

        # Check for mine
        if pos in self.mines:
            self.state = GameState.LOST
            self.elapsed_time = time.time() - self.start_time
            return False

        # Flood fill for empty cells using iterative approach
        to_reveal = {pos}
        while to_reveal:
            current = to_reveal.pop()
            if current in self.revealed:
                continue

            self.revealed.add(current)
            self.cell_states[current] = CellState.REVEALED

            # Auto-reveal neighbors if no adjacent mines
            if self.adjacent_cache.get(current, 0) == 0:
                to_reveal |= current.neighbors(self.rows, self.cols) - self.revealed - self.flags

        # Check win condition
        if len(self.revealed) + len(self.mines) == self.rows * self.cols:
            self.state = GameState.WON
            self.elapsed_time = time.time() - self.start_time
            self.flags = self.mines.copy()

        return True

    def toggle_flag(self, pos: Position):
        """Toggle flag state using XOR logic."""
        if pos in self.revealed or self.state != GameState.PLAYING:
            return

        # Toggle flag state
        self.flags ^= {pos}
        self.cell_states[pos] = CellState.FLAGGED if pos in self.flags else CellState.HIDDEN

    def auto_reveal_neighbors(self, pos: Position) -> bool:
        """Auto-reveal neighbors if flag count matches mine count."""
        if pos not in self.revealed or self.state != GameState.PLAYING:
            return False

        neighbors = pos.neighbors(self.rows, self.cols)
        flagged_neighbors = neighbors & self.flags
        hidden_neighbors = neighbors - self.revealed - self.flags

        # Check if number of flags equals adjacent mine count
        if len(flagged_neighbors) == self.adjacent_cache.get(pos, 0):
            # Reveal all non-flagged neighbors
            return all(self.reveal_cell(n) for n in hidden_neighbors)

        return False


class MinesweeperGUI:
    """Modern, beautiful GUI for Minesweeper game."""

    # Modern color scheme
    COLORS = {
        'bg': '#2b2d42',
        'panel': '#3d405b',
        'cell_hidden': '#585b7a',
        'cell_revealed': '#a8a9c4',
        'cell_hover': '#6c6f8f',
        'mine': '#d90429',
        'flag': '#06ffa5',
        'text': '#edf2f4',
        'numbers': ['', '#4895ef', '#4cc9f0', '#4361ee', '#3f37c9',
                   '#7209b7', '#b5179e', '#f72585', '#560bad']
    }

    CELL_SIZE = 32
    FONT_FAMILY = 'Segoe UI'

    def __init__(self):
        """Initialize the GUI with modern styling."""
        self.root = tk.Tk()
        self.root.title("Minesweeper Professional")
        self.root.configure(bg=self.COLORS['bg'])
        self.root.resizable(False, False)

        # Game instance
        self.game = MinesweeperGame()

        # UI state
        self.cells: Dict[Position, tk.Label] = {}
        self.timer_job: Optional[str] = None

        # Apply modern styling
        self._configure_styles()

        # Build UI components
        self._build_menu()
        self._build_header()
        self._build_game_board()

        # Start with beginner difficulty
        self.new_game('Beginner')

        # Center window
        self._center_window()

    def _configure_styles(self):
        """Configure ttk styles for modern look."""
        style = ttk.Style()
        style.theme_use('clam')

        # Configure button styles
        style.configure('Modern.TButton',
                       background=self.COLORS['panel'],
                       foreground=self.COLORS['text'],
                       borderwidth=0,
                       relief='flat',
                       padding=6)
        style.map('Modern.TButton',
                 background=[('active', self.COLORS['cell_hover'])])

    def _build_menu(self):
        """Build modern menu bar."""
        menubar = tk.Menu(self.root, bg=self.COLORS['panel'],
                         fg=self.COLORS['text'], relief='flat')
        self.root.config(menu=menubar)

        # Game menu
        game_menu = tk.Menu(menubar, tearoff=0, bg=self.COLORS['panel'],
                           fg=self.COLORS['text'])
        menubar.add_cascade(label="Game", menu=game_menu)

        # Add difficulty options using lambda instead of loops
        list(map(lambda d: game_menu.add_command(
            label=f"{d[0]} ({d[1][0]}×{d[1][1]}, {d[1][2]} mines)",
            command=partial(self.new_game, d[0])
        ), self.game.DIFFICULTY_PRESETS.items()))

        game_menu.add_separator()
        game_menu.add_command(label="Exit", command=self.root.quit)

    def _build_header(self):
        """Build header panel with game info."""
        self.header_frame = tk.Frame(self.root, bg=self.COLORS['panel'],
                                     height=60, relief='flat')
        self.header_frame.pack(fill='x', padx=2, pady=2)

        # Mine counter
        self.mine_label = tk.Label(
            self.header_frame,
            text="💣 010",
            font=(self.FONT_FAMILY, 20, 'bold'),
            bg=self.COLORS['panel'],
            fg=self.COLORS['flag']
        )
        self.mine_label.pack(side='left', padx=20, pady=10)

        # New game button
        self.new_game_btn = tk.Button(
            self.header_frame,
            text="😊",
            font=('Segoe UI Emoji', 24),
            bg=self.COLORS['cell_hidden'],
            fg=self.COLORS['text'],
            relief='flat',
            command=lambda: self.new_game()
        )
        self.new_game_btn.pack(side='left', expand=True)

        # Timer
        self.timer_label = tk.Label(
            self.header_frame,
            text="⏱ 000",
            font=(self.FONT_FAMILY, 20, 'bold'),
            bg=self.COLORS['panel'],
            fg=self.COLORS['flag']
        )
        self.timer_label.pack(side='right', padx=20, pady=10)

    def _build_game_board(self):
        """Build the game board with cells."""
        self.board_frame = tk.Frame(self.root, bg=self.COLORS['bg'])
        self.board_frame.pack(padx=10, pady=10)

    def _update_cell(self, pos: Position):
        """Update single cell appearance."""
        cell = self.cells[pos]

        # Determine cell content and styling using dictionary mapping
        count = self.game.adjacent_cache.get(pos, 0)

        display_map = {
            (True, False, False): ('🚩', self.COLORS['flag'], self.COLORS['cell_hidden']),
            (False, True, False): (
                str(count) if count else '',
                self.COLORS['numbers'][count] if count else self.COLORS['text'],
                self.COLORS['cell_revealed']
            ),
            (False, True, True): ('💣', self.COLORS['mine'], self.COLORS['mine']),
            (False, False, False): ('', self.COLORS['text'], self.COLORS['cell_hidden'])
        }

        key = (pos in self.game.flags, pos in self.game.revealed,
            pos in self.game.mines and self.game.state == GameState.LOST)
        text, fg, bg = display_map.get(key, ('', self.COLORS['text'], self.COLORS['cell_hidden']))

        cell.config(text=text, fg=fg, bg=bg,
                    relief='sunken' if pos in self.game.revealed else 'raised')



        # Bind events using partial functions
        cell.bind('<Button-1>', partial(self._on_left_click, pos))
        cell.bind('<Button-3>', partial(self._on_right_click, pos))
        cell.bind('<Double-Button-1>', partial(self._on_double_click, pos))
        cell.bind('<Enter>', partial(self._on_hover_enter, pos))
        cell.bind('<Leave>', partial(self._on_hover_leave, pos))

        cell.grid(row=pos.row, col=pos.col, padx=1, pady=1)
        return cell

    def _create_cell(self, pos: Position) -> tk.Label:
        """Create a single cell widget."""
        cell = tk.Label(
            self.board_frame,
            width=3,
            height=1,
            font=(self.FONT_FAMILY, 12, 'bold'),
            bg=self.COLORS['cell_hidden'],
            fg=self.COLORS['text'],
            relief='raised',
            bd=2
        )

        # Bind events using partial functions
        cell.bind('<Button-1>', partial(self._on_left_click, pos))
        cell.bind('<Button-3>', partial(self._on_right_click, pos))
        cell.bind('<Double-Button-1>', partial(self._on_double_click, pos))
        cell.bind('<Enter>', partial(self._on_hover_enter, pos))
        cell.bind('<Leave>', partial(self._on_hover_leave, pos))

        cell.grid(row=pos.row, column=pos.col, padx=1, pady=1)

        return cell


    def new_game(self, difficulty: str = None):
        """Start a new game with specified difficulty."""
        # Update game parameters if difficulty specified
        if difficulty:
            rows, cols, mines = self.game.DIFFICULTY_PRESETS[difficulty]
            self.game = MinesweeperGame(rows, cols, mines)
        else:
            self.game.reset()

        # Clear and rebuild board
        list(map(lambda w: w.destroy(), self.board_frame.winfo_children()))
        self.cells.clear()

        # Create cells using dictionary comprehension
        self.cells = {
            Position(r, c): self._create_cell(Position(r, c))
            for r in range(self.game.rows)
            for c in range(self.game.cols)
        }

        # Reset UI elements
        self._update_mine_counter()
        self._update_timer()
        self.new_game_btn.config(text="😊")

        # Stop timer if running
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None

    def _on_left_click(self, pos: Position, event):
        """Handle left click on cell."""
        if self.game.state == GameState.PLAYING or self.game.state == GameState.READY:
            if self.game.reveal_cell(pos):
                self._update_board()
                if self.game.state == GameState.PLAYING and not self.timer_job:
                    self._start_timer()
            else:
                self._game_over()

    def _on_right_click(self, pos: Position, event):
        """Handle right click for flagging."""
        self.game.toggle_flag(pos)
        self._update_cell(pos)
        self._update_mine_counter()

    def _on_double_click(self, pos: Position, event):
        """Handle double click for auto-reveal."""
        if self.game.auto_reveal_neighbors(pos):
            self._update_board()
        elif self.game.state == GameState.LOST:
            self._game_over()

    def _on_hover_enter(self, pos: Position, event):
        """Handle mouse enter for hover effect."""
        if pos not in self.game.revealed and pos not in self.game.flags:
            self.cells[pos].config(bg=self.COLORS['cell_hover'])

    def _on_hover_leave(self, pos: Position, event):
        """Handle mouse leave to remove hover effect."""
        if pos not in self.game.revealed and pos not in self.game.flags:
            self.cells[pos].config(bg=self.COLORS['cell_hidden'])

    def _update_cell(self, pos: Position):
        """Update single cell appearance."""
        cell = self.cells[pos]

        # Determine cell content and styling using dictionary mapping
        count = self.game.adjacent_cache.get(pos, 0)

        display_map = {
            (True, False, False): ('🚩', self.COLORS['flag'], self.COLORS['cell_hidden']),
            (False, True, False): (
                str(count) if count else '',
                self.COLORS['numbers'][count] if count else self.COLORS['text'],
                self.COLORS['cell_revealed']
            ),
            (False, True, True): ('💣', self.COLORS['mine'], self.COLORS['mine']),
            (False, False, False): ('', self.COLORS['text'], self.COLORS['cell_hidden'])
        }

        key = (pos in self.game.flags, pos in self.game.revealed,
            pos in self.game.mines and self.game.state == GameState.LOST)
        text, fg, bg = display_map.get(key, ('', self.COLORS['text'], self.COLORS['cell_hidden']))

        cell.config(text=text, fg=fg, bg=bg,
                    relief='sunken' if pos in self.game.revealed else 'raised')


    def _update_board(self):
        """Update entire board display."""
        # Use map for functional update
        list(map(self._update_cell, self.cells.keys()))

        # Check for win
        if self.game.state == GameState.WON:
            self._game_won()

    def _update_mine_counter(self):
        """Update mine counter display."""
        remaining = max(0, self.game.total_mines - len(self.game.flags))
        self.mine_label.config(text=f"💣 {remaining:03d}")

    def _update_timer(self):
        """Update timer display."""
        elapsed = int(self.game.elapsed_time if self.game.state in (GameState.WON, GameState.LOST)
                     else time.time() - self.game.start_time if self.game.start_time else 0)
        self.timer_label.config(text=f"⏱ {min(elapsed, 999):03d}")

    def _start_timer(self):
        """Start the game timer."""
        def tick():
            if self.game.state == GameState.PLAYING:
                self._update_timer()
                self.timer_job = self.root.after(1000, tick)
        tick()

    def _game_over(self):
        """Handle game over state."""
        self.game.state = GameState.LOST
        self.new_game_btn.config(text="😵")

        # Reveal all mines
        list(map(lambda m: self.cells[m].config(
            text='💣', bg=self.COLORS['mine'], relief='sunken'
        ), self.game.mines))

        # Show wrongly flagged cells
        wrong_flags = self.game.flags - self.game.mines
        list(map(lambda f: self.cells[f].config(
            text='❌', bg=self.COLORS['mine']
        ), wrong_flags))

        if self.timer_job:
            self.root.after_cancel(self.timer_job)

        messagebox.showinfo("Game Over", "💥 You hit a mine! Try again!")

    def _game_won(self):
        """Handle game won state."""
        self.new_game_btn.config(text="😎")

        if self.timer_job:
            self.root.after_cancel(self.timer_job)

        # Animated celebration
        self._celebrate()

        messagebox.showinfo("Congratulations!",
                          f"🎉 You won in {int(self.game.elapsed_time)} seconds!")

    def _celebrate(self):
        """Animate celebration effect."""
        colors = ['#4cc9f0', '#4895ef', '#4361ee', '#7209b7', '#b5179e']

        def flash(index=0):
            if index < 5:
                list(map(lambda c: c.config(bg=colors[index]),
                        [self.cells[p] for p in self.game.flags]))
                self.root.after(100, lambda: flash(index + 1))
            else:
                list(map(lambda p: self._update_cell(p), self.game.flags))

        flash()

    def _center_window(self):
        """Center the window on screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def run(self):
        """Start the GUI event loop."""
        self.root.mainloop()


def main():
    """Entry point for the application."""
    app = MinesweeperGUI()
    app.run()


if __name__ == "__main__":
    main()

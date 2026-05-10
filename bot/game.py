# bot/game.py
from time import time
from typing import List, Optional

class TicTacToe:
    def __init__(self, chat_id: int, message_id: int):
        self.chat_id = chat_id
        self.message_id = message_id
        self.board: List[str] = ["⬜"] * 9  # 3x3 grid flattened
        self.players: List[dict] = []       # List of {'id': int, 'username': str}
        self.turn_index = 0                 # 0 for Player 1 (X), 1 for Player 2 (O)
        self.is_active = True
        self.winner: Optional[str] = None
        self.winning_line: Optional[List[int]] = None
        self.start_time = time()
        self.last_move_time = time()
        self.join_phase = True
        
        # Win combinations (indices)
        self.win_combinations = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8], # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8], # Cols
            [0, 4, 8], [2, 4, 6]             # Diagonals
        ]

    def add_player(self, user_id: int, username: str):
        """Adds a player if slots are available."""
        if len(self.players) < 2 and not any(p['id'] == user_id for p in self.players):
            self.players.append({'id': user_id, 'username': username})
            return True
        return False

    def make_move(self, index: int, user_id: int) -> tuple[bool, str]:
        """Processes a move. Returns (success, message)."""
        if not self.is_active:
            return False, "Game is over."
        
        # Check if it's the player's turn
        current_player_id = self.players[self.turn_index]['id']
        if user_id != current_player_id:
            return False, "Not your turn!"
        
        # Check if cell is empty
        if self.board[index] != "⬜":
            return False, "Cell already taken!"

        # Place mark
        mark = "❌" if self.turn_index == 0 else "⭕"
        self.board[index] = mark
        self.last_move_time = time()
        
        # Check Win/Draw
        if self.check_win():
            self.is_active = False
            self.winner = self.players[self.turn_index]['username']
            return True, "WIN"
        
        if "⬜" not in self.board:
            self.is_active = False
            return True, "DRAW"

        # Switch turn
        self.turn_index = 1 - self.turn_index
        return True, "SUCCESS"

    def check_win(self):
        for combo in self.win_combinations:
            if (self.board[combo[0]] == self.board[combo[1]] == self.board[combo[2]] != "⬜"):
                self.winning_line = combo
                return True
        return False

    def get_board_text(self) -> str:
        """Generates the formatted text for the game message."""
        if self.join_phase:
            text = "🎮 **Tic Tac Toe Arena** 🎮\n\n"
            text += f"Players Joined: {len(self.players)}/2\n"
            for p in self.players:
                m = "❌" if len(self.players) == 1 and p == self.players[0] else ("⭕" if p == self.players[1] else "")
                text += f"@{p['username']} {m}\n"
            text += "\nClick **⚡ JOIN** to play!"
            return text

        text = ""
        if self.winner:
            text += f"🏆 **WINNER:** @{self.winner}\n"
            loser_mark = "⭕" if self.board[self.winning_line[0]] == "❌" else "❌"
            text += f"❌ defeated {loser_mark}\n\n"
        elif not self.is_active:
            text += "🤝 **Match Draw!**\n\n"
        else:
            p1 = self.players[0]
            p2 = self.players[1]
            turn_mark = "❌" if self.turn_index == 0 else "⭕"
            curr_user = p1['username'] if self.turn_index == 0 else p2['username']
            text += f"Player 1: @{p1['username']} ❌\n"
            text += f"Player 2: @{p2['username']} ⭕\n\n"
            text += f"{turn_mark} **Turn:** @{curr_user}\n"

        return text

    def get_keyboard(self):
        """Generates the inline keyboard markup."""
        from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

        if self.join_phase:
            # Show grid (disabled) and Join button
            buttons = []
            for i in range(0, 9, 3):
                row = []
                for j in range(3):
                    row.append(InlineKeyboardButton("⬜", callback_data=f"void_{i+j}"))
                buttons.append(row)
            
            # Join button logic
            btn_text = "⚡ JOIN GAME"
            if len(self.players) >= 2:
                btn_text = "⏳ Game Full"
                
            buttons.append([InlineKeyboardButton(btn_text, callback_data="join_game")])
            return InlineKeyboardMarkup(buttons)

        # Gameplay Phase
        buttons = []
        for i in range(0, 9, 3):
            row = []
            for j in range(3):
                idx = i + j
                cell_text = self.board[idx]
                
                # If game ended, disable buttons. Else use move callback.
                if not self.is_active:
                    # Highlight winning line
                    if self.winning_line and idx in self.winning_line:
                        cell_text = "🟩" + cell_text
                    cb_data = f"void_{idx}"
                else:
                    cb_data = f"move_{idx}"
                
                row.append(InlineKeyboardButton(cell_text, callback_data=cb_data))
            buttons.append(row)

        # Add Play Again button if game over
        if not self.is_active:
            buttons.append([InlineKeyboardButton("🔄 PLAY AGAIN", callback_data="restart_game")])

        return InlineKeyboardMarkup(buttons)

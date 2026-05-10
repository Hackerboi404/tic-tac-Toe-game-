# bot/main.py
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from game import TicTacToe
from config import Config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Dictionary to store active games: {chat_id: TicTacToeInstance}
active_games = {}

# Initialize Pyrogram Client
app = Client(
    "tic_tac_toe_bot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN
)

@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    """Handles the /start command in private chat."""
    await message.reply_text(
        "🎮 **Welcome to Tic Tac Toe Arena!**\n\n"
        "Features:\n"
        "⚡ Multiplayer Battle\n"
        "🎯 Inline Tap Gameplay\n"
        "🏆 Live Win Detection\n"
        "🔥 Fast & Smooth UI\n\n"
        "Add me to a group and use /startgame to play!",
        parse_mode="markdown"
    )

@app.on_message(filters.command("startgame") & filters.group)
async def start_game(client: Client, message: Message):
    """Initiates the game in a group."""
    chat_id = message.chat.id
    
    # Prevent multiple games in one chat
    if chat_id in active_games:
        await message.reply_text("⚠️ A game is already running in this group!")
        return

    # Send initial stylish message
    msg = await message.reply_text(
        "🎮 **TIC TAC TOE ARENA** 🎮\n"
        "Get ready for battle...\n"
        "Game starting in..."
    )

    # Countdown
    for i in range(3, 0, -1):
        await asyncio.sleep(1)
        try:
            await msg.edit_text(f"{i}️⃣")
        except Exception:
            pass # Ignore if message deleted during countdown

    # Create Game Instance
    game = TicTacToe(chat_id, msg.id)
    active_games[chat_id] = game

    # Send the Board
    await msg.edit_text(
        game.get_board_text(),
        reply_markup=game.get_keyboard()
    )

@app.on_callback_query()
async def handle_callback(client: Client, callback_query: CallbackQuery):
    """Handles inline button presses."""
    chat_id = callback_query.message.chat.id
    user_id = callback_query.from_user.id
    username = callback_query.from_user.username or callback_query.from_user.first_name

    # Check if game exists in this chat
    if chat_id not in active_games:
        await callback_query.answer("❌ No active game.", show_alert=True)
        return

    game = active_games[chat_id]
    data = callback_query.data

    # 1. JOIN GAME LOGIC
    if data == "join_game":
        if game.add_player(user_id, username):
            await callback_query.answer(f"✅ {username} joined!")
            if len(game.players) == 2:
                # Start game logic
                game.join_phase = False
                game.turn_index = 0 # Player 1 starts
        else:
            if len(game.players) >= 2:
                await callback_query.answer("⏳ Game is full!", show_alert=True)
            elif any(p['id'] == user_id for p in game.players):
                await callback_query.answer("⚠️ You already joined!", show_alert=True)
            else:
                await callback_query.answer("❌ Error joining.", show_alert=True)
        
        # Update message regardless of join status to show player count
        await callback_query.edit_message_text(
            text=game.get_board_text(),
            reply_markup=game.get_keyboard()
        )
        return

    # 2. RESTART LOGIC
    if data == "restart_game":
        # Reset game
        active_games[chat_id] = TicTacToe(chat_id, callback_query.message.id)
        new_game = active_games[chat_id]
        # Auto-join the players from the previous game
        for p in game.players:
            new_game.add_player(p['id'], p['username'])
        
        new_game.join_phase = False # Skip join phase if restarting
        await callback_query.answer("🔄 Game Restarted!")
        await callback_query.edit_message_text(
            text=new_game.get_board_text(),
            reply_markup=new_game.get_keyboard()
        )
        return

    # 3. GAMEPLAY LOGIC (MOVE)
    if data.startswith("move_"):
        if not game.is_active or game.join_phase:
            await callback_query.answer("⚠️ Game not active.", show_alert=True)
            return
        
        try:
            move_index = int(data.split("_")[1])
        except ValueError:
            return

        success, status = game.make_move(move_index, user_id)

        if not success:
            await callback_query.answer(status, show_alert=True)
            return
        
        # If valid move, update board
        await callback_query.answer()
        await callback_query.edit_message_text(
            text=game.get_board_text(),
            reply_markup=game.get_keyboard()
        )
        return

    # 4. INVALID/VOID CLICKS (clicking empty cells or disabled buttons)
    if data.startswith("void_"):
        await callback_query.answer("😶 Just watching?", show_alert=True)
        return

# Run the Flask app + Pyrogram
if __name__ == "__main__":
    # Check for webhook variables
    import os
    if "WEBHOOK_URL" in os.environ:
        # Webhook mode for Render
        print("Starting with Webhook...")
        app.run(
            webhook_url=os.environ.get("WEBHOOK_URL") + "/bot",
            certificate="cert.pem",
            max_retries=3,
            port=Config.PORT
        )
    else:
        # Polling mode (fallback or local)
        print("Starting with Polling...")
        app.run()

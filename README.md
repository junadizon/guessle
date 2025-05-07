# Guessle Bot

A Discord bot that brings the popular word-guessing game to your server! Players try to guess a 5-letter word within 6 attempts, receiving feedback after each guess.

## Features

- 🎮 Word-guessing game with 6 attempts
- 🎯 Real-time feedback using colored boxes
- 🔒 Private feedback for players
- 📊 Game statistics and history
- 🎨 Custom emoji support for feedback
- 🌐 Health check endpoints for monitoring

## Commands

- `/guessle` - Start a new game
- `/guess <word>` - Make a guess (5-letter word)
- `/status` - Check your current game status
- `/giveup` - End your current game
- `/help` - Show all available commands

## Game Rules

1. The bot randomly selects a 5-letter word
2. Players have 6 attempts to guess the word
3. After each guess, players receive feedback:
   - 🟩 Green box: Correct letter in correct position
   - 🟨 Yellow box: Correct letter in wrong position
   - ⬛ Gray box: Letter not in the word
4. Players can only have one active game at a time
5. The game ends when:
   - Player correctly guesses the word
   - Player uses all 6 attempts
   - Player gives up

## Privacy Features

- All guesses and feedback are private to the player
- Public messages only show colored boxes
- The word is only revealed to the player at the end of the game
- Game status is only visible to the player

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your Discord bot token:
   ```
   DISCORD_TOKEN=your_token_here
   PORT=8080  # Optional, defaults to 8080
   ```
4. Run the bot:
   ```bash
   python bot.py
   ```

## Dependencies

- discord.py
- python-dotenv
- aiohttp
- pyspellchecker

## Health Check Endpoints

The bot includes health check endpoints for monitoring:
- `GET /` - Basic health check
- `GET /health` - Detailed health check

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - see the LICENSE file for details.
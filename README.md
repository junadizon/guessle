# Guessle Discord Bot 🎯

A Wordle-inspired Discord bot that brings the popular word-guessing game to your server! Players try to guess a 5-letter word within 6 attempts, with color-coded feedback for each guess.

## Features 🚀

### Game Commands
- `/guessle` - Start a new game
- `/guess <word>` - Make a guess in your current game
- `/status` - Check your current game status
- `/giveup` - End your current game and reveal the word

### Leaderboards 📊
- `/leaderboard` - View the server's overall leaderboard
- `/monthly` - View the current month's leaderboard
- Tracks:
  - Words successfully guessed
  - Total games played
  - Win rate percentage

### Game Mechanics 🎮
- 6 attempts to guess a 5-letter word
- Color-coded feedback:
  - 🟩 Green: Correct letter in correct position
  - 🟨 Yellow: Correct letter in wrong position
  - ⬛ Gray: Letter not in the word
- Validates guesses against a dictionary
- Custom emoji support for feedback

## Setup 🛠️

1. Clone the repository:
```bash
git clone https://github.com/yourusername/guessle.git
cd guessle
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your Discord bot token:

```
DISCORD_TOKEN=your_bot_token_here
PORT=8080  # Optional: Change if needed
```

5. Run the bot:
```bash
python bot.py
```

## Requirements 📋
- Python 3.8 or higher
- discord.py >= 2.3.2
- python-dotenv >= 1.0.0
- aiohttp >= 3.9.1
- pyspellchecker >= 0.7.2

## Contributing 🤝
Contributions are welcome! Feel free to submit issues and pull requests.

## License 📄
This project is licensed under the MIT License - see the LICENSE file for details.

## Support 💬
If you encounter any issues or have questions, please open an issue in the repository.

---
Made with ❤️ by friedeggyolkie (Discord) / junadizon (GitHub)
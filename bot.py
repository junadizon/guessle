import random
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio
from aiohttp import web
import threading
from spellchecker import SpellChecker
import json
import datetime

# Load token from .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PORT = int(os.getenv("PORT", 8080))  # Get PORT from environment variable, default to 8080

# Intents and Bot Setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Required for role management

# Initialize spell checker
spell = SpellChecker()

# Emoji mapping
EMOJI_MAP = {}

async def load_emojis(guild):
    """Load emoji IDs from a JSON file or create it if it doesn't exist."""
    global EMOJI_MAP
    try:
        with open('emoji_map.json', 'r') as f:
            EMOJI_MAP = json.load(f)
    except FileNotFoundError:
        # Create emoji map if it doesn't exist
        EMOJI_MAP = {}
        for color in ['green', 'yellow', 'gray']:
            for letter in 'abcdefghijklmnopqrstuvwxyz':
                emoji_path = f'emojis/{color}/{color}_{letter}.png'
                if os.path.exists(emoji_path):
                    with open(emoji_path, 'rb') as f:
                        emoji = await guild.create_custom_emoji(
                            name=f'{color}_{letter}',
                            image=f.read()
                        )
                        EMOJI_MAP[f'{color}_{letter}'] = str(emoji)

        # Save the emoji map
        with open('emoji_map.json', 'w') as f:
            json.dump(EMOJI_MAP, f)

# Common 5-letter words for random selection
COMMON_WORDS = [
    "apple", "beach", "cloud", "dance", "earth", "flame", "ghost", "heart",
    "jelly", "knife", "light", "music", "night", "ocean", "piano", "queen",
    "river", "smile", "tiger", "unity", "voice", "water", "xenon", "yield",
    "zebra", "about", "above", "abuse", "actor", "acute", "admit", "adopt",
    "adult", "after", "again", "agent", "agree", "ahead", "alarm", "album",
    "alert", "alike", "alive", "allow", "alone", "along", "alter", "among",
    "anger", "angle", "angry", "apart", "apple", "apply", "arena", "argue",
    "arise", "array", "aside", "asset", "audio", "audit", "avoid", "award",
    "aware", "badly", "baker", "bases", "basic", "basis", "beach", "began",
    "begin", "begun", "being", "below", "bench", "billy", "birth", "black",
    "blame", "blind", "block", "blood", "board", "boost", "booth", "bound",
    "brain", "brand", "bread", "break", "breed", "brief", "bring", "broad",
    "broke", "brown", "build", "built", "buyer", "cable", "calif", "carry",
    "catch", "cause", "chain", "chair", "chart", "chase", "cheap", "check",
    "chest", "chief", "child", "china", "chose", "civil", "claim", "class",
    "clean", "clear", "click", "clock", "close", "coach", "coast", "could",
    "count", "court", "cover", "craft", "crash", "cream", "crime", "cross",
    "crowd", "crown", "curve", "cycle", "daily", "dance", "dated", "dealt",
    "death", "debut", "delay", "depth", "doing", "doubt", "dozen", "draft",
    "drama", "drawn", "dream", "dress", "drink", "drive", "drove", "dying",
    "eager", "early", "earth", "eight", "elite", "empty", "enemy", "enjoy",
    "enter", "entry", "equal", "error", "event", "every", "exact", "exist",
    "extra", "faith", "false", "fault", "fiber", "field", "fifth", "fifty",
    "fight", "final", "first", "fixed", "flash", "fleet", "floor", "fluid",
    "focus", "force", "forth", "forty", "forum", "found", "frame", "frank",
    "fraud", "fresh", "front", "fruit", "fully", "funny", "giant", "given",
    "glass", "globe", "going", "grace", "grade", "grand", "grant", "grass",
    "great", "green", "gross", "group", "grown", "guard", "guess", "guest",
    "guide", "happy", "harry", "heart", "heavy", "hence", "henry", "horse",
    "hotel", "house", "human", "ideal", "image", "index", "inner", "input",
    "issue", "japan", "jimmy", "joint", "jones", "judge", "known", "label",
    "large", "laser", "later", "laugh", "layer", "learn", "lease", "least",
    "leave", "legal", "level", "lewis", "light", "limit", "links", "lives",
    "local", "logic", "loose", "lower", "lucky", "lunch", "lying", "magic",
    "major", "maker", "march", "maria", "match", "maybe", "mayor", "meant",
    "media", "metal", "might", "minor", "minus", "mixed", "model", "money",
    "month", "moral", "motor", "mount", "mouse", "mouth", "movie", "music",
    "needs", "never", "newly", "night", "noise", "north", "noted", "novel",
    "nurse", "occur", "ocean", "offer", "order", "other", "ought", "paint",
    "panel", "paper", "party", "peace", "peter", "phase", "phone", "photo",
    "piece", "pilot", "pitch", "place", "plain", "plane", "plant", "plate",
    "point", "pound", "power", "press", "price", "pride", "prime", "print",
    "prior", "prize", "proof", "proud", "prove", "queen", "quick", "quiet",
    "quite", "radio", "raise", "range", "rapid", "ratio", "reach", "ready",
    "refer", "right", "rival", "river", "robin", "roger", "roman", "rough",
    "round", "route", "royal", "rural", "scale", "scene", "scope", "score",
    "sense", "serve", "seven", "shall", "shape", "share", "sharp", "sheet",
    "shelf", "shell", "shift", "shirt", "shock", "shoot", "short", "shown",
    "sight", "since", "sixth", "sixty", "sized", "skill", "sleep", "slide",
    "small", "smart", "smile", "smith", "smoke", "solid", "solve", "sorry",
    "sound", "south", "space", "spare", "speak", "speed", "spend", "spent",
    "split", "spoke", "sport", "staff", "stage", "stake", "stand", "start",
    "state", "steam", "steel", "stick", "still", "stock", "stone", "stood",
    "store", "storm", "story", "strip", "stuck", "study", "stuff", "style",
    "sugar", "suite", "super", "sweet", "table", "taken", "taste", "taxes",
    "teach", "teeth", "terry", "texas", "thank", "theft", "their", "theme",
    "there", "these", "thick", "thing", "think", "third", "those", "three",
    "threw", "throw", "tight", "times", "tired", "title", "today", "topic",
    "total", "touch", "tough", "tower", "track", "trade", "train", "treat",
    "trend", "trial", "tried", "tries", "truck", "truly", "trust", "truth",
    "twice", "under", "undue", "union", "unity", "until", "upper", "upset",
    "urban", "usage", "usual", "valid", "value", "video", "virus", "visit",
    "voice", "waste", "watch", "water", "wheel", "where", "which", "while",
    "white", "whole", "whose", "woman", "women", "world", "worse", "worst",
    "would", "wound", "write", "wrong", "wrote", "yield", "young", "youth"
]

# Dictionary to store user statistics
user_stats = {}

def load_user_stats():
    """Load user statistics from a JSON file."""
    try:
        with open('user_stats.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_user_stats():
    """Save user statistics to a JSON file."""
    with open('user_stats.json', 'w') as f:
        json.dump(user_stats, f)

# Load existing stats when bot starts
user_stats = load_user_stats()

class GuessleBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='/', intents=intents)
        self.web_app = web.Application()
        self.setup_web_routes()

    def setup_web_routes(self):
        """Set up web routes for health checks."""
        self.web_app.router.add_get('/', self.handle_health_check)
        self.web_app.router.add_get('/health', self.handle_health_check)

    async def handle_health_check(self, request):
        """Handle health check requests."""
        return web.Response(text="Bot is running!")

    async def setup_hook(self):
        # Start the web server
        runner = web.AppRunner(self.web_app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', PORT)
        await site.start()
        print(f"Web server started on port {PORT}")

        # Sync commands with Discord
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(f"Failed to sync commands: {e}")

        # Start the activity update loop
        self.bg_task = self.loop.create_task(self.update_activity())

    async def update_activity(self):
        await self.wait_until_ready()
        while not self.is_closed():
            # Update activity every 30 seconds
            await self.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.playing,
                    name="Guessle | /help"
                )
            )
            await asyncio.sleep(30)

    async def on_ready(self):
        print(f'✅ Logged in as {bot.user}')
        # Set initial activity
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.playing,
                name="Guessle | /help"
            )
        )

    async def on_guild_join(self, guild):
        """Load emojis when joining a new guild."""
        await load_emojis(guild)

bot = GuessleBot()

# Track active games for rich presence
active_games = set()

def get_random_word():
    """Generate a random 5-letter word."""
    return random.choice(COMMON_WORDS)

user_games = {}

def get_feedback(guess, correct, show_word=True):
    feedback = []
    correct_list = list(correct)

    # First pass: mark correct positions
    for i in range(5):
        if guess[i] == correct[i]:
            feedback.append("🟩")  # Green - correct position
            correct_list[i] = None  # Mark as used
        else:
            feedback.append(None)

    # Second pass: mark correct letters in wrong positions
    for i in range(5):
        if feedback[i] is None:  # If not already marked as correct
            if guess[i] in correct_list:
                feedback[i] = "🟨"  # Yellow - correct letter, wrong position
                correct_list[correct_list.index(guess[i])] = None  # Mark as used
            else:
                feedback[i] = "⬛"  # Gray - letter not in word

    result = " ".join(feedback)
    if show_word:
        result += f" - `{guess.upper()}`"
    return result

async def is_valid_word(word: str) -> bool:
    """Check if a word exists using pyspellchecker."""
    try:
        # Check if the word is in the spell checker's dictionary
        return len(spell.unknown([word.lower()])) == 0
    except Exception:
        return False

@bot.tree.command(name="guessle", description="Start a new Guessle game")
async def start_guessle(interaction: discord.Interaction):
    if interaction.user.id in user_games:
        await interaction.response.send_message("You already have an ongoing game! Use `/guess` to continue or `/giveup` to end it.")
        return

    word = get_random_word()
    user_games[interaction.user.id] = {
        "word": word,
        "attempts": 0,
        "guesses": []  # Store previous guesses and their feedback
    }
    active_games.add(interaction.user.id)

    # Update activity to show active game
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing,
            name=f"with {interaction.user.name}"
        )
    )

    await interaction.response.send_message(f"🎉 {interaction.user.name} has started Guessle! Guess a 5-letter word using `/guess`.")

@bot.tree.command(name="guess", description="Make a guess in your current game")
@app_commands.describe(word="Enter a 5-letter word")
async def guess_word(interaction: discord.Interaction, word: str):
    guessed_word = word.lower()

    if len(guessed_word) != 5:
        await interaction.response.send_message("❌ Invalid word. Make sure it's 5 letters.", ephemeral=True)
        return

    # Check if the word exists in the dictionary
    if not await is_valid_word(guessed_word):
        await interaction.response.send_message("❌ That's not a valid English word. Try another word!", ephemeral=True)
        return

    game = user_games.get(interaction.user.id)
    if not game:
        await interaction.response.send_message("You haven't started a game yet. Use `/guessle` to start one.", ephemeral=True)
        return

    game["attempts"] += 1
    feedback = get_feedback(guessed_word, game["word"], show_word=True)  # Show word in private feedback

    # Store the guess and feedback
    game["guesses"].append((guessed_word, feedback))

    # Send private feedback for this guess
    await interaction.response.send_message(
        f"Attempt {game['attempts']} of 6:\n{feedback}",
        ephemeral=True
    )

    if guessed_word == game["word"]:
        # Update user stats when they win
        user_id = str(interaction.user.id)
        if user_id not in user_stats:
            user_stats[user_id] = {'games': []}

        # Add game with timestamp and result
        user_stats[user_id]['games'].append({
            'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'won': True
        })
        save_user_stats()

        # Create public message with only colored boxes
        public_message = f"🎉 {interaction.user.name} has won Guessle!\n\n"
        for i, (guess, fb) in enumerate(game["guesses"], 1):
            public_message += f"{get_feedback(guess, game['word'], show_word=False)}\n"
        public_message += f"\nGuessed the word in {game['attempts']} attempts!"

        # Create private message with the word
        private_message = f"🎉 You won Guessle!\n\n"
        for i, (guess, fb) in enumerate(game["guesses"], 1):
            private_message += f"{fb}\n"
        private_message += f"\nThe word was `{game['word'].upper()}`"

        await interaction.followup.send(public_message)
        await interaction.followup.send(private_message, ephemeral=True)

        active_games.remove(interaction.user.id)
        del user_games[interaction.user.id]

        # Update activity if no more active games
        if not active_games:
            await bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.playing,
                    name="Guessle | /help"
                )
            )
    elif game["attempts"] >= 6:
        # Create public message with only colored boxes
        public_message = f"❌ {interaction.user.name} has lost Guessle!\n\n"
        for i, (guess, fb) in enumerate(game["guesses"], 1):
            public_message += f"{get_feedback(guess, game['word'], show_word=False)}\n"

        # Create private message with the word
        private_message = f"❌ You lost Guessle!\n\n"
        for i, (guess, fb) in enumerate(game["guesses"], 1):
            private_message += f"{fb}\n"
        private_message += f"\nThe word was `{game['word'].upper()}`"

        await interaction.followup.send(public_message)
        await interaction.followup.send(private_message, ephemeral=True)

        active_games.remove(interaction.user.id)
        del user_games[interaction.user.id]

        # Update activity if no more active games
        if not active_games:
            await bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.playing,
                    name="Guessle | /help"
                )
            )

@bot.tree.command(name="status", description="Check your current game status")
async def game_status(interaction: discord.Interaction):
    game = user_games.get(interaction.user.id)
    if not game:
        await interaction.response.send_message("You don't have an active game. Use `/guessle` to start one!", ephemeral=True)
        return

    # Show all previous attempts privately
    message = "Your current game status:\n\n"
    for i, (guess, fb) in enumerate(game["guesses"], 1):
        message += f"{fb}\n"
    message += f"\nYou're on attempt {game['attempts']} of 6."

    await interaction.response.send_message(message, ephemeral=True)

@bot.tree.command(name="giveup", description="End your current game and reveal the word")
async def give_up(interaction: discord.Interaction):
    if interaction.user.id not in user_games:
        await interaction.response.send_message("You don't have an active game to give up!", ephemeral=True)
        return

    game = user_games[interaction.user.id]
    # Update games played even when giving up
    user_id = str(interaction.user.id)
    if user_id not in user_stats:
        user_stats[user_id] = {'games': []}

    # Add game with timestamp and result
    user_stats[user_id]['games'].append({
        'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'won': False
    })
    save_user_stats()

    # Create public message with only colored boxes
    public_message = f"🏳️ {interaction.user.name} has given up on Guessle!\n\n"
    for i, (guess, fb) in enumerate(game["guesses"], 1):
        public_message += f"{get_feedback(guess, game['word'], show_word=False)}\n"

    # Create private message with the word
    private_message = f"🏳️ You gave up on Guessle!\n\n"
    for i, (guess, fb) in enumerate(game["guesses"], 1):
        private_message += f"{fb}\n"
    private_message += f"\nThe word was `{game['word'].upper()}`"

    await interaction.response.send_message(public_message)
    await interaction.followup.send(private_message, ephemeral=True)
    del user_games[interaction.user.id]

@bot.tree.command(name="help", description="Shows all available commands and how to use them")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎮 Guessle Bot Commands",
        description="Here are all the available commands:",
        color=discord.Color.blue()
    )

    commands_list = [
        ("/guessle", "Start a new Guessle game"),
        ("/guess <word>", "Make a guess in your current game"),
        ("/status", "Check your current game status"),
        ("/giveup", "End your current game and reveal the word"),
        ("/help", "Shows this help message")
    ]

    for cmd, desc in commands_list:
        embed.add_field(name=cmd, value=desc, inline=False)

    embed.set_footer(text="Type / to see all available commands")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="leaderboard", description="View the server's overall Guessle leaderboard")
async def leaderboard(interaction: discord.Interaction):
    if not user_stats:
        await interaction.response.send_message("No games have been played yet!")
        return

    # Calculate overall stats
    overall_stats = []
    for user_id, stats in user_stats.items():
        total_words = sum(1 for game in stats.get('games', []) if game.get('won', False))
        total_games = len(stats.get('games', []))

        if total_games > 0:
            overall_stats.append({
                'user_id': user_id,
                'words_guessed': total_words,
                'games_played': total_games,
                'win_rate': (total_words / total_games * 100) if total_games > 0 else 0
            })

    # Sort by words guessed
    overall_stats.sort(key=lambda x: x['words_guessed'], reverse=True)

    # Create leaderboard embed
    embed = discord.Embed(
        title="🏆 Overall Guessle Leaderboard",
        color=discord.Color.gold()
    )

    # Add top 10 users to the leaderboard
    for i, stats in enumerate(overall_stats[:10], 1):
        try:
            user = await bot.fetch_user(int(stats['user_id']))
            username = user.name
        except:
            username = "Unknown User"

        embed.add_field(
            name=f"{i}. {username}",
            value=f"Words Guessed: {stats['words_guessed']}\nGames Played: {stats['games_played']}\nWin Rate: {stats['win_rate']:.1f}%",
            inline=False
        )

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="monthly", description="View the server's monthly Guessle leaderboard")
async def monthly_leaderboard(interaction: discord.Interaction):
    if not user_stats:
        await interaction.response.send_message("No games have been played yet!")
        return

    # Get current month and year
    current_month = datetime.datetime.now().strftime("%Y-%m")

    # Filter and sort users by monthly stats
    monthly_stats = []
    for user_id, stats in user_stats.items():
        monthly_words = sum(1 for game in stats.get('games', [])
                          if game.get('timestamp', '').startswith(current_month)
                          and game.get('won', False))
        monthly_games = sum(1 for game in stats.get('games', [])
                          if game.get('timestamp', '').startswith(current_month))

        if monthly_games > 0:
            monthly_stats.append({
                'user_id': user_id,
                'words_guessed': monthly_words,
                'games_played': monthly_games,
                'win_rate': (monthly_words / monthly_games * 100) if monthly_games > 0 else 0
            })

    # Sort by words guessed
    monthly_stats.sort(key=lambda x: x['words_guessed'], reverse=True)

    # Create leaderboard embed
    embed = discord.Embed(
        title=f"🏆 Monthly Guessle Leaderboard ({current_month})",
        color=discord.Color.blue()
    )

    # Add top 10 users to the leaderboard
    for i, stats in enumerate(monthly_stats[:10], 1):
        try:
            user = await bot.fetch_user(int(stats['user_id']))
            username = user.name
        except:
            username = "Unknown User"

        embed.add_field(
            name=f"{i}. {username}",
            value=f"Words Guessed: {stats['words_guessed']}\nGames Played: {stats['games_played']}\nWin Rate: {stats['win_rate']:.1f}%",
            inline=False
        )

    await interaction.response.send_message(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Missing argument. Please provide all required arguments.")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Command not found. Available commands: `-guessle`, `-guess`, `-status`, `-giveup`")
    else:
        await ctx.send(f"❌ An error occurred: {str(error)}")

# Start bot
bot.run(TOKEN)
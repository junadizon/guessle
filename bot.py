import random
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio
from spellchecker import SpellChecker

# Load token from .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Intents and Bot Setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Required for role management

class GuessleBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='/', intents=intents)

    async def setup_hook(self):
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

bot = GuessleBot()

# Track active games for rich presence
active_games = set()

# Initialize spell checker
spell = SpellChecker()

# Common 5-letter words list for target words
COMMON_WORDS = [
    "apple", "beach", "cloud", "dance", "earth", "flame", "ghost", "heart",
    "jelly", "knife", "light", "music", "night", "ocean", "piano", "queen",
    "river", "smile", "tiger", "unity", "voice", "water", "xenon", "yield",
    "zebra", "actor", "baker", "candy", "drama", "eagle", "fairy", "grape",
    "house", "ivory", "jumbo", "karma", "lemon", "mango", "noble", "olive",
    "peach", "quilt", "radio", "snake", "table", "umbra", "vivid", "wagon",
    "xerox", "yacht", "zesty", "amber", "brave", "crown", "dream", "eager",
    "frost", "globe", "happy", "ivory", "jolly", "kiosk", "lunar", "magic",
    "noble", "oasis", "pride", "quick", "royal", "sunny", "tiger", "unity",
    "vivid", "witty", "xenon", "yield", "zesty"
]

def get_random_word():
    """Get a random 5-letter word from the common words list."""
    return random.choice(COMMON_WORDS)

user_games = {}

def get_feedback(guess, correct):
    feedback = []
    correct_list = list(correct)

    # First pass: mark correct positions
    for i in range(5):
        if guess[i] == correct[i]:
            feedback.append("🟩")
            correct_list[i] = None  # Mark as used
        else:
            feedback.append(None)

    # Second pass: mark correct letters in wrong positions
    for i in range(5):
        if feedback[i] is None:  # If not already marked as correct
            if guess[i] in correct_list:
                feedback[i] = "🟨"
                correct_list[correct_list.index(guess[i])] = None  # Mark as used
            else:
                feedback[i] = "⬛"

    return "".join(feedback)

async def is_valid_word(word: str) -> bool:
    """Check if a word is valid (5 letters and in dictionary)."""
    if len(word) != 5 or not word.isalpha():
        return False
    # Check if word is in dictionary or in our common words list
    return word.lower() in COMMON_WORDS or word.lower() not in spell.unknown([word.lower()])

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
        await interaction.response.send_message("❌ Invalid word. Make sure it's 5 letters.")
        return

    # Check if the word exists in the dictionary
    if not await is_valid_word(guessed_word):
        await interaction.response.send_message("❌ That's not a valid English word. Try another word!")
        return

    game = user_games.get(interaction.user.id)
    if not game:
        await interaction.response.send_message("You haven't started a game yet. Use `/guessle` to start one.")
        return

    game["attempts"] += 1
    feedback = get_feedback(guessed_word, game["word"])

    # Store the guess and feedback
    game["guesses"].append((guessed_word, feedback))

    # Create message with all attempts
    message = ""
    for i, (guess, fb) in enumerate(game["guesses"], 1):
        message += f"Attempt {i}: `{guess.upper()}` -> {fb}\n"
    message += f"\nYou're on attempt {game['attempts']} of 6."

    await interaction.response.send_message(message)

    if guessed_word == game["word"]:
        await interaction.followup.send(f"✅ Congrats! You guessed the word in {game['attempts']} attempts!")
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
        await interaction.followup.send(f"❌ Out of tries! The word was `{game['word'].upper()}`.")
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
        await interaction.response.send_message("You don't have an active game. Use `/guessle` to start one!")
        return

    # Show all previous attempts
    message = ""
    for i, (guess, fb) in enumerate(game["guesses"], 1):
        message += f"Attempt {i}: `{guess.upper()}` -> {fb}\n"
    message += f"\nYou're on attempt {game['attempts']} of 6."

    await interaction.response.send_message(message)

@bot.tree.command(name="giveup", description="End your current game and reveal the word")
async def give_up(interaction: discord.Interaction):
    if interaction.user.id not in user_games:
        await interaction.response.send_message("You don't have an active game to give up!")
        return

    word = user_games[interaction.user.id]["word"]
    del user_games[interaction.user.id]
    await interaction.response.send_message(f"Game ended. The word was `{word.upper()}`.")

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
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
import psycopg2
from psycopg2.extras import DictCursor
import pytz

# Load token from .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PORT = int(os.getenv("PORT", 8080))  # Get PORT from environment variable, default to 8080

# Set timezone to GMT+8
TIMEZONE = pytz.timezone('Asia/Singapore')

# Intents and Bot Setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Required for role management

# Initialize spell checker
spell = SpellChecker()

# Emoji mapping
EMOJI_MAP = {
    # Yellow emojis
    'yellow_a': '<:yellow_a:1369662416857858088>',
    'yellow_b': '<:yellow_b:1369662427796476078>',
    'yellow_c': '<:yellow_c:1369662439431471165>',
    'yellow_d': '<:yellow_d:1369662450458300557>',
    'yellow_e': '<:yellow_e:1369662461438988309>',
    'yellow_f': '<:yellow_f:1369662473069920367>',
    'yellow_g': '<:yellow_g:1369662483131793458>',
    'yellow_h': '<:yellow_h:1369662495719165962>',
    'yellow_i': '<:yellow_i:1369662505365803018>',
    'yellow_j': '<:yellow_j:1369662515314950244>',
    'yellow_k': '<:yellow_k:1369662525834268825>',
    'yellow_l': '<:yellow_l:1369662537712271490>',
    'yellow_m': '<:yellow_m:1369662556356087921>',
    'yellow_n': '<:yellow_n:1369662566166691851>',
    'yellow_o': '<:yellow_o:1369662576425697402>',
    'yellow_p': '<:yellow_p:1369662585594577037>',
    'yellow_q': '<:yellow_q:1369662595862102046>',
    'yellow_r': '<:yellow_r:1369662608000417832>',
    'yellow_s': '<:yellow_s:1369662618129928262>',
    'yellow_t': '<:yellow_t:1369662627135098990>',
    'yellow_u': '<:yellow_u:1369662637989826610>',
    'yellow_v': '<:yellow_v:1369662647859019796>',
    'yellow_w': '<:yellow_w:1369662659242491984>',
    'yellow_x': '<:yellow_x:1369662682667548672>',
    'yellow_y': '<:yellow_y:1369662697011937421>',
    'yellow_z': '<:yellow_z:1369662708252676186>',

    # Green emojis
    'green_a': '<:green_a:1369661679494762637>',
    'green_b': '<:green_b:1369661689363955833>',
    'green_c': '<:green_c:1369661700952948766>',
    'green_d': '<:green_d:1369661711719862343>',
    'green_e': '<:green_e:1369661721274220584>',
    'green_f': '<:green_f:1369661853478948915>',
    'green_g': '<:green_g:1369661862655955035>',
    'green_h': '<:green_h:1369661873452220456>',
    'green_i': '<:green_i:1369661882998329444>',
    'green_j': '<:green_j:1369661891625877605>',
    'green_k': '<:green_k:1369661901004472391>',
    'green_l': '<:green_l:1369661909967831101>',
    'green_m': '<:green_m:1369661918822010892>',
    'green_n': '<:green_n:1369661928703655946>',
    'green_o': '<:green_o:1369661938493292665>',
    'green_p': '<:green_p:1369661947380895844>',
    'green_q': '<:green_q:1369661959196246036>',
    'green_r': '<:green_r:1369661969669292163>',
    'green_s': '<:green_s:1369661979840614471>',
    'green_t': '<:green_t:1369661991358173215>',
    'green_u': '<:green_u:1369662036790739065>',
    'green_v': '<:green_v:1369662046844489758>',
    'green_w': '<:green_w:1369662056416018462>',
    'green_x': '<:green_x:1369662066767564932>',
    'green_y': '<:green_y:1369662076041298111>',
    'green_z': '<:green_z:1369662086283657236>',

    # Gray emojis
    'gray_a': '<:gray_a:1369661251235479552>',
    'gray_b': '<:gray_b:1369661303068692490>',
    'gray_c': '<:gray_c:1369661314355433594>',
    'gray_d': '<:gray_d:1369661337965301760>',
    'gray_e': '<:gray_e:1369661352221868236>',
    'gray_f': '<:gray_f:1369661377265795082>',
    'gray_g': '<:gray_g:1369661387940302949>',
    'gray_h': '<:gray_h:1369661400955486300>',
    'gray_i': '<:gray_i:1369661411734585364>',
    'gray_j': '<:gray_j:1369661422681722973>',
    'gray_k': '<:gray_k:1369661435780534343>',
    'gray_l': '<:gray_l:1369661446488592475>',
    'gray_m': '<:gray_m:1369661457217749082>',
    'gray_n': '<:gray_n:1369661467909029919>',
    'gray_o': '<:gray_o:1369661476834644009>',
    'gray_p': '<:gray_p:1369661485785284649>',
    'gray_q': '<:gray_q:1369661495528525905>',
    'gray_r': '<:gray_r:1369661506517729371>',
    'gray_s': '<:gray_s:1369661516076421240>',
    'gray_t': '<:gray_t:1369661526230827164>',
    'gray_u': '<:gray_u:1369661536171196466>',
    'gray_v': '<:gray_v:1369661545432350921>',
    'gray_w': '<:gray_w:1369661614873247775>',
    'gray_x': '<:gray_x:1369661622658011146>',
    'gray_y': '<:gray_y:1369661633667924068>',
    'gray_z': '<:gray_z:1369661643298177097>'
}

async def load_emojis(guild):
    """Load emoji IDs from a JSON file or create it if it doesn't exist."""
    global EMOJI_MAP
    print(f"Loading emojis for guild: {guild.name}")
    try:
        with open('emoji_map.json', 'r') as f:
            EMOJI_MAP = json.load(f)
            print(f"Loaded {len(EMOJI_MAP)} emojis from file")
    except FileNotFoundError:
        print("Emoji map not found, creating new one...")
        # Create emoji map if it doesn't exist
        EMOJI_MAP = {}
        for color in ['green', 'yellow', 'gray']:
            for letter in 'abcdefghijklmnopqrstuvwxyz':
                emoji_path = f'emojis/{color}/{color}_{letter}.png'
                if os.path.exists(emoji_path):
                    print(f"Creating emoji for {emoji_path}")
                    with open(emoji_path, 'rb') as f:
                        emoji = await guild.create_custom_emoji(
                            name=f'{color}_{letter}',
                            image=f.read()
                        )
                        EMOJI_MAP[f'{color}_{letter}'] = str(emoji)
                        print(f"Created emoji: {emoji}")

        # Save the emoji map
        print("Saving emoji map...")
        with open('emoji_map.json', 'w') as f:
            json.dump(EMOJI_MAP, f)
        print("Emoji map saved!")

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

class UserStats:
    def __init__(self):
        print("Initializing UserStats...")
        self.conn = None
        self.get_db_connection()
        self.create_tables()

    def get_db_connection(self):
        """Get database connection from Neon."""
        try:
            database_url = os.getenv('DATABASE_URL')
            if not database_url:
                print("DATABASE_URL not found in environment variables!")
                raise ValueError("DATABASE_URL environment variable not set")

            print("Attempting to connect to database...")
            if self.conn is not None:
                try:
                    self.conn.close()
                except:
                    pass
            self.conn = psycopg2.connect(database_url)
            print("Successfully connected to database!")
            return self.conn
        except Exception as e:
            print(f"Error connecting to database: {e}")
            return None

    def ensure_connection(self):
        """Ensure database connection is active."""
        try:
            if self.conn is None or self.conn.closed:
                self.get_db_connection()
            return self.conn is not None
        except Exception as e:
            print(f"Error ensuring connection: {e}")
            return False

    def create_tables(self):
        """Create necessary tables if they don't exist."""
        try:
            if not self.ensure_connection():
                return

            print("Creating tables if they don't exist...")
            with self.conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS games (
                        id SERIAL PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                        won BOOLEAN NOT NULL
                    )
                """)
            self.conn.commit()
            print("Tables created successfully!")
        except Exception as e:
            print(f"Error creating tables: {e}")

    def add_game(self, user_id: str, won: bool):
        """Add a game result to the database."""
        try:
            if not self.ensure_connection():
                return

            print(f"Adding game for user {user_id}, won: {won}")
            # Get current time in GMT+8
            current_time = datetime.datetime.now(TIMEZONE)

            with self.conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO games (user_id, timestamp, won) VALUES (%s, %s, %s)",
                    (user_id, current_time, won)
                )
            self.conn.commit()
            print("Game added successfully!")
        except Exception as e:
            print(f"Error adding game: {e}")

    def get_monthly_stats(self):
        """Get stats for the current month in GMT+8."""
        try:
            if not self.ensure_connection():
                return []

            # Get current time in GMT+8
            current_time = datetime.datetime.now(TIMEZONE)
            current_month = current_time.strftime("%Y-%m")

            with self.conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("""
                    SELECT
                        user_id,
                        COUNT(*) as games_played,
                        SUM(CASE WHEN won THEN 1 ELSE 0 END) as words_guessed
                    FROM games
                    WHERE to_char(timestamp AT TIME ZONE 'Asia/Singapore', 'YYYY-MM') = %s
                    GROUP BY user_id
                    HAVING COUNT(*) > 0
                    ORDER BY words_guessed DESC
                """, (current_month,))
                return [dict(row) for row in cur.fetchall()]
        except Exception as e:
            print(f"Error getting monthly stats: {e}")
            return []

    def get_overall_stats(self):
        """Get overall stats for all users."""
        try:
            if not self.ensure_connection():
                return []

            with self.conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("""
                    SELECT
                        user_id,
                        COUNT(*) as games_played,
                        SUM(CASE WHEN won THEN 1 ELSE 0 END) as words_guessed
                    FROM games
                    GROUP BY user_id
                    HAVING COUNT(*) > 0
                    ORDER BY words_guessed DESC
                """)
                return [dict(row) for row in cur.fetchall()]
        except Exception as e:
            print(f"Error getting overall stats: {e}")
            return []

    def __del__(self):
        """Close database connection when object is destroyed."""
        if hasattr(self, 'conn') and self.conn:
            try:
                self.conn.close()
            except:
                pass

# Create a global instance of UserStats
user_stats = UserStats()

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

        # Load emojis when the bot is ready
        await self.load_emojis()

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

    async def load_emojis(self):
        """Load emojis when the bot is ready."""
        print("Loading emojis...")
        for guild in self.guilds:
            await load_emojis(guild)
        print("Emojis loaded!")

bot = GuessleBot()

# Track active games for rich presence
active_games = set()

def get_random_word():
    """Generate a random 5-letter word."""
    return random.choice(COMMON_WORDS)

user_games = {}

def get_feedback(guess, correct, show_word=True, use_custom_emojis=False):
    feedback = []
    correct_list = list(correct)

    # First pass: mark correct positions
    for i in range(5):
        if guess[i] == correct[i]:
            if use_custom_emojis:
                emoji_key = f"green_{guess[i]}"
                feedback.append(EMOJI_MAP.get(emoji_key, "🟩"))
            else:
                feedback.append("🟩")
            correct_list[i] = None
        else:
            feedback.append(None)

    # Second pass: mark correct letters in wrong positions
    for i in range(5):
        if feedback[i] is None:
            if guess[i] in correct_list:
                if use_custom_emojis:
                    emoji_key = f"yellow_{guess[i]}"
                    feedback[i] = EMOJI_MAP.get(emoji_key, "🟨")
                else:
                    feedback[i] = "🟨"
                correct_list[correct_list.index(guess[i])] = None
            else:
                if use_custom_emojis:
                    emoji_key = f"gray_{guess[i]}"
                    feedback[i] = EMOJI_MAP.get(emoji_key, "⬛")
                else:
                    feedback[i] = "⬛"

    # Join with spaces
    return " ".join(feedback)

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
    game["guesses"].append(guessed_word)

    # Send private feedback with custom emojis and previous guesses
    private_message = f"Attempt {game['attempts']} of 6:\n"
    # Show all previous guesses with custom emojis
    for guess in game["guesses"]:
        private_message += f"{get_feedback(guess, game['word'], show_word=True, use_custom_emojis=True)}\n"

    await interaction.response.send_message(private_message, ephemeral=True)

    if guessed_word == game["word"]:
        print(f"User {interaction.user.id} won the game!")
        # Update database when user wins
        user_stats.add_game(str(interaction.user.id), True)

        # Create public message with only colored boxes
        public_message = f"🎉 {interaction.user.name} has won Guessle!\n\n"
        for guess in game["guesses"]:
            public_message += f"{get_feedback(guess, game['word'], show_word=False)}\n"
        public_message += f"\nGuessed the word in {game['attempts']} attempts!"

        # Create private message with custom emojis
        private_message = f"🎉 You won Guessle!\n\n"
        for guess in game["guesses"]:
            private_message += f"{get_feedback(guess, game['word'], show_word=True, use_custom_emojis=True)}\n"
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
        # Update database when user loses
        print(f"User {interaction.user.id} lost the game!")
        user_stats.add_game(str(interaction.user.id), False)

        # Create public message with only colored boxes
        public_message = f"❌ {interaction.user.name} has lost Guessle!\n\n"
        for guess in game["guesses"]:
            public_message += f"{get_feedback(guess, game['word'], show_word=False)}\n"

        # Create private message with custom emojis
        private_message = f"❌ You lost Guessle!\n\n"
        for guess in game["guesses"]:
            private_message += f"{get_feedback(guess, game['word'], show_word=True, use_custom_emojis=True)}\n"
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
    for guess in game["guesses"]:
        message += f"{get_feedback(guess, game['word'], show_word=False, use_custom_emojis=True)}\n"
    message += f"\nYou're on attempt {game['attempts']} of 6."

    await interaction.response.send_message(message, ephemeral=True)

@bot.tree.command(name="giveup", description="End your current game and reveal the word")
async def give_up(interaction: discord.Interaction):
    if interaction.user.id not in user_games:
        await interaction.response.send_message("You don't have an active game!")
        return

    game = user_games[interaction.user.id]
    correct = game["word"]

    # Update database when user gives up
    print(f"User {interaction.user.id} gave up the game")
    user_stats.add_game(str(interaction.user.id), False)

    # Create public message with only colored boxes
    public_message = f"❌ {interaction.user.name} has given up Guessle!\n\n"
    for i, (guess, fb) in enumerate(game["guesses"], 1):
        public_message += f"{get_feedback(guess, game['word'], show_word=False)}\n"

    # Create private message with the word
    private_message = f"❌ You gave up Guessle!\n\n"
    for i, (guess, fb) in enumerate(game["guesses"], 1):
        private_message += f"{fb}\n"
    private_message += f"\nThe word was `{game['word'].upper()}`"

    await interaction.response.send_message(public_message)
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
    try:
        # Defer the response since this might take a while
        await interaction.response.defer()

        overall_stats = user_stats.get_overall_stats()

        if not overall_stats:
            await interaction.followup.send("No games have been played yet!")
            return

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

            win_rate = (stats['words_guessed'] / stats['games_played'] * 100) if stats['games_played'] > 0 else 0

            embed.add_field(
                name=f"{i}. {username}",
                value=f"Words Guessed: {stats['words_guessed']}\nGames Played: {stats['games_played']}\nWin Rate: {win_rate:.1f}%",
                inline=False
            )

        await interaction.followup.send(embed=embed)
    except Exception as e:
        print(f"Error in leaderboard command: {e}")
        await interaction.followup.send("❌ An error occurred while fetching the leaderboard. Please try again later.", ephemeral=True)

@bot.tree.command(name="monthly", description="View the server's monthly Guessle leaderboard")
async def monthly_leaderboard(interaction: discord.Interaction):
    try:
        # Defer the response since this might take a while
        await interaction.response.defer()

        monthly_stats = user_stats.get_monthly_stats()

        if not monthly_stats:
            await interaction.followup.send("No games have been played this month!")
            return

        # Get current time in GMT+8
        current_time = datetime.datetime.now(TIMEZONE)

        # Create leaderboard embed
        embed = discord.Embed(
            title=f"🏆 Monthly Guessle Leaderboard ({current_time.strftime('%Y-%m')})",
            color=discord.Color.blue()
        )

        # Add top 10 users to the leaderboard
        for i, stats in enumerate(monthly_stats[:10], 1):
            try:
                user = await bot.fetch_user(int(stats['user_id']))
                username = user.name
            except:
                username = "Unknown User"

            win_rate = (stats['words_guessed'] / stats['games_played'] * 100) if stats['games_played'] > 0 else 0

            embed.add_field(
                name=f"{i}. {username}",
                value=f"Words Guessed: {stats['words_guessed']}\nGames Played: {stats['games_played']}\nWin Rate: {win_rate:.1f}%",
                inline=False
            )

        await interaction.followup.send(embed=embed)
    except Exception as e:
        print(f"Error in monthly leaderboard command: {e}")
        await interaction.followup.send("❌ An error occurred while fetching the monthly leaderboard. Please try again later.", ephemeral=True)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Missing argument. Please provide all required arguments.")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Command not found. Available commands: `/guessle`, `/guess`, `/status`, `/giveup`, `/help`, `/leaderboard`, `/monthly`")
    else:
        await ctx.send(f"❌ An error occurred: {str(error)}")

# Start bot
bot.run(TOKEN)
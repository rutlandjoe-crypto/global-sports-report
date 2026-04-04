import os
from pathlib import Path

import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH, override=True)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "").strip()
DISCORD_GUILD_ID = os.getenv("DISCORD_GUILD_ID", "").strip()

if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN is missing from .env")

REPORT_FILES = {
    "mlb": BASE_DIR / "mlb_report.txt",
    "nba": BASE_DIR / "nba_report.txt",
    "nhl": BASE_DIR / "nhl_report.txt",
    "soccer": BASE_DIR / "soccer_report.txt",
    "fantasy": BASE_DIR / "fantasy_report.txt",
    "betting": BASE_DIR / "betting_odds_report.txt",
    "global": BASE_DIR / "global_sports_report.txt",
}

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree


def read_report(path: Path) -> str:
    if not path.exists():
        return f"❌ Report file not found: {path.name}"
    text = path.read_text(encoding="utf-8", errors="ignore").strip()
    if not text:
        return f"❌ Report file is empty: {path.name}"
    return text


def split_text(text: str, max_len: int = 1900) -> list[str]:
    chunks = []
    while len(text) > max_len:
        cut = text.rfind("\n", 0, max_len)
        if cut == -1:
            cut = max_len
        chunks.append(text[:cut].strip())
        text = text[cut:].strip()
    if text:
        chunks.append(text)
    return chunks


async def send_report(interaction: discord.Interaction, report_key: str, label: str):
    await interaction.response.defer(thinking=True)

    report_path = REPORT_FILES[report_key]
    report_text = read_report(report_path)
    chunks = split_text(report_text)

    if not chunks:
        await interaction.followup.send(f"❌ No content available for {label}.")
        return

    await interaction.followup.send(chunks[0])

    for chunk in chunks[1:]:
        await interaction.channel.send(chunk)


@tree.command(name="ping", description="Check if the bot is online")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong! Bot is online.")


@tree.command(name="help", description="Show available commands")
async def help_command(interaction: discord.Interaction):
    await interaction.response.send_message(
        "/ping\n"
        "/help\n"
        "/mlb\n"
        "/nba\n"
        "/nhl\n"
        "/soccer\n"
        "/fantasy\n"
        "/betting\n"
        "/global"
    )


@tree.command(name="mlb", description="Show the latest MLB report")
async def mlb(interaction: discord.Interaction):
    await send_report(interaction, "mlb", "MLB")


@tree.command(name="nba", description="Show the latest NBA report")
async def nba(interaction: discord.Interaction):
    await send_report(interaction, "nba", "NBA")


@tree.command(name="nhl", description="Show the latest NHL report")
async def nhl(interaction: discord.Interaction):
    await send_report(interaction, "nhl", "NHL")


@tree.command(name="soccer", description="Show the latest soccer report")
async def soccer(interaction: discord.Interaction):
    await send_report(interaction, "soccer", "Soccer")


@tree.command(name="fantasy", description="Show the latest fantasy report")
async def fantasy(interaction: discord.Interaction):
    await send_report(interaction, "fantasy", "Fantasy")


@tree.command(name="betting", description="Show the latest betting odds report")
async def betting(interaction: discord.Interaction):
    await send_report(interaction, "betting", "Betting")


@tree.command(name="global", description="Show the latest global sports report")
async def global_report(interaction: discord.Interaction):
    await send_report(interaction, "global", "Global Sports")


@bot.event
async def on_ready():
    print("=" * 60)
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    print(f"📁 Base directory: {BASE_DIR}")

    try:
        if DISCORD_GUILD_ID:
            guild = discord.Object(id=int(DISCORD_GUILD_ID))
            synced = await tree.sync(guild=guild)
            print(f"✅ Synced {len(synced)} guild slash command(s)")
        else:
            synced = await tree.sync()
            print(f"✅ Synced {len(synced)} global slash command(s)")
    except Exception as e:
        print(f"❌ Slash command sync failed: {e}")

    print("=" * 60)


bot.run(DISCORD_TOKEN)
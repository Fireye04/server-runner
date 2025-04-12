import discord
from discord.ext import commands
import json
import subprocess

intents = discord.Intents.all()

bot = commands.Bot(command_prefix="$", intents=intents)


def _getsecret():
    with open("secret.json", "r") as sec:
        data = json.load(sec)
    return data


def _setsecret(target: dict):
    with open("secret.json", "w") as sec:
        json.dump(target, sec)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print("------")


@bot.command()
async def run(ctx: commands.Context, *args: tuple):
    data = _getsecret()

    if ctx.author.id not in data["sudolist"]:
        return

    game = "".join(args[0])
    runner = "".join(args[1])
    if game not in data["games"]:
        return
    if runner not in data["games"][game]["runners"]:
        return

    print(
        subprocess.run(
            data["games"][game]["runners"][runner],
            cwd=data["games"][game]["dir"],
        )
    )


if __name__ == "__main__":
    data = _getsecret()
    bot.run(data["token"])

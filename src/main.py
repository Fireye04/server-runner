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
async def status(ctx: commands.Context):
    data = _getsecret()
    total = ""
    for key, process in data["processes"].items():
        status = process.poll()
        total += f"{key} - STATUS: {'Running!' if status is None else f'Dead! (Code: {status})'} \n"
        if status is not None:
            data["processes"].pop(key, None)
            _setsecret(data)
    await ctx.send(total)


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
    if getKey(game, runner) in data["processes"]:
        await ctx.send("Process already running")
        return

    process = subprocess.Popen(
        data["games"][game]["runners"][runner],
        cwd=data["games"][game]["dir"],
    )
    data["processes"][getKey(game, runner)] = process
    _setsecret(data)


def getKey(game: str, runner: str) -> str:
    return f"{game} | {runner}"


if __name__ == "__main__":
    data = _getsecret()
    bot.run(data["token"])

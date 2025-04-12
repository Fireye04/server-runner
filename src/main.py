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


def getKey(game: str, runner: str) -> str:
    return f"{game} | {runner}"


def sync() -> None:
    data = _getsecret()
    for key, process in data["processes"].items():
        status = process.poll()
        if status is not None:
            data["processes"].pop(key, None)
    _setsecret(data)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print("------")
    sync()


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
    sync()
    data = _getsecret()
    if ctx.author.id not in data["sudolist"]:
        await ctx.send("Insufficient permissions! (You're not cool like that)")
        return

    game = "".join(args[0])
    runner = "".join(args[1])
    key = getKey(game, runner)
    if game not in data["games"]:
        await ctx.send("Game not found")
        return
    if runner not in data["games"][game]["runners"]:
        await ctx.send("Runner not found")
        return
    if key in data["processes"]:
        await ctx.send("Process already running")
        return

    process = subprocess.Popen(
        data["games"][game]["runners"][runner],
        cwd=data["games"][game]["dir"],
    )
    data["processes"][key] = process
    _setsecret(data)


@bot.command()
async def kill(ctx: commands.Context, *args: tuple):
    sync()
    data = _getsecret()
    if ctx.author.id not in data["sudolist"]:
        await ctx.send("Insufficient permissions! (You're not cool like that)")
        return

    game = "".join(args[0])
    runner = "".join(args[1])
    key = getKey(game, runner)
    if game not in data["games"]:
        await ctx.send("Game not found")
        return
    if runner not in data["games"][game]["runners"]:
        await ctx.send("Runner not found")
        return
    if key not in data["processes"]:
        await ctx.send("Process not running")
        return

    target = data["processes"][key]

    target.terminate()
    try:
        exit = target.wait(5)
    except subprocess.TimeoutExpired:
        target.kill()
        exit = target.wait(5)
    if exit is None:
        await ctx.send("Process has achieved godhood and/or sentience. Good luck.")
        return
    data["processes"].pop(key, None)
    _setsecret(data)


if __name__ == "__main__":
    data = _getsecret()
    bot.run(data["token"])

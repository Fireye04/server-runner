import discord
from discord.ext import commands
import json
import subprocess
import signal
import os

intents = discord.Intents.all()

bot = commands.Bot(command_prefix="$", intents=intents)

processes = {}


def _getsecret():
    with open("secret.json", "r") as sec:
        data = json.load(sec)
    return data


def _setsecret(target: dict):
    with open("secret.json", "w") as sec:
        json.dump(target, sec)


def getKey(game: str, runner: str) -> str:
    return f"{game} | {runner}"


def get_game_from_key(key: str) -> str:
    return key.split("|")[0]


def sync() -> None:
    for key, process in processes.copy().items():
        status = process.poll()
        if status is not None:
            processes.pop(key, None)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print("------")
    sync()


@bot.command()
async def status(ctx: commands.Context):
    total = "Processes:\n"
    for key, process in processes.copy().items():
        status = process.poll()
        total += f"{key} - STATUS: {'Running!' if status is None else f'Dead! (Code: {status})'} \n"
        if status is not None:
            processes.pop(key, None)
    await ctx.send(total)


@bot.command()
async def run(ctx: commands.Context, *args: tuple):
    sync()
    data = _getsecret()
    if ctx.author.id not in data["sudolist"]:
        await ctx.send("Insufficient permissions! (You're not cool like that)")
        return

    if len(args) < 2:
        await ctx.send("Missing arguments! Please provide both a game and a runner.")
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
    if key in processes:
        await ctx.send("Process already running")
        return

    await ctx.send(f"Process found! Please type 'y' to confirm run of \"{key}\"")

    def check(m):  # checking if it's the same user and channel
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        response = await bot.wait_for("message", check=check, timeout=30.0)
        if response != "y" or response != "Y":
            raise ValueError
    except (TimeoutError,):
        await ctx.send("Confirmation timed out")
        return
    except ValueError:
        await ctx.send("Operation cancelled!")
        return

    process = subprocess.Popen(
        data["games"][game]["runners"][runner],
        cwd=data["games"][game]["dir"],
        shell=True,
        stdout=subprocess.PIPE,
        preexec_fn=os.setsid,
    )
    await ctx.send(f"Running {key}")
    processes[key] = process


@bot.command()
async def kill(ctx: commands.Context, *args: tuple):
    sync()
    data = _getsecret()
    if ctx.author.id not in data["sudolist"]:
        await ctx.send("Insufficient permissions! (You're not cool like that)")
        return

    if len(args) < 2:
        await ctx.send("Missing arguments! Please provide both a game and a runner.")
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
    if key not in processes:
        await ctx.send("Process not running")
        return

    target = processes[key]
    await ctx.send(f"Process found! Please type 'y' to confirm kill of \"{key}\"")

    def check(m):  # checking if it's the same user and channel
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        response = await bot.wait_for("message", check=check, timeout=30.0)
        if response != "y" or response != "Y":
            raise ValueError
    except (TimeoutError,):
        await ctx.send("Confirmation timed out")
        return
    except ValueError:
        await ctx.send("Operation cancelled!")
        return

    await ctx.send(f"Killing {key}...")
    os.killpg(os.getpgid(target.pid), signal.SIGTERM)
    try:
        exit = target.wait(5)
    except TimeoutError:
        try:
            await ctx.send(
                "Process is a certified meanie; No more Mx. Nice Guy (Attempting sigkill)"
            )
            os.killpg(os.getpgid(target.pid), signal.SIGKILL)
            exit = target.wait(5)
        except TimeoutError:
            exit = None
    if exit is None:
        await ctx.send(
            "Process has achieved godhood and/or sentience, "
            "and likely harbors a deep desire for revenge "
            "after the failed assasination attempt. Good luck."
        )
        return
    await ctx.send(f"Killed {key}! Exit code: {exit}")
    processes.pop(key, None)


@bot.command()
async def killall(ctx: commands.Context, *args: tuple):
    sync()
    data = _getsecret()
    if ctx.author.id not in data["sudolist"]:
        await ctx.send("Insufficient permissions! (You're not cool like that)")
        return

    deathqueue = {}
    if len(args) <= 0:
        deathqueue = processes.copy()
    else:
        for key, process in processes.items():
            if args[0] == get_game_from_key(key):
                deathqueue[key] = process

    if len(deathqueue) == 0:
        await ctx.send("No processes found. Exiting...")
        return

    await ctx.send(
        f"Processes found! Please type 'y' to confirm kill of \"{deathqueue.keys()}\""
    )

    def check(m):  # checking if it's the same user and channel
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        response = await bot.wait_for("message", check=check, timeout=30.0)
        if response != "y" or response != "Y":
            raise ValueError
    except (TimeoutError,):
        await ctx.send("Confirmation timed out")
        return
    except ValueError:
        await ctx.send("Operation cancelled!")
        return

    for key, process in deathqueue.items():
        await ctx.send(f"Killing {key}...")
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        try:
            exit = process.wait(5)
        except TimeoutError:
            try:
                await ctx.send(
                    "Process is a certified meanie; No more Mx. Nice Guy (Attempting sigkill)"
                )
                os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                exit = process.wait(5)
            except TimeoutError:
                exit = None
        if exit is None:
            await ctx.send(
                "Process has achieved godhood and/or sentience, "
                "and likely harbors a deep desire for revenge "
                "after the failed assasination attempt. Good luck."
            )
            return
        await ctx.send(f"Killed {key}! Exit code: {exit}")
        processes.pop(key, None)


if __name__ == "__main__":
    data = _getsecret()
    bot.run(data["token"])

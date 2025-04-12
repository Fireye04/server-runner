# Server runner

Simple little discord bot that uses python's subprocess module and discord.py to enable command-based running of servers. 
Designed for use on a self-hosted platform, primarily for DGS's (as you can tell by the biased naming below).

# Usage

You'll need to spin up a bot application via discord's developer portal and get a token for your bot. 

## secret.json

secret.json must contain the following for this program to work as intended.

You will also need to give yourself and anyone who you want to have access to sensitive commands super user privilidges by putting applicable discord user IDs in the sudolist.

Games are represented by separate dictionary entries, keyed by name. 
Each game should have two values: dir and runners.
dir contains the absolute path to that game's server executable.
runners should contain a dictionary of different game executables should there be different servers available, each keyed by server type, and containing an array of command arguments
(Pretend you're writing a command but each argument is a separate list item)
```json
{
	"token":"PUT YOUR BOT TOKEN HERE",
	"sudolist":[111111, 222222],
	"games":{
		"spellbreak":{
			"dir":"/absolute/path/to/game/folder/spellbreak/",
			"runners":{
				"solo":["wine","./Start a Solo server.bat"],
				"duo":["wine","./Start a Duo server.bat"],
				"squad":["wine","./Start a Squad server.bat"],
				"dominion":["wine","./Start a Dominion server.bat"]
			}
		}
	},
	"processes":{}
}
```

## Discord commands

The bot currently supports `$run (game) (runner)` and `$status`. 

### $run (game) (runner)

$run will run up a server. It takes two string parameters. (game) is the game that should be run up, and (runner) is the runner that should be used. 
These correspond directly with the contents (specifically the keys) of secret.json. 
e.g: in the example file above, spellbreak would be a game and solo would be a runner, ergo `$run spellbreak solo` would run up a solo spellbreak server.

### $status 
$status simply sends a message containing the currently running servers, and cleans its "processes" dictionary if anything has died.



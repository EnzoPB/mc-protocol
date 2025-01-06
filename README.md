# MC protocol
An easy-to-use, pure Python Minecraft protocol library, allowing you to connect to a server, encode & send, receive & decode packets.

## Installation
For now it is not a work-in-progress, so it will frequently break and have breaking changes to its API. This is why it is not suitable for production use, and is not published on PyPi.
- Clone the repository: `git clone https://github.com/EnzoPB/mc-protocol`
- Navigate into the folder: `cd mc-protocol`
- Install the dependencies: `pip install -r requirements.txt`
- Clone the minecraft-data repository: `git clone https://github.com/PrismarineJS/minecraft-data`
  - Note: You will have to pull this repository for every new Minecraft version
- Start the example script: `python main.py <username> <host> <port>`

## Compatibility
This package is using [minecraft-data](https://github.com/PrismarineJS/minecraft-data), so it should automatically be compatible with every version from 1.8, except:
- 1.19.1 and 1.19.2 because of some weird encryption protocol

## Missing features
These features are listed here because they will be implemented at one point
- Encryption
- Authentication
- Some of the special types (NBT, Anvil chunk data, etc)
- [Packet bundles](https://minecraft.wiki/w/Minecraft_Wiki:Projects/wiki.vg_merge/Protocol#Bundle_Delimiter)

## Thanks to
- The [wiki.vg](https://minecraft.wiki/w/Minecraft_Wiki:Projects/wiki.vg_merge/Main_Page) contributors, for all the very detailed documentation on the Minecraft protocol
- [ammaraskar](https://github.com/ammaraskar), for the [pyCraft](https://github.com/ammaraskar/pyCraft) package, which helped me implement some types and functions in Python
- The PrismarineJS team, for the [minecraft-data](https://github.com/PrismarineJS/minecraft-data) project
- [SpockBotMC](https://github.com/SpockBotMC), for the [python-minecraft-data](https://github.com/SpockBotMC/python-minecraft-data) package (see my fork [here](https://github.com/EnzoPB/python-minecraft-data)!)

## License
[MIT license](https://github.com/EnzoPB/mc-protocol/blob/master/LICENSE)

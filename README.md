# Resident Evil 4 Gamecube - remove faux-letterboxing

### The holy grail (of mine) - GameCube Resident Evil 4, with full-frame rendering achieved. NO CROPPING - this is the real deal, full 4:3 rendered screen.


Removes the faux-letterboxing that was done in the original GameCube version.
The borders were done in 2 passes - one set of horizontal bars was rendered as part of the overlay, and the other - part of the rendering frame.
That's why you could see the bars when emulating in Dolphin and moving the free camera behind, but the render was still letterboxed.

Thanks to the decomp code (esp. Cinescope parts) the parts responsible for these were mapped to the retail builds, and could be manipulated/turned off.

End result - FULL 4:3 512×448 FRAME, with smooth removal (fade in-out) of said letterboxing, with possibility to toggle it per context. It fades out during gameplay (and optionally - cutscenes, just like in future ports). It stays on during movies and menu/inventory screens, as they were showing unintended out-of-bounds stuff.

Tested on Gamecube with latest Swiss, on Resident Evil 4 USA NTSC version. X-delta patch worked, no crashes noted before the initial village title drop.
Also tested the stock rom on Dolphin with Gecko Codes enabling during gameplay.

I made a set of presets for delta patching:

| Preset | Bars removed in | Bars kept in |
|---|---|---|
| **gameplay** | gameplay | pause/options menu, inventory/map/files/shop, cutscenes, movies |
| **gameplay + cutscenes** | gameplay, in-engine cutscenes | pause/options menu, inventory/map/files/shop, movies |
| **everywhere** | the whole game | – |

The gameplay + cutscenes patch is what the future ports look like (no letterboxing in cutscenes). I like the letterboxing in cutscenes, so I kept that as an option.

---

## Installation
## Option 1: Gecko codes

Use one of the codes (and only one).


- **Swiss (real GameCube):** copy `swiss/swiss/cheats/G4BE08.txt` to `SD:/swiss/cheats/`. [NOT TESTED, should work tho]
- **Dolphin:** Move `dolphin/G4BE08.ini` to your dolphin cheats directory or paste it in Cheat tool directly.

## Option 2: patch your ISO

Apply the `.xdelta` patch to your copy of Resident Evil 4 discs via xdelta patcher of your choice (I use this one usually)[https://kotcrab.github.io/xdelta-wasm/]. [Recommended, tested on GameCube with latest Swiss release].


## Credits
Many thanks to the [decomp of a GameCube debug build](https://github.com/adonis-singh/re4) which made it possible.
Also Dolphin team of course, amazing stuff and debug mode is very cool and useful.
Also Claude made this faster to iterate and cross-check the bytes used between decomp build and retail, as memory manipulating in dolphin's mac version is kind of clunky on a laptop screen. All the technical details are in README_MORE.md made by a clanker with some guidance. This one's all human made.

No game data is included in this repository. You need your own legally obtained copy of the game.

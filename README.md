# Resident Evil 4 Gamecube - remove faux-letterboxing

### GameCube Resident Evil 4, playable for the first time in full framing, on OG hardware.
**NO CROPPING** - this is the real deal, fully rendered screen, with smooth fading between in-game and cutscenes/menus.

https://github.com/user-attachments/assets/c364b368-2026-4b8e-8ce9-50cc56abe722

| Before | After |
|----------|----------|
| <img width="583" height="448" alt="G4BE08_2026-10-23_13-03-43" src="https://github.com/user-attachments/assets/9efd72f4-1d69-481e-86b8-dd383a8b2eb6" />  | <img width="583" height="448" alt="G4BE08_2026-11-22_13-36-55" src="https://github.com/user-attachments/assets/0364b276-3091-4732-a7d3-7a29ce37ebd7" /> |


Direct gamecube captures @ 480p (only in-game letterbox removed [no hud adjustment applied]):
| In-game | Cutscenes| Inventory | 
|----------|----------|----------|
| <img width="720" height="480" alt="snap 8" src="https://github.com/user-attachments/assets/5642352a-8340-4697-ac82-00296a2ff754" /> | <img width="720" height="480" alt="snap 6" src="https://github.com/user-attachments/assets/b8ab832f-6072-4975-8f61-8645e1bbeeea" /> | <img width="720" height="480" alt="snap 7" src="https://github.com/user-attachments/assets/11cc6c1b-cedd-430a-9ba3-aea00b7c23fd" /> |

---

Removes the faux-letterboxing that was done in the original GameCube version.
The borders were done in 2 passes - one set of horizontal bars was rendered as part of the overlay, and the other - part of the rendering frame.
That's why you could see the bars when emulating in Dolphin and moving the free camera behind, but the render was still letterboxed nonetheless.

Thanks to the decomp code (esp. Cinescope sections) the parts responsible for these were mapped to the retail builds, and could be manipulated/turned off.

End result - FULL 4:3 512×448 framing, with smooth context-aware fading of said letterboxing, with possibility to toggle it per context/completely. 

It fades out during gameplay (and optionally - cutscenes, just like in future ports). It stays on during movies and menu/inventory screens, as they were showing unintended out-of-bounds stuff.


Pre-made sets for x-delta patching

| Preset | Bars removed in | Bars kept in |
|---|---|---|
| **gameplay** | gameplay | pause/options menu, inventory/map/files/shop, cutscenes, movies |
| **gameplay + cutscenes, AKA modern ports** | gameplay, in-engine cutscenes | pause/options menu, inventory/map/files/shop, movies |
| **everywhere** | the whole game | – |

The gameplay + cutscenes patch is what the future ports look like (no letterboxing in cutscenes). I like the letterboxing in cutscenes, so I kept that as an option.

---

## Installation
### Option 1: Gecko cheat code

Use one of the codes (and only one).
- **Swiss (real GameCube):** copy `swiss/swiss/cheats/G4BE08.txt` to `SD:/swiss/cheats/`. [NOT TESTED, should work tho]
- **Dolphin:** Move `dolphin/G4BE08.ini` to your dolphin cheats directory or paste it in Cheat tool directly.

### Option 2: patch an ISO

Apply the `.xdelta` patch to your copy of Resident Evil 4 discs via xdelta patcher of your choice (I use this one usually)[https://kotcrab.github.io/xdelta-wasm/]. [Recommended, tested on GameCube with latest Swiss release].


## Credits
Many thanks to the [decomp of a GameCube debug build](https://github.com/adonis-singh/re4) which made it possible.
Also Dolphin team of course, amazing stuff and debug mode is very cool and useful.
Claude was used to to iterate and cross-check the bytes used between decomp build and retail, as memory manipulating in dolphin's mac version is kind of clunky on a Mac/laptop screen. All the technical details are in README_MORE.md made by a clanker with some guidance. This one's all human written.

No game data is included in this repository. You need your own legally obtained copy of the game.

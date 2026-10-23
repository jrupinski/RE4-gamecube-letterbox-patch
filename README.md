# Resident Evil 4 (GameCube) – Letterbox Removal

Removes the cinemascope letterbox from **Resident Evil 4 (USA, `G4BE08`)**. The game renders and
outputs its full native **512×448** frame: nothing is cropped, stretched or rescaled, so the image
stays pixel-sharp on any output (analog, GCVideo/Swiss digital out, Dolphin).

The patch is **modular**: choose in which parts of the game the bars are removed.

| Part | Removes the bars in |
|---|---|
| `gameplay` | normal play |
| `menu` | the pause / options menu |
| `subscreen` | inventory, map, files, shop |
| `cutscene` | in-engine cutscenes |
| `movie` | pre-rendered movies |

Parts you don't select keep the original bars, which fade in and out just like in the original
game. Menus and movies were laid out for the letterboxed screen, so **gameplay only** is the
recommended choice. Selecting everything removes the bars from the whole game.

**Tested on a real GameCube via Swiss** with no errors, including Hunnigan's radio calls, and in
Dolphin.

Only the **USA release (`G4BE08`, Rev 0)** is supported. Both discs share the same `main.dol`, so
everything applies to Disc 1 and Disc 2.

---

## Option 1: Gecko codes (Swiss / Dolphin)

The codes are one required **core** code plus one code per part. Enable the core and any parts you want.

| Code | What it does |
|---|---|
| `Letterbox: core (required, no visible change on its own)` | installs the switchable letterbox logic and full-frame rendering; on its own the game looks original |
| `Letterbox: remove in gameplay` | 1 line |
| `Letterbox: remove in pause/options menu` | 1 line |
| `Letterbox: remove in inventory/map/files/shop` | 1 line |
| `Letterbox: remove in cutscenes` | 1 line |
| `Letterbox: remove in movies` | 1 line |

- **Swiss (real GameCube):** copy `swiss/swiss/cheats/G4BE08.txt` to `SD:/swiss/cheats/G4BE08.txt`,
  then enable the core and the parts you want in the game's cheats menu.
- **Dolphin:** add the contents of `dolphin/G4BE08.ini` to your user `GameSettings/G4BE08.ini`
  (core + gameplay are pre-enabled), or paste the codes in **Properties → Gecko Codes**.

## Option 2: patch your ISO

You need your own **plain ISO** dumps that match Redump, not RVZ, NKit or CISO. Dolphin can
convert an RVZ to ISO: right-click the game, then **Convert File… → ISO**.

| Disc | Source ISO MD5 |
|---|---|
| Disc 1 | `ca749757e3b9d119f3feb1f9f0f81bd7` |
| Disc 2 | `2381acd2199d6e7566932df86901903d` |

### a) Patcher script (any combination)

`patch_re4.py` needs Python 3 only. It patches the ISO **in place**, so work on a copy:

```sh
cp "Resident Evil 4 (USA) (Disc 1).iso" "RE4 Disc 1 [No Letterbox].iso"
python3 patch_re4.py "RE4 Disc 1 [No Letterbox].iso" --gameplay
python3 patch_re4.py "RE4 Disc 1 [No Letterbox].iso" --gameplay --subscreen --movie   # any combination
python3 patch_re4.py "RE4 Disc 1 [No Letterbox].iso" --all                            # everywhere
```

The script checks the game ID and every original word before writing. You can run it again on an
already patched ISO to add more parts.

### b) Ready-made xdelta presets

Apply with [xdelta3](https://github.com/jmacd/xdelta) or a GUI such as Delta Patcher:

```sh
xdelta3 -d -s "Resident Evil 4 (USA) (Disc 1).iso" \
  "patches/Resident Evil 4 (USA) (Disc 1) - No Letterbox (gameplay only).xdelta" \
  "Resident Evil 4 (USA) (Disc 1) [No Letterbox].iso"
```

| Preset | Disc 1 result MD5 | Disc 2 result MD5 |
|---|---|---|
| gameplay only | `dc4d91590d954288731e1df7e6a52684` | `12a97836597eae9ebd87cd8b5c4688dd` |
| everywhere | `85b7d1773222474c22feb134bc59acc1` | `d1ff414ae83c18f6e08fbee06cde7d88` |

Use **either** a patched ISO **or** the Gecko codes, not both. They make identical changes.

---

## How it works

The letterbox in the GameCube version is made of three things:

1. **`Draw_cinesco()`** (`0x80171C64`) draws two black quads over rows 0–56 and 393–449 at the
   end of every frame. Its controller (`game/cinesco.cpp`) fades the bars in and out over 15 frames.
2. **HUD bar sprites** (`IDC_CINESCO`, HUD display group `0x30`) are a second pair of black bars
   in the HUD sprite list.
3. **A "letterbox mode" flag** (bit `0x800` of `pG+0x54`) restricts the 3D render scissor to rows
   56–392 and switches several screen effects to their strip-only variants.

The game already renders the 3D scene with a full 4:3 projection over the whole 448-line viewport.
The letterbox only covered it up, so removing the bars shows real picture, not stretched picture.

The **core** code:

- hides the HUD bar sprites (group `0x30`)
- makes every letterbox-mode check take the game's full-frame path
- makes the fade overlay cover the whole screen
- replaces the bar controller with a small routine that detects the current context and reads one
  "option slot" per context

The slots are leftover words of the old controller code, which are never executed any more and
are non-zero, meaning "keep the bars". Each **part** code writes `0` into its own slot, meaning
"remove the bars here". Because each part writes a different address, any combination works.

Context detection works like this:

- `Stop_flg` (`pG+0x170`) is 0 during free play, so that is gameplay.
- Otherwise the game is frozen. It is a movie, a cutscene or a sub screen if the corresponding
  `Status_flg` bit is set, and the pause/options menu if none is set.

**[docs/CODE_REFERENCE.md](docs/CODE_REFERENCE.md)** explains every single line: address,
original instruction, new instruction, and what it does.

## Known issues

- A few post-processing effects (some blur/glow passes) copy only rows 56–392 by design, because
  those coordinates are hard-coded in the game. In some scenes they may stop at a visible edge near
  the top or bottom of the screen.
- **Dolphin only:** at the end of Hunnigan's radio calls, Dolphin may show
  `Invalid read from 0xffffffe4, PC = 0x80191b90`. This is a known Dolphin issue with the
  **unmodified** game ([dolphin-emu #13579](https://bugs.dolphin-emu.org/issues/13579)), not
  caused by this patch, and it does not occur on real hardware. Click "Ignore for this session",
  or enable **Write-Back Cache** in Dolphin.
- **Dolphin only:** a single purple frame when closing the inventory or map also happens with the
  unmodified game. It is Dolphin's display of an empty frame buffer. Turning off
  **Graphics → Hacks → Store XFB Copies to Texture Only** avoids it.

## Credits

- Function names and structures were identified with the help of the
  [Resident Evil 4 GameCube decompilation](https://github.com/adonis-singh/re4) (debug build),
  in particular `game/cinesco.cpp`.
- Reverse engineering and patch development done with Dolphin and Claude Code.

No game data is included in this repository. You need your own legally obtained copy of the game.

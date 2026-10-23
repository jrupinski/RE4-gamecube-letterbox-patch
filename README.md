# Resident Evil 4 (GameCube) – Letterbox Removal

Removes the cinemascope letterbox from **Resident Evil 4 (USA, `G4BE08`)**. The game renders and
outputs its full native **512×448** frame: nothing is cropped, stretched or rescaled, so the image
stays pixel-sharp on any output (analog, GCVideo/Swiss digital out, Dolphin).

Choose **one** preset:

| Preset | Bars removed in | Bars kept in |
|---|---|---|
| **gameplay** (recommended) | gameplay | pause/options menu, inventory/map/files/shop, cutscenes, movies |
| **gameplay + cutscenes** | gameplay, in-engine cutscenes | pause/options menu, inventory/map/files/shop, movies |
| **everywhere** | the whole game | – |

Menus, the inventory and movies were laid out for the letterboxed screen, so they look best with
the bars kept. Where the bars are kept, they fade in and out just like in the original game.

**The gameplay preset is tested on a real GameCube via Swiss** with no errors, including Hunnigan's
radio calls.

Only the **USA release (`G4BE08`, Rev 0)** is supported. Both discs share the same `main.dol`, so
everything applies to Disc 1 and Disc 2.

---

## Option 1: Gecko codes (Swiss / Dolphin)

Enable **exactly one** of the three codes.

- **Swiss (real GameCube):** copy `swiss/swiss/cheats/G4BE08.txt` to `SD:/swiss/cheats/G4BE08.txt`
  and enable one code in the game's cheats menu.
- **Dolphin:** add the contents of `dolphin/G4BE08.ini` to your user `GameSettings/G4BE08.ini`
  (the gameplay preset is pre-enabled), or paste a code in **Properties → Gecko Codes**.

## Option 2: patch your ISO

You need your own **plain ISO** dumps that match Redump, not RVZ, NKit or CISO. Dolphin can
convert an RVZ to ISO: right-click the game, then **Convert File… → ISO**.

| Disc | Source ISO MD5 |
|---|---|
| Disc 1 | `ca749757e3b9d119f3feb1f9f0f81bd7` |
| Disc 2 | `2381acd2199d6e7566932df86901903d` |

### a) xdelta patches

Apply with [xdelta3](https://github.com/jmacd/xdelta) or a GUI such as Delta Patcher:

```sh
xdelta3 -d -s "Resident Evil 4 (USA) (Disc 1).iso" \
  "patches/Resident Evil 4 (USA) (Disc 1) - No Letterbox (gameplay).xdelta" \
  "Resident Evil 4 (USA) (Disc 1) [No Letterbox].iso"
```

| Preset | Disc 1 result MD5 | Disc 2 result MD5 |
|---|---|---|
| gameplay | `6c372fd391d2add37de83027182bd099` | `21fc8de4158328934759cd734d16b357` |
| gameplay + cutscenes | `3cf7546a34044326a50a1f9ecb671976` | `ead1c0d08f41656736554b2f7687c8df` |
| everywhere | `94eba2d3dae28e97aaf866ec791d0adb` | `d3a9a7503e4fe9116e5864151664c085` |

### b) Patcher script

`patch_re4.py` needs Python 3 only. It patches **in place**, so work on a copy:

```sh
cp "Resident Evil 4 (USA) (Disc 1).iso" "RE4 Disc 1 [No Letterbox].iso"
python3 patch_re4.py "RE4 Disc 1 [No Letterbox].iso" gameplay      # or: cutscenes, all
```

The script checks the game ID and every original word before writing.

Use **either** a patched ISO **or** a Gecko code, not both. They make identical changes.

---

## How it works

The letterbox in the GameCube version is made of three things:

1. **`Draw_cinesco()`** (`0x80171C64`) draws two black quads over rows 0–56 and 393–449 at the
   end of every frame. Its controller `cine_polling()` (`0x80171B3C`) decides once per frame whether
   the bars are on and fades them in or out over 15 frames.
2. **HUD bar sprites** (`IDC_CINESCO`, HUD display group `0x30`) are a second pair of black bars
   in the HUD sprite list.
3. **A "letterbox mode" flag** (bit `0x800` of `pG+0x54`) restricts the 3D render scissor to rows
   56–392 and switches several screen effects to their strip-only variants.

The game already renders the 3D scene with a full 4:3 projection over the whole 448-line viewport.
The letterbox only covered it up, so removing the bars shows real picture, not stretched picture.

All presets share 12 lines:

- 5 lines hide the HUD bar sprites
- 6 lines make every letterbox-mode check take the game's full-frame path
- 1 line makes the fade overlay cover the whole screen

The presets then differ only in the yes/no decision inside `cine_polling`. It originally reads "bars
on when the game requests them", which is always. `Draw_cinesco` and the fade routines are untouched.

- **gameplay** (2 lines): bars on when `Stop_flg` (`pG+0x170`) is non-zero, i.e. the game is frozen
  (menus, inventory, cutscenes, movies).
- **gameplay + cutscenes** (7 lines): bars on when the game is frozen and the cutscene flag
  (`STA_EVENT`, `0x00001000` in `pG+0x5018`) is not set.
- **everywhere** (1 line): the bars are never requested.

**[docs/CODE_REFERENCE.md](docs/CODE_REFERENCE.md)** explains every single line: address,
original instruction, new instruction, and what it does.

## Known issues

- A few post-processing effects (some blur/glow passes) copy only rows 56–392 by design, because
  those coordinates are hard-coded in the game. In some scenes they may stop at a visible edge near
  the top or bottom of the screen.
- **gameplay + cutscenes:** a movie that plays during a cutscene event would also lose its bars.
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

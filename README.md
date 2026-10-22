# Resident Evil 4 (GameCube) – Letterbox Removal

Removes the cinemascope letterbox from **Resident Evil 4 (USA, `G4BE08`)** during normal gameplay.
The game renders and outputs its full native **512×448** frame: nothing is cropped, stretched or
rescaled, so the image stays pixel-sharp on any output (analog, GCVideo/Swiss digital out, Dolphin).

Menus, the inventory, cutscenes and FMV movies keep the original bars, because their layouts were
designed for the letterboxed frame. The bars fade in and out exactly as in the original game.

| Original | Patched |
|---|---|
| 336 visible lines, 56-line black bars top and bottom | Full 448 lines of picture during gameplay |

Provided as:

- **xdelta patches** for both discs (play on a GameCube via Swiss/ODE, or in Dolphin)
- **Gecko code** (Swiss cheats file and Dolphin `.ini`)

**Tested on a real GameCube via Swiss** with no errors, including Hunnigan's radio calls, and in
Dolphin.

Only the **USA release (`G4BE08`, Rev 0)** is supported. Both discs share the same `main.dol`, so
the same changes apply to Disc 1 and Disc 2.

---

## Option 1: xdelta patch (recommended)

You need your own **plain ISO** dumps that match Redump, not RVZ, NKit or CISO. Dolphin can
convert an RVZ to ISO: right-click the game, then **Convert File… → ISO**.

| Disc | Source ISO MD5 | Patched ISO MD5 |
|---|---|---|
| Disc 1 | `ca749757e3b9d119f3feb1f9f0f81bd7` | `6c372fd391d2add37de83027182bd099` |
| Disc 2 | `2381acd2199d6e7566932df86901903d` | `21fc8de4158328934759cd734d16b357` |

Apply with [xdelta3](https://github.com/jmacd/xdelta) or a GUI such as Delta Patcher:

```sh
xdelta3 -d -s "Resident Evil 4 (USA) (Disc 1).iso" \
  "patches/Resident Evil 4 (USA) (Disc 1) - Full Frame.xdelta" \
  "Resident Evil 4 (USA) (Disc 1) [Full Frame].iso"

xdelta3 -d -s "Resident Evil 4 (USA) (Disc 2).iso" \
  "patches/Resident Evil 4 (USA) (Disc 2) - Full Frame.xdelta" \
  "Resident Evil 4 (USA) (Disc 2) [Full Frame].iso"
```

## Option 2: Gecko code

### Swiss (real GameCube)

Copy `swiss/swiss/cheats/G4BE08.txt` to `SD:/swiss/cheats/G4BE08.txt`. Then select the game in
Swiss and enable **Full Frame (no letterbox during gameplay)** in its cheats menu.

### Dolphin

Add the contents of `dolphin/G4BE08.ini` to your Dolphin user `GameSettings/G4BE08.ini`, or enter
the code below in **Properties → Gecko Codes**. Cheats must be enabled in Dolphin's settings.

```
$Full Frame (no letterbox during gameplay)
040FA860 70090000
0411BB88 881F0002
0411BB8C 28000030
0411BB90 41820050
0411BB94 5409EEFA
0411BB98 7D69E02E
0411BB9C 5D6B0001
0411BBA0 40820040
04165E88 700B0000
041789A8 70090000
04178DC8 70090000
0417CADC 70090000
04182FD4 70090000
041EBB2C 00000000
04171B44 80090170
04171B48 2C000000
```

Use **either** the patched ISO **or** the Gecko code, not both. They make identical changes.

---

## How it works

The letterbox in the GameCube version is made of three things:

1. **`Draw_cinesco()`** (`0x80171C64`) draws two black quads over rows 0–56 and 393–449 at
   the end of every frame. It is driven by `cine_polling()` (`0x80171B3C`), which fades the bars
   in and out based on a status flag that the game sets every frame.
2. **HUD bar sprites** (`IDC_CINESCO`, HUD display group `0x30`) are a second pair of black bars
   in the HUD sprite list.
3. **A "letterbox mode" flag** (bit `0x800` of `pG+0x54`) restricts the 3D render scissor to rows
   56–392 and switches several screen effects to their band-only variants.

The patch changes 16 words in `main.dol`:

| Address | Change |
|---|---|
| `8011BB88`–`8011BBA0` | HUD sprite loop: the group-visibility check is rewritten more compactly so it can also skip group `0x30` (the bar sprites). |
| `800FA860`, `80165E88`, `801789A8`, `80178DC8`, `8017CADC`, `80182FD4` | `andi. rX, r0, 0x800` → `andi. rX, r0, 0`: every letterbox-mode check takes the game's own full-frame path (render scissor and effects). |
| `801EBB2C` | Screen fade quad offset `56.0` → `0.0`, so fades cover the full frame. |
| `80171B44`, `80171B48` | `cine_polling`: the bars are requested only when `Stop_flg` (`pG+0x170`) is non-zero, i.e. when the game is frozen (pause/options, inventory, cutscenes, movies). The bars are off during free play. |

The game already renders the 3D scene with a full 4:3 projection over the whole 448-line viewport.
The letterbox only covered it up, so removing the bars shows real picture, not stretched picture.

## Known issues

- A few post-processing effects (some blur/glow passes) copy only rows 56–392 by design, because
  those coordinates are hard-coded in the game. In some scenes they may stop at a visible edge near
  the top or bottom of the screen.
- Brief moments that set some of the game's stop flags in gameplay, such as doors, may fade the bars in.
- **Dolphin:** at the end of Hunnigan's radio calls, Dolphin may show
  `Invalid read from 0xffffffe4, PC = 0x80191b90`. This is a known Dolphin issue with the
  **unmodified** game ([dolphin-emu #13579](https://bugs.dolphin-emu.org/issues/13579)), not
  caused by this patch, and it does not occur on real hardware. Click "Ignore for this session",
  or enable **Write-Back Cache** in Dolphin.

## Credits

- Function names and structures were identified with the help of the
  [Resident Evil 4 GameCube decompilation](https://github.com/adonis-singh/re4) (debug build),
  in particular `game/cinesco.cpp`.
- Reverse engineering and patch development done with Dolphin and Claude Code.

No game data is included in this repository. You need your own legally obtained copy of the game.

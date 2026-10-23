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

Enable **exactly one** of the three preset codes. Optionally also enable
**HUD: move health meter to screen edge in gameplay** (see [Optional: health meter position](#optional-health-meter-position)).

- **Swiss (real GameCube):** copy `swiss/swiss/cheats/G4BE08.txt` to `SD:/swiss/cheats/G4BE08.txt`
  and enable one code in the game's cheats menu.
- **Dolphin:** add the contents of `dolphin/G4BE08.ini` to your user `GameSettings/G4BE08.ini`
  (the gameplay preset is pre-enabled), or paste a code in **Properties → Gecko Codes**.

## Optional: health meter position

The HUD was laid out for the letterboxed picture. Without the bars, the health meter (ammo ring,
ammo count, "Leon") floats 56 pixels above the bottom edge. The optional Gecko code
**HUD: move health meter to screen edge in gameplay** moves it down by exactly that amount, so it
sits at the bottom edge like in the original framing. Use it together with a preset. It is
available as a **Gecko code only**: it adds new code, and `main.dol` has no free space for that in
an ISO patch.

```
C211B06C 00000009
899F0002 2C0C0021
40820034 819F0068
2C0C0000 40820028
818D8B00 818C0170
2C0C0000 40820018
C01F0098 3D80802B
C02C3F54 EC000828
D01F0098 881F0004
60000000 00000000
```

**How it works.** The HUD is drawn by the ID system (decomp `game/id_sys.cpp`). Every frame,
`idSysMove00` (`0x8011AE9C`) computes each HUD object's position as `pos = pos0 + animation
offset` (`ID_UNIT`: `+0x88` pos0, `+0x94` pos, `+0x02` class, `+0x68` parent). The units are a
640×480 screen space with y = 0 at the centre and negative y downwards. The bars covered 60 units
at each edge, i.e. 56 pixels of the 448-line frame.

The `C2` line inserts code right after that calculation, at `0x8011B06C`. For objects of class
`0x21` (`IDC_LIFE_METER`) that have no parent, and only while `Stop_flg` (`pG+0x170`) is 0 (free
play), it subtracts 60.0 from `pos.y`. Child objects (ring, digits, name plate) follow their parent.
Menus and the inventory keep the original position, under their bars.

| Instruction | What it does |
|---|---|
| `lbz r12, 2(r31)` / `cmpwi r12, 0x21` / `bne done` | only HUD objects of class 0x21 (health meter) |
| `lwz r12, 0x68(r31)` / `cmpwi r12, 0` / `bne done` | only top-level objects (children follow) |
| `lwz r12, -0x7500(r13)` / `lwz r12, 0x170(r12)` / `cmpwi r12, 0` / `bne done` | only in free play (`Stop_flg == 0`) |
| `lfs f0, 0x98(r31)` | f0 = `pos.y` |
| `lis r12, 0x802B` / `lfs f1, 0x3F54(r12)` | f1 = 60.0 (an existing constant in the game's read-only data) |
| `fsubs f0, f0, f1` / `stfs f0, 0x98(r31)` | `pos.y -= 60` (56 pixels down) |
| `done: lbz r0, 4(r31)` | the original instruction at `0x8011B06C` |

Moving the whole HUD at once (the HUD screen matrix `IDSystem::m_scrn_mat`, `0x802B173C`) also
works, but it slides other HUD parts into view, such as a red marker that the game parks just
above the top edge. That's why the code moves only the health meter.

---

## Option 2: patch your ISO

You need your own **plain ISO** dumps that match Redump, not RVZ, NKit or CISO. Dolphin can
convert an RVZ to ISO: right-click the game, then **Convert File… → ISO**.

| Disc | Source ISO MD5 |
|---|---|
| Disc 1 | `ca749757e3b9d119f3feb1f9f0f81bd7` |
| Disc 2 | `2381acd2199d6e7566932df86901903d` |

Apply the `.xdelta` file for your disc and preset from `patches/` with any xdelta patcher, for example:

- [Rom Patcher JS](https://www.marcrobledo.com/RomPatcher.js/) (in the browser, no install)
- Delta Patcher (Windows, macOS, Linux)
- the `xdelta3` command line tool:

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

Use **either** a patched ISO **or** a Gecko code, not both. They make identical changes.

---

## How it works

### Where the letterbox comes from

The letterbox in the GameCube version is made of three separate things. All three have to be
handled to get a clean full frame.

1. **`Draw_cinesco()`** (`0x80171C64`, decomp `game/cinesco.cpp`) draws two black quads over rows
   0–56 and 393–449 of the 512×448 frame at the end of every frame, with the alpha in `cine_work`.
   It draws nothing when the alpha is 0.
2. **HUD bar sprites** (`IDC_CINESCO`) are a second pair of black 640×60 bars at y = ±210 in the
   HUD sprite list, in HUD display group `0x30`.
3. **A "letterbox mode" flag** (bit `0x800` of `pG+0x54`) restricts the 3D render scissor to rows
   56–392 and switches several screen effects to their strip-only variants.

The game already renders the 3D scene with a full 4:3 projection (vertical FOV 50°, aspect 1.333)
over the whole 512×448 viewport. The letterbox only covered it up, so removing it shows real
picture, not stretched picture.

### Game data used

| Address | Name | Meaning |
|---|---|---|
| `0x8027F7D0` | `pG` | the game's main state structure (also reachable as `lwz rX, -0x7500(r13)`) |
| `pG+0x54` | `System_flg` | bit `0x800` = letterbox mode |
| `pG+0x170` | `Stop_flg` | 0 during free play, `0xFFFFFFFF` while the game is frozen: pause/options menu, inventory/map/files/shop, cutscenes, movies |
| `pG+0x5018` | `Status_flg[0]` | `0x01000000` STA_CINESCO (letterbox requested), `0x00040000` STA_SUB_SCRN (inventory etc.), `0x00001000` STA_EVENT (cutscene), `0x10000000`/`0x04000000` STA_MOVIE_ON / STA_MOVIE2_ON |
| `pG+0x5024` | `Status_flg[3]` | bit `0x10000000` = letterbox scissor active (set by the render loop) |
| `0x802B3220` | `cine_work` | `+0` state (0 idle, 1 fade in, 2 fade out), `+1` bar alpha, `+2` previous on/off, `+4` fade timer (float) |
| `0x8027F5DC` | HUD sprite list | `+0x2C` hidden-groups bitmask, `+0x4C` sprite array (`0x138` bytes per sprite, group at `+2`, layer at `+0x80`) |

The bit numbering of the decomp's flag enums is MSB-first: flag *n* is
`0x80000000 >> (n % 32)` in word *n / 32*. The decomp is a debug build, and in retail
`Status_flg` sits at `pG+0x5018` instead of the decomp's `0x500C`. The early fields
(`System_flg`, `Stop_flg`, …) are at the same offsets.

### The original bar controller

Each frame `CinescoMove` (`0x80171AF0`) sets STA_CINESCO and calls one of three routines through
the table `cine_tbl` at `0x8020CE60`:

- `cine_polling` (`0x80171B3C`): decides whether the bars should be on, and starts a 15-frame fade
  when that changes
- `cine_on_move` (`0x80171B94`): fade in
- `cine_off_move` (`0x80171C00`): fade out

```
cine_polling:
80171B3C  lwz    r9, -0x7500(r13)   ; r9 = pG
80171B40  li     r11, 1             ; want bars = 1
80171B44  lwz    r0, 0x5018(r9)     ; r0 = Status_flg[0]
80171B48  andis. r9, r0, 0x100      ; STA_CINESCO set?
80171B4C  bne    +8                 ; yes: keep 1
80171B50  li     r11, 0             ; no: want bars = 0
80171B54  lbz    r0, 2(r3)          ; previous on/off
80171B58  extsb  r0, r0
80171B5C  cmpw   r0, r11            ; changed?
80171B60  beqlr                     ; no: return
...                                 ; yes: store it, state = 1 or 2, timer = 15.0
```

The presets change only the decision part (`0x80171B40`–`0x80171B58`). The fade routines and
`Draw_cinesco` are untouched.

## Every line explained

A Gecko line `04XXXXXX YYYYYYYY` writes the 32-bit value `YYYYYYYY` to address `0x80XXXXXX` (the
game's code and data in RAM). The xdelta patches write exactly the same values
into `main.dol`. All presets share the first 12 lines.

### Shared 1: hide the HUD bar sprites (5 lines, needed, all together)

The HUD drawing loop (`0x8011BB2C`) already skips sprites whose group bit is set in the
hidden-groups mask. These lines rewrite that check in fewer instructions. The two freed slots now
also skip group `0x30`. Removing any one of them breaks the loop.

| Line | Original | New | What it does |
|---|---|---|---|
| `0411BB8C 28000030` | `rlwinm r9,r0,29,27,29` | `cmplwi r0, 0x30` | is this sprite in group 0x30 (the bar sprites)? |
| `0411BB90 41820050` | `clrlwi r0,r0,27` | `beq 0x8011BBE0` | yes: skip drawing it |
| `0411BB94 5409EEFA` | `lwzx r11,r9,r28` | `rlwinm r9,r0,29,27,29` | (moved) word index into the hidden-groups mask = group / 32 |
| `0411BB98 7D69E02E` | `srw r0,r27,r0` | `lwzx r11,r9,r28` | (moved) load the mask word |
| `0411BB9C 5D6B0001` | `and. r9,r11,r0` | `rlwnm. r11,r11,r0,0,0` | rotate the sprite's group bit to the top and test it; this replaces the original shift + and, which freed the two slots |

### Shared 2: render the full frame (6 lines)

Each line changes `andi. rX, r0, 0x800` (test the letterbox-mode flag) to `andi. rX, r0, 0`
(always false), so that code takes the game's own full-frame path.

| Line | Location | Needed? |
|---|---|---|
| `04165E88 700B0000` | main render loop (`0x80165E60`): enables the 3D scissor to rows 56–392 (via `pG+0x5024` and `0x80123E14`) | **yes**: the flag is on during gameplay, and without this line rows 0–55 and 393–447 stay black |
| `040FA860 70090000` | screen effect: EFB strip copy offset (56 vs 0) | cosmetic: without it the effect covers only rows 56–392 |
| `041789A8 70090000` | screen effect: EFB copy offset (56 vs 0) | cosmetic: pairs with the next line |
| `04178DC8 70090000` | the same effect: texture projection (y scale 0.667 strip / 0.5 full) | must be changed together with the previous line |
| `0417CADC 70090000` | screen effect: offset (56 vs 0) | cosmetic |
| `04182FD4 70090000` | screen effect: offset (56 vs 0) | cosmetic |

The five effect lines were never tested individually. Try removing one at a time and watch for an
effect (blur, glow, heat haze) ending at a hard edge 56 rows from the top or bottom.

### Shared 3: full-screen fades (1 line)

| Line | Original | New | What it does |
|---|---|---|---|
| `041EBB2C 00000000` | float `56.0` | float `0.0` | top offset of the fade-to-black overlay (function `0x8011251C`); without it, fades leave the top and bottom rows bright |

### Preset "gameplay": bars in menus, inventory, cutscenes, movies (2 lines)

| Line | Original | New | What it does |
|---|---|---|---|
| `04171B44 80090170` | `lwz r0, 0x5018(r9)` | `lwz r0, 0x170(r9)` | read `Stop_flg` instead of `Status_flg[0]` |
| `04171B48 2C000000` | `andis. r9, r0, 0x100` | `cmpwi r0, 0` | bars on when `Stop_flg != 0` (game frozen) instead of when STA_CINESCO is set |

### Preset "gameplay + cutscenes": bars in menus, inventory, movies (7 lines)

The rule is: bars on = `Stop_flg != 0` AND NOT STA_EVENT.

| Line | Original | New | What it does |
|---|---|---|---|
| `04171B40 80090170` | `li r11, 1` | `lwz r0, 0x170(r9)` | r0 = `Stop_flg` |
| `04171B44 81295018` | `lwz r0, 0x5018(r9)` | `lwz r9, 0x5018(r9)` | r9 = `Status_flg[0]` |
| `04171B48 3180FFFF` | `andis. r9, r0, 0x100` | `addic r12, r0, -1` | carry = (`Stop_flg != 0`) |
| `04171B4C 7D6C0110` | `bne +8` | `subfe r11, r12, r0` | r11 = carry: 1 = frozen, 0 = free play |
| `04171B50 5529A7FE` | `li r11, 0` | `rlwinm r9, r9, 20, 31, 31` | r9 = STA_EVENT bit (`0x00001000`) as 0/1 |
| `04171B54 7D6B4878` | `lbz r0, 2(r3)` | `andc r11, r11, r9` | r11 = frozen AND NOT cutscene |
| `04171B58 88030002` | `extsb r0, r0` | `lbz r0, 2(r3)` | the original "previous on/off" load, moved down one slot; the `extsb` was dropped because the value is only ever 0 or 1 |

Because cutscenes are detected by STA_EVENT, a movie that plays during an event would also lose its
bars.

### Preset "everywhere": no bars (1 line)

| Line | Original | New | What it does |
|---|---|---|---|
| `04171B4C 60000000` | `bne +8` | `nop` | the "bars on" branch is never taken, so `li r11, 0` always runs and the bars are never requested |

## Notes for further work

- **Minimum set:** to remove the bars only, you need the sprite lines (5) + `04165E88` + the
  decision lines. The effect lines and the fade line are for clean results.
- **New presets:** any rule that `cine_polling` can compute in the decision slots
  (`0x80171B40`–`0x80171B58`, 7 words once `extsb` is dropped) works without new code.
  - A single bit test of `Status_flg[0]` fits in one line. For example, "bars only in movies" is
    `04171B48 74091400` (`andis. r9, r0, 0x1400`).
  - Movie and sub-screen bits are in the upper half of the word and STA_EVENT is in the lower half,
    so one `andis.`/`andi.` can't test both.
- **Strip-only effects not handled:** a few effects copy the EFB strip with the top `0x38` written
  directly into their code, regardless of the letterbox flag: functions around `0x800F66F8`,
  `0x800FD994`, `0x801015BC` and `0x8016CBD0` (`li r4, 0x38` before `GXSetTexCopySrc`
  `0x80095E44`). They aren't patched. If an effect shows an edge, it is probably one of these.
- **Other functions of interest:**

  | Address | Function |
  |---|---|
  | `0x80093B5C` | `GXSetScissor` |
  | `0x80093AF0` | `GXSetViewport` |
  | `0x80093708` | `GXSetProjection` |
  | `0x80095DC8` | `GXSetDispCopySrc` |
  | `0x80096400` | `GXCopyDisp` |
  | `0x8012405C` | render-mode setup (512×448 EFB/XFB) |
  | `0x80123E14` | restore the scissor (applies the letterbox scissor if `pG+0x5024 & 0x10000000`) |

- **Other regions:** the addresses are for USA Rev 0 only. A PAL port (`G4BP08`) would need the
  same functions located again. The decomp's function names and the instruction patterns above
  make that straightforward.
- **Debugging:** in Dolphin, Free Look shows which parts are overlays: overlays move with the
  camera, while the scissored render area does not. Dolphin's debugger (`Dolphin -d`) and
  memory view work well with the addresses above.

**[docs/CODE_REFERENCE.md](docs/CODE_REFERENCE.md)** contains the same per-line tables, generated
from the patch data.

## Credits

- Function names and structures were identified with the help of the
  [Resident Evil 4 GameCube decompilation](https://github.com/adonis-singh/re4) (debug build),
  in particular `game/cinesco.cpp`.
- Reverse engineering and patch development done with Dolphin and Claude Code.

No game data is included in this repository. You need your own legally obtained copy of the game.

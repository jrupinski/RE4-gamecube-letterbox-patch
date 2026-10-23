# Code reference

Every line of the Gecko codes. These are also every word the xdelta patches change in `main.dol`. A
Gecko line `04XXXXXX YYYYYYYY` writes the 32-bit value `YYYYYYYY` to address `0x80XXXXXX`, the
game's code and data in RAM. Disassembly is PowerPC (Gekko). Each preset is the **shared lines**
plus the **preset lines**. See [README_MORE.md](../README_MORE.md) for background.

The tables list every changed word as its own `04` line, for readability. The shipped codes in
`swiss/` and `dolphin/` are packed: runs of 3 or more consecutive words use the Gecko string-write
type `06XXXXXX NNNNNNNN` (write `NNNNNNNN` bytes starting at `0x80XXXXXX`), followed by the data
two words per line. The last data line is padded with `00000000`, which isn't written. Packed and
unpacked codes write exactly the same bytes. For example, the 5 sprite lines become:

```
0611BB8C 00000014
28000030 41820050
5409EEFA 7D69E02E
5D6B0001 00000000
```

| Field | Meaning |
|---|---|
| `pG` | game state structure at `0x8027F7D0` |
| `pG+0x54` bit `0x800` | letterbox mode |
| `pG+0x170` `Stop_flg` | 0 during free play (and on the title screen), non-zero while the game is frozen |
| `pG+0x5018` `Status_flg[0]` | `0x00001000` STA_EVENT (cutscene) |
| `pG+0x5020` `Status_flg[2]` | `0x00008000` STA_TITLE (title screen and its menus) |
| `0x802B3220` `cine_work` | `+0` fade state, `+1` bar alpha, `+2` previous on/off, `+4` fade timer |

## Shared lines

### Hide the HUD bar sprites

| Gecko line | Address | Original | New | What it does |
|---|---|---|---|---|
| `0411BB8C 28000030` | `8011BB8C` | `rlwinm r9, r0, 0x1d, 0x1b, 0x1d` | `cmplwi r0, 0x30` | is this sprite in display group 0x30 (the bar sprites)? |
| `0411BB90 41820050` | `8011BB90` | `clrlwi r0, r0, 0x1b` | `beq 0x8011bbe0` | yes: skip drawing it |
| `0411BB94 5409EEFA` | `8011BB94` | `lwzx r11, r9, r28` | `rlwinm r9, r0, 0x1d, 0x1b, 0x1d` | (moved) word index into the hidden-groups mask = group / 32 |
| `0411BB98 7D69E02E` | `8011BB98` | `srw r0, r27, r0` | `lwzx r11, r9, r28` | (moved) load the hidden-groups mask word |
| `0411BB9C 5D6B0001` | `8011BB9C` | `and. r9, r11, r0` | `rlwnm. r11, r11, r0, 0, 0` | rotate the group bit to the top and test it: replaces the original shift + and, which frees the two slots above |

### Render the full frame underneath

| Gecko line | Address | Original | New | What it does |
|---|---|---|---|---|
| `040FA860 70090000` | `800FA860` | `andi. r9, r0, 0x800` | `andi. r9, r0, 0` | screen effect: letterbox-mode test always false, so the full-frame variant is used |
| `04165E88 700B0000` | `80165E88` | `andi. r11, r0, 0x800` | `andi. r11, r0, 0` | main render loop: never enable the rows 56–392 3D scissor |
| `041789A8 70090000` | `801789A8` | `andi. r9, r0, 0x800` | `andi. r9, r0, 0` | screen effect: letterbox-mode test always false, so the full-frame variant is used |
| `04178DC8 70090000` | `80178DC8` | `andi. r9, r0, 0x800` | `andi. r9, r0, 0` | screen effect projection: full-frame variant (pairs with 801789A8) |
| `0417CADC 70090000` | `8017CADC` | `andi. r9, r0, 0x800` | `andi. r9, r0, 0` | screen effect: letterbox-mode test always false, so the full-frame variant is used |
| `04182FD4 70090000` | `80182FD4` | `andi. r9, r0, 0x800` | `andi. r9, r0, 0` | screen effect: letterbox-mode test always false, so the full-frame variant is used |

### Full-screen fades

| Gecko line | Address | Original | New | What it does |
|---|---|---|---|---|
| `041EBB2C 00000000` | `801EBB2C` | float 56 | float 0 | top offset of the fade-to-black overlay: 56.0 → 0.0, so fades cover the whole screen |

## Preset: no letterbox in gameplay

Bars on = `Stop_flg != 0` OR STA_TITLE.

| Gecko line | Address | Original | New | What it does |
|---|---|---|---|---|
| `04171B40 80090170` | `80171B40` | `li r11, 1` | `lwz r0, 0x170(r9)` | r0 = Stop_flg (pG+0x170) |
| `04171B44 81895020` | `80171B44` | `lwz r0, 0x5018(r9)` | `lwz r12, 0x5020(r9)` | r12 = Status_flg[2] (pG+0x5020) |
| `04171B48 558C8FFE` | `80171B48` | `andis. r9, r0, 0x100` | `rlwinm r12, r12, 0x11, 0x1f, 0x1f` | r12 = STA_TITLE bit (0x00008000) as 0/1 |
| `04171B4C 7C006378` | `80171B4C` | `bne 0x80171b54` | `or r0, r0, r12` | frozen OR title screen |
| `04171B50 3180FFFF` | `80171B50` | `li r11, 0` | `addic r12, r0, -1` | carry = (r0 != 0) |
| `04171B54 7D6C0110` | `80171B54` | `lbz r0, 2(r3)` | `subfe r11, r12, r0` | r11 = carry: 1 = bars, 0 = no bars |
| `04171B58 88030002` | `80171B58` | `extsb r0, r0` | `lbz r0, 2(r3)` | previous on/off load, moved down one slot (extsb dropped: the value is only 0 or 1) |

## Preset: no letterbox in gameplay and cutscenes

Bars on = (`Stop_flg != 0` AND NOT STA_EVENT) OR STA_TITLE. The rest of `cine_polling` is rewritten
more compactly to make room.

| Gecko line | Address | Original | New | What it does |
|---|---|---|---|---|
| `04171B40 80090170` | `80171B40` | `li r11, 1` | `lwz r0, 0x170(r9)` | r0 = Stop_flg (pG+0x170) |
| `04171B44 81895018` | `80171B44` | `lwz r0, 0x5018(r9)` | `lwz r12, 0x5018(r9)` | r12 = Status_flg[0] (pG+0x5018) |
| `04171B48 3140FFFF` | `80171B48` | `andis. r9, r0, 0x100` | `addic r10, r0, -1` | carry = (Stop_flg != 0) |
| `04171B4C 7D6A0110` | `80171B4C` | `bne 0x80171b54` | `subfe r11, r10, r0` | r11 = 1 frozen / 0 free play |
| `04171B50 558CA7FE` | `80171B50` | `li r11, 0` | `rlwinm r12, r12, 0x14, 0x1f, 0x1f` | r12 = STA_EVENT bit (0x00001000) as 0/1 |
| `04171B54 7D6B6078` | `80171B54` | `lbz r0, 2(r3)` | `andc r11, r11, r12` | r11 = frozen AND NOT cutscene |
| `04171B58 81895020` | `80171B58` | `extsb r0, r0` | `lwz r12, 0x5020(r9)` | r12 = Status_flg[2] (pG+0x5020) |
| `04171B5C 558C8FFE` | `80171B5C` | `cmpw r0, r11` | `rlwinm r12, r12, 0x11, 0x1f, 0x1f` | r12 = STA_TITLE bit (0x00008000) as 0/1 |
| `04171B60 7D6B6378` | `80171B60` | `beqlr ` | `or r11, r11, r12` | OR title screen: r11 = bars wanted |
| `04171B64 88030002` | `80171B64` | `cmpwi r11, 0` | `lbz r0, 2(r3)` | r0 = previous on/off |
| `04171B68 7C005800` | `80171B68` | `stb r11, 2(r3)` | `cmpw r0, r11` | changed? |
| `04171B6C 4D820020` | `80171B6C` | `beq 0x80171b88` | `beqlr ` | no: return |
| `04171B70 99630002` | `80171B70` | `lis r9, -0x7fe1` | `stb r11, 2(r3)` | remember the new on/off |
| `04171B74 200B0002` | `80171B74` | `li r0, 1` | `subfic r0, r11, 2` | fade state = 2 - r11 (1 fade in, 2 fade out) |
| `04171B78 3D20801F` | `80171B78` | `lfs f0, -0x17d0(r9)` | `lis r9, -0x7fe1` | r9 = 0x801F0000 (float constants) |
| `04171B7C C009E830` | `80171B7C` | `stb r0, 0(r3)` | `lfs f0, -0x17d0(r9)` | f0 = 15.0 |
| `04171B80 98030000` | `80171B80` | `stfs f0, 4(r3)` | `stb r0, 0(r3)` | store the fade state |
| `04171B84 D0030004` | `80171B84` | `blr ` | `stfs f0, 4(r3)` | fade timer = 15 frames |
| `04171B88 4E800020` | `80171B88` | `lis r9, -0x7fe1` | `blr ` | return |

## Preset: no letterbox anywhere

| Gecko line | Address | Original | New | What it does |
|---|---|---|---|---|
| `04171B4C 60000000` | `80171B4C` | `bne 0x80171b54` | `nop ` | the "bars on" branch is never taken, so li r11, 0 always runs and the bars are never requested |

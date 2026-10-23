# Code reference

Every line of the Gecko codes. These are also every word the patcher and the xdelta patches change in
`main.dol`. A Gecko line `04XXXXXX YYYYYYYY` means "write the 32-bit value `YYYYYYYY` to address
`0x80XXXXXX`", the game's code and data in RAM. Disassembly is PowerPC (Gekko).

Each preset = the **shared lines** + the **preset lines**.

## Background

The game state structure `pG` is at `0x8027F7D0`.

| Field | Meaning |
|---|---|
| `pG+0x54` bit `0x800` | letterbox mode: restricts the 3D render to rows 56–392 and picks strip-only screen effects |
| `pG+0x170` `Stop_flg` | 0 during free play, all bits set when the game is frozen (pause/options menu, inventory/map/files/shop, cutscenes, movies) |
| `pG+0x5018` `Status_flg[0]` | `0x01000000` STA_CINESCO (letterbox requested), `0x00001000` STA_EVENT (cutscene) |

The bars themselves are drawn by `Draw_cinesco` (`0x80171C64`). It draws two black quads with
the alpha in `cine_work` (`0x802B3220`). Its controller `cine_polling` (`0x80171B3C`) decides once
per frame whether the bars should be on. When that decision changes, it starts a 15-frame fade.
The presets only change that one decision. `Draw_cinesco` and the fade routines are untouched.

Original `cine_polling` (decision part):

```
80171B3C  lwz    r9, -0x7500(r13)   ; r9 = pG
80171B40  li     r11, 1             ; want bars = 1
80171B44  lwz    r0, 0x5018(r9)     ; r0 = Status_flg[0]
80171B48  andis. r9, r0, 0x100      ; STA_CINESCO set?
80171B4C  bne    +8                 ; yes: keep 1
80171B50  li     r11, 0             ; no: want bars = 0
80171B54  lbz    r0, 2(r3)          ; previous on/off ...
80171B58  extsb  r0, r0
80171B5C  cmpw   r0, r11            ; changed? then start the 15-frame fade in/out
```

## Shared lines (all presets)

### Hide the HUD bar sprites

The game draws a second pair of black bars as HUD sprites (`IDC_CINESCO`, display group `0x30`). The
HUD drawing loop at `0x8011BB2C` is compacted so that it can also skip group `0x30`.

| Gecko line | Address | Original | New | What it does |
|---|---|---|---|---|
| `0411BB8C 28000030` | `8011BB8C` | `rlwinm r9, r0, 0x1d, 0x1b, 0x1d` | `cmplwi r0, 0x30` | is this HUD object in display group 0x30 (the bar sprites)? |
| `0411BB90 41820050` | `8011BB90` | `clrlwi r0, r0, 0x1b` | `beq 0x8011bbe0` | yes: skip drawing it |
| `0411BB94 5409EEFA` | `8011BB94` | `lwzx r11, r9, r28` | `rlwinm r9, r0, 0x1d, 0x1b, 0x1d` | (moved) word index into the hidden-groups mask = group / 32 |
| `0411BB98 7D69E02E` | `8011BB98` | `srw r0, r27, r0` | `lwzx r11, r9, r28` | (moved) load the hidden-groups mask word |
| `0411BB9C 5D6B0001` | `8011BB9C` | `and. r9, r11, r0` | `rlwnm. r11, r11, r0, 0, 0` | rotate the group bit to the top and test it: replaces the original shift + and, which frees the two slots used above |

### Render the full frame underneath

Each line changes `andi. rX, r0, 0x800` (test the letterbox-mode flag) to `andi. rX, r0, 0`
(always false), so the game takes its own full-frame path.

| Gecko line | Address | Original | New | What it does |
|---|---|---|---|---|
| `040FA860 70090000` | `800FA860` | `andi. r9, r0, 0x800` | `andi. r9, r0, 0` | screen effect: letterbox-mode test always false, so the full-frame variant is used |
| `04165E88 700B0000` | `80165E88` | `andi. r11, r0, 0x800` | `andi. r11, r0, 0` | main render loop: never enable the rows 56–392 3D scissor |
| `041789A8 70090000` | `801789A8` | `andi. r9, r0, 0x800` | `andi. r9, r0, 0` | screen effect: letterbox-mode test always false, so the full-frame variant is used |
| `04178DC8 70090000` | `80178DC8` | `andi. r9, r0, 0x800` | `andi. r9, r0, 0` | screen effect projection: full-frame variant |
| `0417CADC 70090000` | `8017CADC` | `andi. r9, r0, 0x800` | `andi. r9, r0, 0` | screen effect: letterbox-mode test always false, so the full-frame variant is used |
| `04182FD4 70090000` | `80182FD4` | `andi. r9, r0, 0x800` | `andi. r9, r0, 0` | screen effect: letterbox-mode test always false, so the full-frame variant is used |

### Full-screen fades

| Gecko line | Address | Original | New | What it does |
|---|---|---|---|---|
| `041EBB2C 00000000` | `801EBB2C` | float 56 | float 0 | top offset of the fade-to-black overlay: 56.0 → 0.0, so fades cover the whole screen |

## Preset: no letterbox in gameplay

Bars in menus, inventory, cutscenes and movies.

| Gecko line | Address | Original | New | What it does |
|---|---|---|---|---|
| `04171B44 80090170` | `80171B44` | `lwz r0, 0x5018(r9)` | `lwz r0, 0x170(r9)` | read Stop_flg (pG+0x170) instead of Status_flg[0] (pG+0x5018) |
| `04171B48 2C000000` | `80171B48` | `andis. r9, r0, 0x100` | `cmpwi r0, 0` | bars on when Stop_flg != 0 (game frozen) instead of when the STA_CINESCO bit is set |

## Preset: no letterbox in gameplay and cutscenes

Bars in menus, inventory and movies. Rewrites the decision part shown above:
"bars on" = `Stop_flg != 0` AND NOT STA_EVENT.

| Gecko line | Address | Original | New | What it does |
|---|---|---|---|---|
| `04171B40 80090170` | `80171B40` | `li r11, 1` | `lwz r0, 0x170(r9)` | r0 = Stop_flg (pG+0x170) |
| `04171B44 81295018` | `80171B44` | `lwz r0, 0x5018(r9)` | `lwz r9, 0x5018(r9)` | r9 = Status_flg[0] (pG+0x5018) |
| `04171B48 3180FFFF` | `80171B48` | `andis. r9, r0, 0x100` | `addic r12, r0, -1` | r12 = Stop_flg - 1; sets carry when Stop_flg != 0 |
| `04171B4C 7D6C0110` | `80171B4C` | `bne 0x80171b54` | `subfe r11, r12, r0` | r11 = carry = (Stop_flg != 0) |
| `04171B50 5529A7FE` | `80171B50` | `li r11, 0` | `rlwinm r9, r9, 0x14, 0x1f, 0x1f` | r9 = STA_EVENT bit (0x00001000) as 0/1 |
| `04171B54 7D6B4878` | `80171B54` | `lbz r0, 2(r3)` | `andc r11, r11, r9` | r11 = frozen AND NOT cutscene → bars on/off |
| `04171B58 88030002` | `80171B58` | `extsb r0, r0` | `lbz r0, 2(r3)` | load the previous on/off state (the sign extension after it is no longer needed: the value is only ever 0 or 1) |

## Preset: no letterbox anywhere

| Gecko line | Address | Original | New | What it does |
|---|---|---|---|---|
| `04171B4C 60000000` | `80171B4C` | `bne 0x80171b54` | `nop ` | remove the branch that keeps the bars on, so the request is always "off" |

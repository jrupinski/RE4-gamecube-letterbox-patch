# Code reference

Every line of the Gecko codes, which is also every word the patcher and the xdelta patches change in
`main.dol`. A Gecko line `04XXXXXX YYYYYYYY` means "write the 32-bit value `YYYYYYYY` to address
`0x80XXXXXX`" (the game's code and data in RAM). Disassembly is PowerPC (Gekko).

The game state structure (`pG`) is at `0x8027F7D0`. Fields used:

| Offset | Field | Meaning |
|---|---|---|
| `+0x54` (bit `0x800`) | letterbox mode | restricts the 3D render to rows 56–392 and picks strip-only effect variants |
| `+0x170` | `Stop_flg` | 0 during free play, non-zero when the game is frozen (menus, inventory, cutscenes, movies) |
| `+0x5018` | `Status_flg[0]` | `0x00040000` sub screen (inventory/map/files/shop), `0x00001000` event (cutscene), `0x10000000`/`0x04000000` movie |

`cine_work` (`0x802B3220`): `+0` state (0 idle, 1 fade in, 2 fade out), `+1` bar alpha, `+2` previous on/off, `+4` fade timer.
`Draw_cinesco` (`0x80171C64`, unchanged) draws the black bars with `cine_work.alpha`, and nothing when alpha is 0.

### Core 1: hide the HUD bar sprites

| Gecko line | Address | Original | New | What it does |
|---|---|---|---|---|
| `0411BB8C 28000030` | `8011BB8C` | `rlwinm r9, r0, 0x1d, 0x1b, 0x1d` | `cmplwi r0, 0x30` | is this HUD object in display group 0x30 (the bar sprites)? |
| `0411BB90 41820050` | `8011BB90` | `clrlwi r0, r0, 0x1b` | `beq 0x8011bbe0` | yes: skip drawing it |
| `0411BB94 5409EEFA` | `8011BB94` | `lwzx r11, r9, r28` | `rlwinm r9, r0, 0x1d, 0x1b, 0x1d` | original group-mask check: word index = group/32 |
| `0411BB98 7D69E02E` | `8011BB98` | `srw r0, r27, r0` | `lwzx r11, r9, r28` | load the hidden-groups mask word |
| `0411BB9C 5D6B0001` | `8011BB9C` | `and. r9, r11, r0` | `rlwnm. r11, r11, r0, 0, 0` | rotate the group bit to the top and test it (replaces srw+and., frees two slots) |

### Core 2: render the full frame (letterbox-mode checks)

| Gecko line | Address | Original | New | What it does |
|---|---|---|---|---|
| `040FA860 70090000` | `800FA860` | `andi. r9, r0, 0x800` | `andi. r9, r0, 0` | effect: letterbox-mode test always false -> full-frame variant |
| `04165E88 700B0000` | `80165E88` | `andi. r11, r0, 0x800` | `andi. r11, r0, 0` | main render loop: never switch on the 56..392 3D scissor |
| `041789A8 70090000` | `801789A8` | `andi. r9, r0, 0x800` | `andi. r9, r0, 0` | effect: letterbox-mode test always false -> full-frame variant |
| `04178DC8 70090000` | `80178DC8` | `andi. r9, r0, 0x800` | `andi. r9, r0, 0` | effect projection: full-frame variant |
| `0417CADC 70090000` | `8017CADC` | `andi. r9, r0, 0x800` | `andi. r9, r0, 0` | effect: letterbox-mode test always false -> full-frame variant |
| `04182FD4 70090000` | `80182FD4` | `andi. r9, r0, 0x800` | `andi. r9, r0, 0` | effect: letterbox-mode test always false -> full-frame variant |

### Core 3: full-screen fades

| Gecko line | Address | Original | New | What it does |
|---|---|---|---|---|
| `041EBB2C 00000000` | `801EBB2C` | float 56 | float 0 | fade overlay top offset 56.0 -> 0.0 (fades cover the whole screen) |

### Core 4: replacement letterbox controller (game/cinesco.cpp)

| Gecko line | Address | Original | New | What it does |
|---|---|---|---|---|
| `04171B3C 9421FFF0` | `80171B3C` | `lwz r9, -0x7500(r13)` | `stwu r1, -0x10(r1)` | fade routine (shared by fade-in/out): stack frame |
| `04171B40 3D20801F` | `80171B40` | `li r11, 1` | `lis r9, -0x7fe1` | r9 = 0x801F0000 (float constants) |
| `04171B44 C1A30004` | `80171B44` | `lwz r0, 0x5018(r9)` | `lfs f13, 4(r3)` | f13 = timer |
| `04171B48 C009E834` | `80171B48` | `andis. r9, r0, 0x100` | `lfs f0, -0x17cc(r9)` | f0 = 1.0 |
| `04171B4C EDAD0028` | `80171B4C` | `bne 0x80171b54` | `fsubs f13, f13, f0` | timer -= 1 |
| `04171B50 D1A30004` | `80171B50` | `li r11, 0` | `stfs f13, 4(r3)` | store timer |
| `04171B54 C189E838` | `80171B54` | `lbz r0, 2(r3)` | `lfs f12, -0x17c8(r9)` | f12 = 15.0 |
| `04171B58 88030000` | `80171B58` | `extsb r0, r0` | `lbz r0, 0(r3)` | r0 = state (1 fade-in, 2 fade-out) |
| `04171B5C FC006890` | `80171B5C` | `cmpw r0, r11` | `fmr f0, f13` | f0 = timer |
| `04171B60 2C000001` | `80171B60` | `beqlr ` | `cmpwi r0, 1` | fading in? |
| `04171B64 40820008` | `80171B64` | `cmpwi r11, 0` | `bne 0x80171b6c` | no: keep f0 = timer |
| `04171B68 EC0C6828` | `80171B68` | `stb r11, 2(r3)` | `fsubs f0, f12, f13` | yes: f0 = 15 - timer |
| `04171B6C EC006024` | `80171B6C` | `beq 0x80171b88` | `fdivs f0, f0, f12` | f0 /= 15 |
| `04171B70 C169E83C` | `80171B70` | `lis r9, -0x7fe1` | `lfs f11, -0x17c4(r9)` | f11 = 255.0 |
| `04171B74 EC0002F2` | `80171B74` | `li r0, 1` | `fmuls f0, f0, f11` | f0 *= 255 (alpha) |
| `04171B78 FC00001E` | `80171B78` | `lfs f0, -0x17d0(r9)` | `fctiwz f0, f0` | convert to integer |
| `04171B7C D8010008` | `80171B7C` | `stb r0, 0(r3)` | `stfd f0, 8(r1)` | spill to stack |
| `04171B80 8801000F` | `80171B80` | `stfs f0, 4(r3)` | `lbz r0, 0xf(r1)` | low byte = alpha |
| `04171B84 98030001` | `80171B84` | `blr ` | `stb r0, 1(r3)` | cine_work.alpha = alpha |
| `04171B88 C169E840` | `80171B88` | `lis r9, -0x7fe1` | `lfs f11, -0x17c0(r9)` | f11 = 0.0 |
| `04171B8C FC0D5800` | `80171B8C` | `li r0, 2` | `fcmpu cr0, f13, f11` | timer > 0? |
| `04171B90 4181000C` | `80171B90` | `b 0x80171b78` | `bgt 0x80171b9c` | yes: still fading |
| `04171B94 38000000` | `80171B94` | `stwu r1, -0x10(r1)` | `li r0, 0` | no: state = 0 (idle) |
| `04171B98 98030000` | `80171B98` | `lis r9, -0x7fe1` | `stb r0, 0(r3)` | store state |
| `04171B9C 38210010` | `80171B9C` | `lfs f13, 4(r3)` | `addi r1, r1, 0x10` | pop stack frame |
| `04171BA0 4E800020` | `80171BA0` | `lfs f0, -0x17cc(r9)` | `blr ` | return |
| `04171BA4 812D8B00` | `80171BA4` | `lis r11, -0x7fe1` | `lwz r9, -0x7500(r13)` | decide routine: r9 = game state (pG) |
| `04171BA8 3D408017` | `80171BA8` | `lfs f12, -0x17c8(r11)` | `lis r10, -0x7fe9` | r10 = 0x80170000 (option slots) |
| `04171BAC 81890170` | `80171BAC` | `lis r9, -0x7fe1` | `lwz r12, 0x170(r9)` | r12 = Stop_flg (pG+0x170): 0 during free play |
| `04171BB0 816A1C40` | `80171BB0` | `fsubs f13, f13, f0` | `lwz r11, 0x1c40(r10)` | r11 = gameplay slot (80171C40) |
| `04171BB4 2C0C0000` | `80171BB4` | `lfs f10, -0x17c4(r9)` | `cmpwi r12, 0` | free play? |
| `04171BB8 41820030` | `80171BB8` | `fsubs f0, f12, f13` | `beq 0x80171be8` | yes: use gameplay slot |
| `04171BBC 80095018` | `80171BBC` | `fdivs f0, f0, f12` | `lwz r0, 0x5018(r9)` | r0 = Status_flg[0] (pG+0x5018) |
| `04171BC0 816A1C44` | `80171BC0` | `lis r9, -0x7fe1` | `lwz r11, 0x1c44(r10)` | frozen, default context: pause/options menu slot (80171C44) |
| `04171BC4 740C0004` | `80171BC4` | `lfs f11, -0x17c0(r9)` | `andis. r12, r0, 4` | STA_SUB_SCRN (0x00040000) set? |
| `04171BC8 41820008` | `80171BC8` | `stfs f13, 4(r3)` | `beq 0x80171bd0` | no: skip |
| `04171BCC 816A1C48` | `80171BCC` | `fmuls f0, f0, f10` | `lwz r11, 0x1c48(r10)` | yes: inventory/map/files/shop slot (80171C48) |
| `04171BD0 700C1000` | `80171BD0` | `xsmaddasp f0, f1, f20` | `andi. r12, r0, 0x1000` | STA_EVENT (0x00001000) set? |
| `04171BD4 41820008` | `80171BD4` | `fcmpu cr0, f13, f11` | `beq 0x80171bdc` | no: skip |
| `04171BD8 816A1C4C` | `80171BD8` | `lbz r0, 8(r1)` | `lwz r11, 0x1c4c(r10)` | yes: cutscene slot (80171C4C) |
| `04171BDC 740C1400` | `80171BDC` | `stb r0, 1(r3)` | `andis. r12, r0, 0x1400` | STA_MOVIE_ON/MOVIE2_ON (0x14000000) set? |
| `04171BE0 41820008` | `80171BE0` | `cror cr0un, cr0eq, cr0lt` | `beq 0x80171be8` | no: done |
| `04171BE4 816A1C50` | `80171BE4` | `bns 0x80171bf8` | `lwz r11, 0x1c50(r10)` | yes: movie slot (80171C50) |
| `04171BE8 2C0B0000` | `80171BE8` | `li r9, 0` | `cmpwi r11, 0` | slot value zero? |
| `04171BEC 39600000` | `80171BEC` | `li r0, 0xff` | `li r11, 0` | want = 0 (no bars) |
| `04171BF0 41820008` | `80171BF0` | `stb r0, 1(r3)` | `beq 0x80171bf8` | slot zero: keep want = 0 |
| `04171BF4 39600001` | `80171BF4` | `stb r9, 0(r3)` | `li r11, 1` | slot non-zero: want = 1 (bars) |
| `04171BF8 88030002` | `80171BF8` | `addi r1, r1, 0x10` | `lbz r0, 2(r3)` | r0 = cine_work.old_flag |
| `04171BFC 7C005800` | `80171BFC` | `blr ` | `cmpw r0, r11` | changed since last frame? |
| `04171C00 4D820020` | `80171C00` | `stwu r1, -0x10(r1)` | `beqlr ` | no: return |
| `04171C04 99630002` | `80171C04` | `lis r9, -0x7fe1` | `stb r11, 2(r3)` | old_flag = want |
| `04171C08 38000002` | `80171C08` | `lfs f13, 4(r3)` | `li r0, 2` | state = 2 (fade out) |
| `04171C0C 2C0B0000` | `80171C0C` | `lfs f12, -0x17bc(r9)` | `cmpwi r11, 0` | want bars? |
| `04171C10 41820008` | `80171C10` | `lis r11, -0x7fe1` | `beq 0x80171c18` | no: keep fade out |
| `04171C14 38000001` | `80171C14` | `lfs f0, -0x17b8(r11)` | `li r0, 1` | yes: state = 1 (fade in) |
| `04171C18 98030000` | `80171C18` | `lis r9, -0x7fe1` | `stb r0, 0(r3)` | store state |
| `04171C1C 3D20801F` | `80171C1C` | `fsubs f13, f13, f12` | `lis r9, -0x7fe1` | r9 = 0x801F0000 |
| `04171C20 C009E830` | `80171C20` | `lfs f11, -0x17b4(r9)` | `lfs f0, -0x17d0(r9)` | f0 = 15.0 |
| `04171C24 D0030004` | `80171C24` | `fdivs f0, f13, f0` | `stfs f0, 4(r3)` | timer = 15 frames |
| `04171C28 4E800020` | `80171C28` | `lis r9, -0x7fe1` | `blr ` | return |
| `0420CE60 80171BA4` | `8020CE60` | pointer 0x80171B3C | pointer 0x80171BA4 | cine_tbl[0] (idle/poll) -> decide routine |
| `0420CE64 80171B3C` | `8020CE64` | pointer 0x80171B94 | pointer 0x80171B3C | cine_tbl[1] (fade in) -> fade routine |
| `0420CE68 80171B3C` | `8020CE68` | pointer 0x80171C00 | pointer 0x80171B3C | cine_tbl[2] (fade out) -> fade routine |

### Option: remove in gameplay

| Gecko line | Address | Original | New | What it does |
|---|---|---|---|---|
| `04171C40 00000000` | `80171C40` | (old code, not executed any more) | `0x00000000` | gameplay slot: 0 = remove bars |

### Option: remove in pause/options menu

| Gecko line | Address | Original | New | What it does |
|---|---|---|---|---|
| `04171C44 00000000` | `80171C44` | (old code, not executed any more) | `0x00000000` | pause/options menu slot |

### Option: remove in inventory/map/files/shop

| Gecko line | Address | Original | New | What it does |
|---|---|---|---|---|
| `04171C48 00000000` | `80171C48` | (old code, not executed any more) | `0x00000000` | inventory/map/files/shop slot |

### Option: remove in cutscenes

| Gecko line | Address | Original | New | What it does |
|---|---|---|---|---|
| `04171C4C 00000000` | `80171C4C` | (old code, not executed any more) | `0x00000000` | cutscene slot |

### Option: remove in movies

| Gecko line | Address | Original | New | What it does |
|---|---|---|---|---|
| `04171C50 00000000` | `80171C50` | (old code, not executed any more) | `0x00000000` | movie slot |

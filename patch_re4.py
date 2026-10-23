#!/usr/bin/env python3
"""Resident Evil 4 (GameCube, USA G4BE08) letterbox removal patcher.

Patches main.dol inside a plain ISO of Disc 1 or Disc 2 IN PLACE (work on a copy).
Python 3 standard library only. Choose one preset:

  gameplay   bars removed in gameplay (kept in menus, inventory, cutscenes, movies)
  cutscenes  bars removed in gameplay and cutscenes (kept in menus, inventory, movies)
  all        bars removed everywhere

  python3 patch_re4.py "RE4 Disc 1.iso" gameplay
"""
import json, struct, sys

PATCHES = json.loads(r'''{
 "shared": [
  {
   "addr": "8011BB8C",
   "orig": "5409EEFA",
   "new": "28000030"
  },
  {
   "addr": "8011BB90",
   "orig": "540006FE",
   "new": "41820050"
  },
  {
   "addr": "8011BB94",
   "orig": "7D69E02E",
   "new": "5409EEFA"
  },
  {
   "addr": "8011BB98",
   "orig": "7F600430",
   "new": "7D69E02E"
  },
  {
   "addr": "8011BB9C",
   "orig": "7D690039",
   "new": "5D6B0001"
  },
  {
   "addr": "800FA860",
   "orig": "70090800",
   "new": "70090000"
  },
  {
   "addr": "80165E88",
   "orig": "700B0800",
   "new": "700B0000"
  },
  {
   "addr": "801789A8",
   "orig": "70090800",
   "new": "70090000"
  },
  {
   "addr": "80178DC8",
   "orig": "70090800",
   "new": "70090000"
  },
  {
   "addr": "8017CADC",
   "orig": "70090800",
   "new": "70090000"
  },
  {
   "addr": "80182FD4",
   "orig": "70090800",
   "new": "70090000"
  },
  {
   "addr": "801EBB2C",
   "orig": "42600000",
   "new": "00000000"
  }
 ],
 "frozen": [
  {
   "addr": "80171B44",
   "orig": "80095018",
   "new": "80090170"
  },
  {
   "addr": "80171B48",
   "orig": "74090100",
   "new": "2C000000"
  }
 ],
 "frozen_nocut": [
  {
   "addr": "80171B40",
   "orig": "39600001",
   "new": "80090170"
  },
  {
   "addr": "80171B44",
   "orig": "80095018",
   "new": "81295018"
  },
  {
   "addr": "80171B48",
   "orig": "74090100",
   "new": "3180FFFF"
  },
  {
   "addr": "80171B4C",
   "orig": "40820008",
   "new": "7D6C0110"
  },
  {
   "addr": "80171B50",
   "orig": "39600000",
   "new": "5529A7FE"
  },
  {
   "addr": "80171B54",
   "orig": "88030002",
   "new": "7D6B4878"
  },
  {
   "addr": "80171B58",
   "orig": "7C000774",
   "new": "88030002"
  }
 ],
 "never": [
  {
   "addr": "80171B4C",
   "orig": "40820008",
   "new": "60000000"
  }
 ]
}''')
PRESETS = {"gameplay": "frozen", "cutscenes": "frozen_nocut", "all": "never"}

def main():
    if len(sys.argv) != 3 or sys.argv[2] not in PRESETS:
        sys.exit(__doc__)
    iso, preset = sys.argv[1], sys.argv[2]
    with open(iso, "r+b") as f:
        f.seek(0); gid = f.read(6)
        if gid != b"G4BE08":
            sys.exit("not Resident Evil 4 USA (G4BE08): game id %r" % gid)
        f.seek(0x420); dol = struct.unpack(">I", f.read(4))[0]
        f.seek(dol); h = f.read(0xE0)
        offs = struct.unpack(">18I", h[0:0x48]); addrs = struct.unpack(">18I", h[0x48:0x90]); sizes = struct.unpack(">18I", h[0x90:0xD8])
        def foff(addr):
            for o, b, s in zip(offs, addrs, sizes):
                if s and b <= addr < b + s:
                    return dol + o + addr - b
            sys.exit("address %08X not in main.dol" % addr)
        todo = []
        for p in PATCHES["shared"] + PATCHES[PRESETS[preset]]:
            addr = int(p["addr"], 16); pos = foff(addr)
            f.seek(pos); cur = f.read(4).hex().upper()
            if cur != p["orig"]:
                sys.exit("unexpected data at %08X (%s): ISO already patched or wrong revision. Start from a clean ISO." % (addr, cur))
            todo.append((pos, bytes.fromhex(p["new"])))
        for pos, val in todo:
            f.seek(pos); f.write(val)
    print("patched %d words (preset: %s)" % (len(todo), preset))

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Resident Evil 4 (GameCube, USA G4BE08) letterbox removal patcher.

Patches main.dol inside a plain ISO of Disc 1 or Disc 2 in place (make a copy first).
Python 3 standard library only.

  python3 patch_re4.py GAME.iso --gameplay                     # bars only off during gameplay
  python3 patch_re4.py GAME.iso --all                          # no bars anywhere
  python3 patch_re4.py GAME.iso --gameplay --subscreen --movie # any combination
"""
import argparse, json, struct, sys

PATCHES = json.loads(r'''{
 "core_sprites": [
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
  }
 ],
 "core_fullframe": [
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
  }
 ],
 "core_fade": [
  {
   "addr": "801EBB2C",
   "orig": "42600000",
   "new": "00000000"
  }
 ],
 "core_cine": [
  {
   "addr": "80171B3C",
   "orig": "812D8B00",
   "new": "9421FFF0"
  },
  {
   "addr": "80171B40",
   "orig": "39600001",
   "new": "3D20801F"
  },
  {
   "addr": "80171B44",
   "orig": "80095018",
   "new": "C1A30004"
  },
  {
   "addr": "80171B48",
   "orig": "74090100",
   "new": "C009E834"
  },
  {
   "addr": "80171B4C",
   "orig": "40820008",
   "new": "EDAD0028"
  },
  {
   "addr": "80171B50",
   "orig": "39600000",
   "new": "D1A30004"
  },
  {
   "addr": "80171B54",
   "orig": "88030002",
   "new": "C189E838"
  },
  {
   "addr": "80171B58",
   "orig": "7C000774",
   "new": "88030000"
  },
  {
   "addr": "80171B5C",
   "orig": "7C005800",
   "new": "FC006890"
  },
  {
   "addr": "80171B60",
   "orig": "4D820020",
   "new": "2C000001"
  },
  {
   "addr": "80171B64",
   "orig": "2C0B0000",
   "new": "40820008"
  },
  {
   "addr": "80171B68",
   "orig": "99630002",
   "new": "EC0C6828"
  },
  {
   "addr": "80171B6C",
   "orig": "4182001C",
   "new": "EC006024"
  },
  {
   "addr": "80171B70",
   "orig": "3D20801F",
   "new": "C169E83C"
  },
  {
   "addr": "80171B74",
   "orig": "38000001",
   "new": "EC0002F2"
  },
  {
   "addr": "80171B78",
   "orig": "C009E830",
   "new": "FC00001E"
  },
  {
   "addr": "80171B7C",
   "orig": "98030000",
   "new": "D8010008"
  },
  {
   "addr": "80171B80",
   "orig": "D0030004",
   "new": "8801000F"
  },
  {
   "addr": "80171B84",
   "orig": "4E800020",
   "new": "98030001"
  },
  {
   "addr": "80171B88",
   "orig": "3D20801F",
   "new": "C169E840"
  },
  {
   "addr": "80171B8C",
   "orig": "38000002",
   "new": "FC0D5800"
  },
  {
   "addr": "80171B90",
   "orig": "4BFFFFE8",
   "new": "4181000C"
  },
  {
   "addr": "80171B94",
   "orig": "9421FFF0",
   "new": "38000000"
  },
  {
   "addr": "80171B98",
   "orig": "3D20801F",
   "new": "98030000"
  },
  {
   "addr": "80171B9C",
   "orig": "C1A30004",
   "new": "38210010"
  },
  {
   "addr": "80171BA0",
   "orig": "C009E834",
   "new": "4E800020"
  },
  {
   "addr": "80171BA4",
   "orig": "3D60801F",
   "new": "812D8B00"
  },
  {
   "addr": "80171BA8",
   "orig": "C18BE838",
   "new": "3D408017"
  },
  {
   "addr": "80171BAC",
   "orig": "3D20801F",
   "new": "81890170"
  },
  {
   "addr": "80171BB0",
   "orig": "EDAD0028",
   "new": "816A1C40"
  },
  {
   "addr": "80171BB4",
   "orig": "C149E83C",
   "new": "2C0C0000"
  },
  {
   "addr": "80171BB8",
   "orig": "EC0C6828",
   "new": "41820030"
  },
  {
   "addr": "80171BBC",
   "orig": "EC006024",
   "new": "80095018"
  },
  {
   "addr": "80171BC0",
   "orig": "3D20801F",
   "new": "816A1C44"
  },
  {
   "addr": "80171BC4",
   "orig": "C169E840",
   "new": "740C0004"
  },
  {
   "addr": "80171BC8",
   "orig": "D1A30004",
   "new": "41820008"
  },
  {
   "addr": "80171BCC",
   "orig": "EC0002B2",
   "new": "816A1C48"
  },
  {
   "addr": "80171BD0",
   "orig": "F001A008",
   "new": "700C1000"
  },
  {
   "addr": "80171BD4",
   "orig": "FC0D5800",
   "new": "41820008"
  },
  {
   "addr": "80171BD8",
   "orig": "88010008",
   "new": "816A1C4C"
  },
  {
   "addr": "80171BDC",
   "orig": "98030001",
   "new": "740C1400"
  },
  {
   "addr": "80171BE0",
   "orig": "4C620382",
   "new": "41820008"
  },
  {
   "addr": "80171BE4",
   "orig": "40830014",
   "new": "816A1C50"
  },
  {
   "addr": "80171BE8",
   "orig": "39200000",
   "new": "2C0B0000"
  },
  {
   "addr": "80171BEC",
   "orig": "380000FF",
   "new": "39600000"
  },
  {
   "addr": "80171BF0",
   "orig": "98030001",
   "new": "41820008"
  },
  {
   "addr": "80171BF4",
   "orig": "99230000",
   "new": "39600001"
  },
  {
   "addr": "80171BF8",
   "orig": "38210010",
   "new": "88030002"
  },
  {
   "addr": "80171BFC",
   "orig": "4E800020",
   "new": "7C005800"
  },
  {
   "addr": "80171C00",
   "orig": "9421FFF0",
   "new": "4D820020"
  },
  {
   "addr": "80171C04",
   "orig": "3D20801F",
   "new": "99630002"
  },
  {
   "addr": "80171C08",
   "orig": "C1A30004",
   "new": "38000002"
  },
  {
   "addr": "80171C0C",
   "orig": "C189E844",
   "new": "2C0B0000"
  },
  {
   "addr": "80171C10",
   "orig": "3D60801F",
   "new": "41820008"
  },
  {
   "addr": "80171C14",
   "orig": "C00BE848",
   "new": "38000001"
  },
  {
   "addr": "80171C18",
   "orig": "3D20801F",
   "new": "98030000"
  },
  {
   "addr": "80171C1C",
   "orig": "EDAD6028",
   "new": "3D20801F"
  },
  {
   "addr": "80171C20",
   "orig": "C169E84C",
   "new": "C009E830"
  },
  {
   "addr": "80171C24",
   "orig": "EC0D0024",
   "new": "D0030004"
  },
  {
   "addr": "80171C28",
   "orig": "3D20801F",
   "new": "4E800020"
  },
  {
   "addr": "8020CE60",
   "orig": "80171B3C",
   "new": "80171BA4"
  },
  {
   "addr": "8020CE64",
   "orig": "80171B94",
   "new": "80171B3C"
  },
  {
   "addr": "8020CE68",
   "orig": "80171C00",
   "new": "80171B3C"
  }
 ],
 "opt_gameplay": [
  {
   "addr": "80171C40",
   "orig": "88010008",
   "new": "00000000"
  }
 ],
 "opt_menu": [
  {
   "addr": "80171C44",
   "orig": "98030001",
   "new": "00000000"
  }
 ],
 "opt_subscreen": [
  {
   "addr": "80171C48",
   "orig": "4C620382",
   "new": "00000000"
  }
 ],
 "opt_cutscene": [
  {
   "addr": "80171C4C",
   "orig": "40830010",
   "new": "00000000"
  }
 ],
 "opt_movie": [
  {
   "addr": "80171C50",
   "orig": "38000000",
   "new": "00000000"
  }
 ]
}''')
OPTIONS = ["gameplay", "menu", "subscreen", "cutscene", "movie"]

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("iso", help="plain .iso of Resident Evil 4 (USA) Disc 1 or 2 - patched IN PLACE")
    ap.add_argument("--all", action="store_true", help="remove the bars in every context")
    help_txt = {"gameplay": "normal play", "menu": "pause/options menu", "subscreen": "inventory, map, files, shop",
                "cutscene": "in-engine cutscenes", "movie": "pre-rendered movies"}
    for o in OPTIONS:
        ap.add_argument("--" + o, action="store_true", help="remove the bars in: " + help_txt[o])
    a = ap.parse_args()
    chosen = OPTIONS if a.all else [o for o in OPTIONS if getattr(a, o)]
    if not chosen:
        ap.error("choose at least one context (or --all)")
    groups = ["core_sprites", "core_fullframe", "core_fade", "core_cine"] + ["opt_" + o for o in chosen]
    with open(a.iso, "r+b") as f:
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
            sys.exit("address %08X not in main.dol" %addr)
        todo = []
        for g in groups:
            for p in PATCHES[g]:
                addr = int(p["addr"], 16); pos = foff(addr)
                f.seek(pos); cur = f.read(4).hex().upper()
                if cur == p["new"]:
                    continue
                if cur != p["orig"]:
                    sys.exit("unexpected data at %08X (%s): already patched with other options, or wrong revision. Start from a clean ISO." % (addr, cur))
                todo.append((pos, bytes.fromhex(p["new"])))
        for pos, val in todo:
            f.seek(pos); f.write(val)
    print("patched %d words; letterbox removed in: %s" % (len(todo), ", ".join(chosen)))

if __name__ == "__main__":
    main()

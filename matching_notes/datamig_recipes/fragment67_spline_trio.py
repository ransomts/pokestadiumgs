# Blob/static migration for the spline trio (fragment67, wave-5 park).
#
# func_8290E040/E0FC/E1D8 (Battle_ComputeSplineWeightsVariantA/B/C) score 0
# only with true function statics; their 9 static words live at
# [0x8291BC14, 0x8291BC44) (orphan bss) and their float literals at
# [0x82917730, 0x82917740) inside the 353F80 rodata blob. Recipe verified
# at .o level by the wave-5 agent:
#  - the C statics become a NOLOAD section at the fixed address (via
#    aliases.ld, which survives extract; the generated ld is rewritten);
#    IDO mangles them to D_8291BC14:1-style globals in the .o's .bss
#  - the 16 bytes of literals replace blob part [0x354230, 0x354240):
#    0x354230 is 16-aligned so SUBALIGN(16) holds
#  - tail padding BC38-BC44 overlaps D_8291BC38-44 absolutes used by
#    fragment67_34B0F0 - harmless (statics end at BC34)

RECIPE = {
    "name": "fragment67_spline_trio",
    "steps": [
        {
            "op": "splice",
            "spool": "func_8290E040",
            "file": "src/fragments/67/fragment67_34AB40.c",
            "func": "func_8290E040",
        },
        {
            "op": "splice",
            "spool": "func_8290E0FC",
            "file": "src/fragments/67/fragment67_34AB40.c",
            "func": "func_8290E0FC",
        },
        {
            "op": "splice",
            "spool": "func_8290E1D8",
            "file": "src/fragments/67/fragment67_34AB40.c",
            "func": "func_8290E1D8",
        },
        {
            "op": "yaml",
            "find": "- [0x353F80, rodata]",
            "insert_after": [
                "- [0x354230, .rodata, fragments/67/fragment67_34AB40] # spline trio literals (datamig)",
                "- [0x354240, rodata]",
            ],
        },
        {
            "op": "yaml",
            "find": "- [0x3542F0, rodata]",
            "insert_after": [
                "- {vram: 0x8292BC14, type: .bss, name: fragments/67/fragment67_34AB40} # spline trio statics (datamig; retail sw offsets 0xBC1C/18/14)",
            ],
        },
    ],
}

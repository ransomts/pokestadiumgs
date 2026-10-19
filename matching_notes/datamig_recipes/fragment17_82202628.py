# Blob-ownership migration for func_82202628 (fragment17, wave-1 park).
#
# The function body is 25/25 instruction-identical; its switch's jump table
# (jtbl_8220E0D4) lives in the fragment17 data blob, so the C switch's own
# .rodata cannot land until the blob splits around the C-owned range.
# Recipe verified at .o level (readelf) by the wave-1 agent:
#  - blob part A keeps everything through D_8220E0CC (0.2f); the C object's
#    .rodata starts at 0x8220E0D0 with the const f32 D_8220E0D0[1] = {0.001f}
#    alignment prefix (the spool carries it), then the jtbls, ending exactly
#    at the 0x11DAD0 blob part B (0x40 bytes total).
#  - yaml: the C-owned .rodata subsegment start moves 0x11DAB0 -> 0x11DA90
#    (the blob part A shrinks by 0x20: D_8220E0D0 + jtbl_8220E0D4's 7 words).
# NOTE: func_82200918 (still asm) lwc1's D_8220E0D0 - the symbol moves to the
# C object but keeps resolving (same address).

RECIPE = {
    "name": "fragment17_82202628",
    "steps": [
        {
            "op": "splice",
            "spool": "func_82202628",
            "file": "src/fragments/17/fragment17_10FFC0.c",
            "func": "func_82202628",
        },
        {
            "op": "yaml",
            "find": "- [0x11DAB0, .rodata, fragments/17/fragment17_10FFC0]",
            "replace": "- [0x11DA90, .rodata, fragments/17/fragment17_10FFC0]",
        },
    ],
}

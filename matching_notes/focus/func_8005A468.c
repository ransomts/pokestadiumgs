extern s32 func_8005CF20(s32, s32, s32);
extern u8 D_80128570[];

void func_8005A468(s32 arg0) {
    s32 count;
    s32 i;
    u8 *cursor;
    u8 *base;
    u8 *record;

    /* D_80128570[arg0] is the 112-byte GB-cart record; word 0 collects status
     * flags, +0x60 holds the save-data buffer pointer. func_8005CF20(cmd, cart, 0)
     * returns list lengths (0x2B party, 0x22 box); the loops scan those Pair
     * arrays (stride 2) for byte 0x45 and set flag 0x4000. */
    record = D_80128570 + arg0 * 0x70;
    base = *(u8 **)(record + 0x60);
    record[0x48] = func_8005CF20(0x20, arg0, 0);
    if (((s8 *)base)[0x477] & 0x20) {
        *(s32 *)record |= 0x200;
    }
    if (((s8 *)base)[0x51D] & 1) {
        *(s32 *)record |= 0x400;
    }
    count = func_8005CF20(0x2B, arg0, 0);
    if (count > 0) {
        i = 0;
        cursor = (u8 *)base;
        do {
            i += 2;
            if (cursor[0x4A] == 0x45) {
                *(s32 *)record |= 0x4000;
            }
            cursor += 2;
        } while (i < count * 2);
    }
    count = func_8005CF20(0x22, arg0, 0);
    if (count > 0) {
        i = 0;
        cursor = (u8 *)base;
        do {
            i += 2;
            if (cursor[0x267] == 0x45) {
                *(s32 *)record |= 0x4000;
            }
            cursor += 2;
        } while (i < count * 2);
    }
}

/* Unreferenced static empty function: the retail ROM has a lone jr ra; nop at
 * 0x8005A5BC (inside func_8005A468's map range, no symbol of its own), the
 * wave-8 empty-static pattern. Must be spliced together with func_8005A468. */
static void func_8005A5BC(void) {
}

s32 func_82610E34(s32 arg0) {
    s32 found;
    s32 i;
    s32 j;
    u8 *entry;
    u8 *sub;
    u8 *walker;

    found = 1;
    i = 0;
    while (i != 2) {
        entry = func_82604C40(6, i, (u8 *)arg0 + 0x114, 0x14);
        i += 1;
        sub = entry + 0x30;
        if (*(s16 *)((u8 *)entry + 0x36) > 0) {
            j = 0;
            walker = sub;
            do {
                j += 2;
                if (*(s16 *)(walker + 0x208) > 0) {
                    found = 0;
                }
                walker += 2;
            } while (j < *(s16 *)(sub + 6) * 2);
        }
        if (found == 0) {
            break;
        }
    }
    return found;
}

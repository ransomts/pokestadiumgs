s32 func_813002D0(void *arg0) {
    u8 *base = (u8 *)arg0 + 0x18000;
    s8 value = *(s8 *)(*(s8 *)(base + 0x2142) + *(u8 **)(base + 0x2148) + 0x900);

    if ((value < 4) && (value >= 0)) {
        return value;
    }
    return 0;
}

extern f64 D_86B0E038;
extern f64 D_86B0E040;
extern f32 D_86B0E048;

void func_86B09834(void) {
    u8 *ptr;
    s32 found;

    found = 0;
    if (*(s32 *)(D_86B17A78 + 0x360) != 0) {
        ptr = D_86B17A78;
        do {
            if (*(s32 *)(ptr + 0x34) == 0x16) {
                found = 1;
            }
            ptr += 4;
        } while (ptr != D_86B17A88);
        if (found != 0) {
            *(f32 *)(D_86B17A78 + 0xF8) = (f32)((f64)*(f32 *)(D_86B17A78 + 0xF8) - D_86B0E038);
        } else {
            *(f32 *)(D_86B17A78 + 0xF8) = (f32)((f64)*(f32 *)(D_86B17A78 + 0xF8) - D_86B0E040);
        }
        if (*(f32 *)(D_86B17A78 + 0xF8) < 0.0f) {
            *(f32 *)(D_86B17A78 + 0xF8) += D_86B0E048;
        }
        func_86B057B0();
        func_86B081B4();
    }
}

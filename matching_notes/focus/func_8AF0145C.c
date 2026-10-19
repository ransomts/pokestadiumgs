u8 func_80063804(u8);                              /* extern */
u8 func_8006397C(u8);                              /* extern */
u8 func_800639C0(u8);                              /* extern */
extern s16 D_8AF263F0[];
extern s16 D_8AF26412;
extern s16 D_8AF2BAD0;

void func_8AF0145C(void) {
    s32 temp_a0;
    s16 *var_s2;
    s16 *var_s5;
    s16 temp_s3;
    s16 temp_v0;
    s32 var_v0;

    var_s2 = &D_8AF2BAD0;
    var_s5 = D_8AF263F0;
    do {
        temp_s3 = *var_s5;
        for (var_v0 = 0; var_v0 != 0xFB; var_v0++) {
            temp_a0 = func_80063804(var_v0 + 1);
            temp_v0 = temp_a0;
            if ((temp_s3 == func_8006397C(temp_a0)) || (temp_s3 == func_800639C0(temp_v0))) {
                *var_s2 = temp_v0;
                var_s2++;
            }
        }
        var_s5++;
        *var_s2 = -1;
        var_s2++;
    } while (var_s5 != &D_8AF26412);
}

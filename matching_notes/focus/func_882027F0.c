typedef struct {
    u8 red;
    u8 green;
    u8 blue;
} Color_88000510;
extern void *func_88000510(void *, s8);
extern void func_880006E0(void *);
extern void func_800495F8(s32, s32, s32, const char *, ...);
extern void *func_8004C874(s32, s32);
extern s32 func_80062CE0(u8);
extern u8 func_80062D5C(u8);
extern u8 func_80062D98(u8);
extern u8 func_80062DD4(u8);
extern s32 func_80062E10(u8);
extern s32 func_80063270(u8);
extern u8 func_88201FE0(u8 *);
extern s32 func_88A008CC(u8 *);
extern void func_80048E30(void *, s16, s16, void *, s32);
extern u8 D_88005FA0[];
extern void *D_8800687C;
extern u8 D_88233BE0[];
extern u8 D_88233BE8[];
extern u8 D_88233BF0[];
extern u8 D_88233BF8[];

void func_882027F0(u8 *arg0, s16 arg1, s16 arg2, s16 arg3, s16 arg4, s16 arg5, s16 arg6) {
    u8 sp47;
    u8 sp46;
    s8 sp45;
    Color_88000510 sp40;
    f32 var_f2;
    void *temp_v0;
    u8 sp37;
    void *sp30;
    void *sp2C;

    sp47 = func_88201FE0(arg0);
    func_880006E0(D_88005FA0);
    if (sp47 != 0) {
        PERM_RANDOMIZE(
        sp46 = func_80062D5C(sp47);
        sp45 = func_80062D98(sp47);
        sp30 = func_8004C874(0x1F, 0xB);
        func_800495F8((s32) arg5, (s32) arg1, 0, D_88233BE0, sp30, func_80062E10(sp47));
        if ((sp46 == 0) || (sp46 == 1)) {
            sp2C = func_8004C874(0x1F, 0xC);
            func_800495F8(arg3, arg2, 0, D_88233BE8, sp2C, func_8004C874(0x1F, 0xE));
        } else {
            func_800495F8(arg3, arg2, 0, D_88233BF0, func_8004C874(0x1F, 0xC), sp46);
        }
        )
        sp30 = func_8004C874(0x1F, 0xD);
        sp37 = func_80062DD4(sp47);
        var_f2 = ((f32) (func_80062DD4(sp47) * 0x64) / 255.0f);
        func_800495F8(arg6, arg2, 0, D_88233BF8, sp30,
                      (s32) (((f32) (sp37 * 0x64) / 255.0f) + ((var_f2 > 0.0f) ? 0.5f : -0.5f)));
        func_880006E0(func_88000510(&sp40, sp45));
        func_80048E30(D_8800687C, arg3, arg1, func_80062CE0(sp47), 1);
        func_80048E30(D_8800687C, arg4, arg1, func_80063270((u8) sp45), 1);
        func_880006E0(D_88005FA0);
        return;
    }
    temp_v0 = func_8004C874(func_88A008CC(arg0) != 0 ? 0xB : 9, *arg0 - 1);
    if (temp_v0 != 0) {
        func_80048E30(D_8800687C, arg3, arg1, temp_v0, 1);
    }
}

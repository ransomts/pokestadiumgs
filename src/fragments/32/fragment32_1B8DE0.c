#include "global.h"


#ifdef VERSION_US
#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/32/fragment32_1B8DE0/func_88307AD0.s")

extern s32 func_88307AD0(s32, s8);
extern void *func_8004C874(s32, s32);
extern s32 func_80063270(u8);
s32 func_88307BCC(s32 arg0, u8 arg1) {
    s32 value = func_88307AD0(arg0, arg1);
    s8 narrowed = value;
    s32 result;

    if (value == -1) {
        result = (s32)func_8004C874(0x28, 0x24);
    } else {
        result = func_80063270(narrowed);
    }
    return result;
}

/* mkdraft:func_88307C2C begin */
#ifndef M2C_FIELD /* mkdraft: m2c --valid-syntax helpers */
#define M2C_UNK s32
#define M2C_UNK8 s8
#define M2C_UNK16 s16
#define M2C_UNK32 s32
#define M2C_UNK64 s64
#define M2C_FIELD(expr, type, offset) (*(type)((u8*)(expr) + (offset)))
#define M2C_BITWISE(type, expr) ((type)(expr))
#define M2C_ERROR(desc) 0
#define M2C_TRAP_IF(cond) ((void)0)
#define M2C_BREAK() ((void)0)
#define M2C_SYNC() ((void)0)
#define M2C_CARRY 0
#define M2C_STRUCT_COPY(dst, src) ((dst) = (src))
#endif

s32 func_80001FF0();                                /* extern */
M2C_UNK func_880024FC(M2C_UNK *, M2C_UNK *, M2C_UNK, M2C_UNK, s32, s32, s32, s32, s32); /* extern */
extern M2C_UNK D_88308ED0;
extern M2C_UNK D_88308EF0;
extern M2C_UNK D_88601894;
extern M2C_UNK D_88601895;

void func_88307C2C(void) {
    s32 sp30;
    f32 var_fv0;
    f32 var_fv0_2;

    sp30 = func_80001FF0();
    if ((1800.0f / (f32) func_80001FF0()) > 0.0f) {
        var_fv0 = 0.5f;
    } else {
        var_fv0 = -0.5f;
    }
    func_880024FC(&D_88308ED0, &D_88601894, 0x11, 0x8C, (s32) (var_fv0 + (1800.0f / (f32) sp30)), 0xA, 0x300, 0xE, 0x4B);
    sp30 = func_80001FF0();
    if ((1800.0f / (f32) func_80001FF0()) > 0.0f) {
        var_fv0_2 = 0.5f;
    } else {
        var_fv0_2 = -0.5f;
    }
    func_880024FC(&D_88308EF0, &D_88601895, 0x12, 0x8C, (s32) (var_fv0_2 + (1800.0f / (f32) sp30)), 0xA, 0x300, 0xE, 0x4B);
}
/* mkdraft:func_88307C2C end */

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/32/fragment32_1B8DE0/func_88307DA4.s")

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/32/fragment32_1B8DE0/func_88307DE8.s")

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/32/fragment32_1B8DE0/func_88307F28.s")
#endif

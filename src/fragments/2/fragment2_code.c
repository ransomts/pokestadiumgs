#include "global.h"


#ifdef VERSION_US
#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/2/fragment2_code/func_81900020.s")

extern s32 D_81900718;
void func_81900154(void) {
    D_81900718 = 1;
}

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/2/fragment2_code/func_81900164.s")

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/2/fragment2_code/func_81900214.s")

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/2/fragment2_code/func_8190037C.s")

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/2/fragment2_code/func_81900500.s")

/* mkdraft:func_819006A0 begin */
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

M2C_UNK func_8003F1DC(M2C_UNK *);                   /* extern */
extern M2C_UNK D_81900820;
extern s16 D_81900834;
extern M2C_UNK D_81900840;
extern M2C_UNK D_81900DE0;

void func_819006A0(s32 arg0) {
    M2C_UNK *var_s0;
    M2C_UNK *var_s1;

    var_s1 = &D_81900820;
    var_s0 = &D_81900840;
    do {
        func_8003F1DC(var_s0);
        var_s0 += 0x168;
        var_s1 += 4;
        M2C_FIELD(var_s1, s32 *, -4) = 0;
    } while (var_s0 != &D_81900DE0);
    D_81900834 = 0;
}
/* mkdraft:func_819006A0 end */
#endif

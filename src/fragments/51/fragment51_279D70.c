#include "global.h"


#ifdef VERSION_US
#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/51/fragment51_279D70/func_86303F50.s")

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/51/fragment51_279D70/func_863040C4.s")

/* mkdraft:func_8630421C begin */
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

M2C_UNK func_87F026E8(s32, void *);                 /* extern */
extern s32 D_87F119D8;
extern void *D_87F119DC;

void func_8630421C(void) {
    s32 temp_v0;

    temp_v0 = M2C_FIELD(D_87F119DC, s32 *, 0x1C);
    if (temp_v0 >= 8) {
        func_87F026E8(D_87F119D8, D_87F119DC);
        return;
    }
    M2C_FIELD(D_87F119DC, s8 *, 0x41) = (s8) (u32) (200.0f * (1.0f - ((f32) temp_v0 / 7.0f)));
}
/* mkdraft:func_8630421C end */

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/51/fragment51_279D70/func_86304318.s")

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/51/fragment51_279D70/func_863043E4.s")

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/51/fragment51_279D70/func_86304544.s")
#endif

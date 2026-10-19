#include "global.h"


#ifdef VERSION_US
#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/67/fragment67_34AB40/func_8290E040.s")

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/67/fragment67_34AB40/func_8290E0FC.s")

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/67/fragment67_34AB40/func_8290E1D8.s")

/* mkdraft:func_8290E2A8 begin */
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

extern M2C_UNK D_8291BC00;
extern M2C_UNK D_8291BC04;
extern M2C_UNK D_8291BC08;
extern M2C_UNK D_8291BC10;

void func_8290E2A8(void) {
    M2C_FIELD(&D_8291BC00, s16 *, 0) = 0xA;
    M2C_FIELD(&D_8291BC04, s16 *, 0) = 1;
    M2C_FIELD(&D_8291BC10, s16 *, 0) = 0xE;
    M2C_FIELD(&D_8291BC00, s16 *, 2) = 0xA;
    M2C_FIELD(&D_8291BC04, s16 *, 2) = 1;
    M2C_FIELD(&D_8291BC10, s16 *, 2) = 0xE;
    M2C_FIELD(&D_8291BC08, f32 *, 0) = 0.0f;
    M2C_FIELD(&D_8291BC08, f32 *, 4) = 0.0f;
}
/* mkdraft:func_8290E2A8 end */

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/67/fragment67_34AB40/func_8290E2FC.s")

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/67/fragment67_34AB40/func_8290E438.s")
#endif

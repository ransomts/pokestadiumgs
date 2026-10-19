#include "global.h"


#ifdef VERSION_US
extern void func_87F02CE0(s32 *, s32, s32);
extern u8 D_80126420;

void func_87F02CB0(s32 arg0, s32 arg1) {
    func_87F02CE0(&D_80126420, arg0, arg1);
}

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/64/fragment64_325920/func_87F02CE0.s")

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/64/fragment64_325920/func_87F02F00.s")

/* mkdraft:func_87F03204 begin */
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

void func_87F03204(void *arg0, void *arg1) {
    u8 temp_v0;

    temp_v0 = M2C_FIELD(arg1, u8 *, 0xC);
    switch (temp_v0) {                              /* irregular */
    case 0:
        M2C_FIELD(arg1, s16 *, 0x1C) = 0x1FF;
        M2C_FIELD(arg1, f32 *, 0x18) = 1.0f;
        return;
    case 1:
        M2C_FIELD(arg0, f32 *, 0x14) = (f32) -M2C_FIELD(arg1, f32 *, 0);
        M2C_FIELD(arg1, s16 *, 0x1C) = 0x1FF;
        M2C_FIELD(arg1, f32 *, 0x18) = 1.0f;
        return;
    case 2:
    case 3:
        M2C_FIELD(arg1, s16 *, 0x1C) = 0x2FF;
        M2C_FIELD(arg1, f32 *, 0x18) = 1.0f;
        return;
    }
}
/* mkdraft:func_87F03204 end */

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/64/fragment64_325920/func_87F0328C.s")

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/64/fragment64_325920/func_87F0339C.s")

extern void func_87F02684();

void func_87F034CC(void) {
    func_87F02684();
}
#endif

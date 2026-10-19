#include "global.h"


#ifdef VERSION_US
void func_8AF07CB0(u8 *arg0, s32 arg1, s32 arg2) {
    *(s32 *)(arg0 + 0x28) = arg1;
    *(s32 *)(arg0 + 0x2C) = arg2;
}

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/44/fragment44_1F5F20/func_8AF07CBC.s")

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/44/fragment44_1F5F20/func_8AF07EBC.s")

extern s16 D_8AF2C960;
void func_8AF07FF0(void) {
    D_8AF2C960 = 1;
}

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/44/fragment44_1F5F20/func_8AF08000.s")

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/44/fragment44_1F5F20/func_8AF08390.s")

/* mkdraft:func_8AF084BC begin */
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

M2C_UNK func_8AF00130(M2C_UNK);                     /* extern */
M2C_UNK func_8AF180F4();                            /* extern */
extern void *D_8AF263C0;
extern s16 D_8AF2C960;

s16 func_8AF084BC(s16 arg0) {
    u16 temp_v0;

    temp_v0 = M2C_FIELD(D_8AF263C0, u16 *, 8);
    if (temp_v0 & 0x100) {
        D_8AF2C960 = 1;
    } else if (temp_v0 & 0x400) {
        D_8AF2C960 = 3;
    } else if (temp_v0 & 0x8000) {
        func_8AF00130(0xBF);
        arg0 = 0x13;
        func_8AF180F4();
    }
    return arg0;
}
/* mkdraft:func_8AF084BC end */

#ifndef M2C_FIELD /* sweep: m2c --valid-syntax helpers (mirrors mkdraft.py) */
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

M2C_UNK func_8AF00130(M2C_UNK);                     /* extern */
M2C_UNK func_8AF08C90();                            /* extern */
extern void *D_8AF263C0;

s16 func_8AF08538(s16 arg0) {
    u16 temp_v0;

    temp_v0 = M2C_FIELD(D_8AF263C0, u16 *, 8);
    if (temp_v0 & 0x400) {
        D_8AF2C960 = 5;
    } else if (temp_v0 & 0x200) {
        D_8AF2C960 = 0;
    } else if (temp_v0 & 0x100) {
        D_8AF2C960 = 2;
    } else if (temp_v0 & 0x8000) {
        func_8AF00130(0xBF);
        arg0 = 8;
        func_8AF08C90();
    }
    return arg0;
}
/* mkdraft:func_8AF085C8 begin */
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

M2C_UNK func_8AF10CD4();                            /* extern */

s16 func_8AF085C8(s16 arg0) {
    u16 temp_v0;

    temp_v0 = M2C_FIELD(D_8AF263C0, u16 *, 8);
    if (temp_v0 & 0x200) {
        D_8AF2C960 = 1;
    } else if (temp_v0 & 0x400) {
        D_8AF2C960 = 4;
    } else if (temp_v0 & 0x8000) {
        func_8AF00130(0xBF);
        arg0 = 0xD;
        func_8AF10CD4();
    }
    return arg0;
}
/* mkdraft:func_8AF085C8 end */

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/44/fragment44_1F5F20/func_8AF08644.s")

#ifndef M2C_FIELD /* sweep: m2c --valid-syntax helpers (mirrors mkdraft.py) */
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

M2C_UNK func_8AF00130(M2C_UNK);                     /* extern */
M2C_UNK func_8AF1B5D4();                            /* extern */
extern void *D_8AF263C0;

s16 func_8AF086C4(s16 arg0) {
    u16 temp_v0;

    temp_v0 = M2C_FIELD(D_8AF263C0, u16 *, 8);
    if (temp_v0 & 0x800) {
        D_8AF2C960 = 1;
    } else if (temp_v0 & 0x200) {
        D_8AF2C960 = 3;
    } else if (temp_v0 & 0x100) {
        D_8AF2C960 = 4;
    } else if (temp_v0 & 0x8000) {
        func_8AF00130(0xBF);
        arg0 = 0x15;
        func_8AF1B5D4();
    }
    return arg0;
}
/* mkdraft:func_8AF08758 begin */
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

M2C_UNK func_8AF1C804();                            /* extern */

s16 func_8AF08758(s16 arg0) {
    u16 temp_v0;

    temp_v0 = M2C_FIELD(D_8AF263C0, u16 *, 8);
    if (temp_v0 & 0x800) {
        D_8AF2C960 = 2;
    } else if (temp_v0 & 0x200) {
        D_8AF2C960 = 5;
    } else if (temp_v0 & 0x8000) {
        func_8AF00130(0xBF);
        arg0 = 0x17;
        func_8AF1C804();
    }
    return arg0;
}
/* mkdraft:func_8AF08758 end */

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/44/fragment44_1F5F20/func_8AF087D4.s")

extern void func_800498C4(void);
extern void func_800499EC(void);
void func_8AF0894C(void) {
    func_800498C4();
    func_800499EC();
}
#pragma C_FUNCTION_PADDING(12)
#endif
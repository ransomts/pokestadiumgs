#include "global.h"


#ifdef VERSION_US
extern s32 D_880068B8;
void func_8822AD40(void) {
    D_880068B8 = 0;
}

extern void func_88220AD0(s32, s32);
extern s32 D_80087200;
extern s32 D_88234660;
void Input_SetRepeatController(s32 value);
extern void func_88001900();
extern s32 D_880068B4;
extern void Util_Free(s32);
extern u32 D_882348F0;
void func_8822AD4C(void) {
    if (D_88234660 != 0) {
        func_88220AD0(0x17C, 0x11F);
    } else {
        Input_SetRepeatController(D_80087200);
        func_88001900();
        D_880068B4 = 1;
    }
    Util_Free((s32) D_882348F0);
}

extern void func_88004990(u8, u8);
void func_8822ADB0(void) {
    if (*(u16 *)((u8 *)D_80087200 + 8) & 0xC000) {
        func_88004990(**(u8 **)D_882348F0, 0);
        D_880068B8 = 1;
    }
}

extern void func_889033A0(s32);
void func_8822AE04(void) {
    func_889033A0((D_882348F0 + 4));
}

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/31/fragment31_19DFC0/func_8822AE2C.s")

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/31/fragment31_19DFC0/func_8822AF00.s")

void func_8822B240(void) {
    D_880068B8 = 0;
}

extern s32 D_88234900;

void func_8822B24C(void) {
    func_88001900();
    D_880068B4 = 1;
    Util_Free(D_88234900);
}

void func_8822B284(void) {
    if (*(u16 *)((u8 *)D_80087200 + 8) & 0xC000) {
        func_88004990(**(u8 **)D_88234900, 0);
        D_880068B8 = 1;
    }
}

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/31/fragment31_19DFC0/func_8822B2D8.s")

/* mkdraft:func_8822B43C begin */
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

M2C_UNK func_8004C54C(M2C_UNK, s32);                /* extern */
M2C_UNK func_8004C8A0(void *, M2C_UNK, M2C_UNK, M2C_UNK); /* extern */
s32 func_800635E0(u8);                              /* extern */
s32 func_88004804(M2C_UNK, M2C_UNK, M2C_UNK, M2C_UNK, s32, s32, s32, s32, s32, M2C_UNK *, M2C_UNK *, M2C_UNK *, M2C_UNK *, s32, s32); /* extern */
s32 func_8820137C(s32);                             /* extern */
extern s32 D_880068B4;
extern M2C_UNK D_8800ED50;
extern s32 D_882345F4;
extern s32 D_88234900;
void func_8822B240(void);
void func_8822B24C(void);
void func_8822B284(void);
void func_8822B2D8(void);

void func_8822B43C(u8 arg0) {
    D_88234900 = Util_Malloc(0x48);
    M2C_FIELD(D_88234900, s32 *, 4) = func_8820137C(D_882345F4);
    func_8004C54C(0x18, func_800635E0(arg0));
    func_8004C8A0(D_88234900 + 8, 0x40, 0x25, 0x75);
    M2C_FIELD(D_88234900, void **, 0) = (void *) ((func_88004804(0, 3, 0xC7, 0xE0, 0, 1, 0xDC, 0xDC, 0xB4, &func_8822B284, &func_8822B2D8, &func_8822B240, &func_8822B24C, 2, 0) * 0x4C) + &D_8800ED50);
    M2C_FIELD(M2C_FIELD(D_88234900, void **, 0), s16 *, 0x10) = 0x165;
    M2C_FIELD(M2C_FIELD(D_88234900, void **, 0), s16 *, 0x12) = 0x81;
    D_880068B4 = 0;
}
/* mkdraft:func_8822B43C end */
#endif

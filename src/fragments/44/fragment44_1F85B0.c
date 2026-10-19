#include "global.h"


#ifdef VERSION_US
#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/44/fragment44_1F85B0/func_8AF0A340.s")

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/44/fragment44_1F85B0/func_8AF0A3A8.s")

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/44/fragment44_1F85B0/func_8AF0A4AC.s")

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/44/fragment44_1F85B0/func_8AF0A6E4.s")

extern void Ui_DrawGradientQuad(s32, s32, u16, u16, s32 *, s32 *);
extern u8 D_8AF26450;
extern u8 D_8AF26454;
s32 func_8AF0A800(void *arg0) {
    void *temp_v0;

    temp_v0 = (*(void **)((u8 *)(arg0) + (0x20)));
    Ui_DrawGradientQuad(0, 0, (*(u16 *)((u8 *)(temp_v0) + (4))), (*(u16 *)((u8 *)(temp_v0) + (6))), &D_8AF26450, &D_8AF26454);
    return 0;
}

extern void func_800504BC(s16 *arg0);
s32 func_8AF0A850(s32 arg0, void *arg1) {
    struct { s32 pad[2]; s16 angles[2]; } scratch;
    if ((arg0 != 0) && (arg0 == 1)) {
        func_800504BC(scratch.angles);
    }
    return 0;
}

s32 func_8004C990(s32, s32);
extern s32 D_8AF2D428;
extern s32 D_8AF2D42C;
extern s32 D_8AF2D430;
extern s32 D_8AF2D434;
extern s32 D_8AF2D438;

void func_8AF0A888(void) {
    D_8AF2D428 = func_8004C990(0xAD, 0);
    D_8AF2D42C = func_8004C990(0xAD, 1);
    D_8AF2D430 = func_8004C990(0xAD, 2);
    D_8AF2D434 = func_8004C990(0xAD, 3);
    D_8AF2D438 = func_8004C990(0xAD, 4);
}

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/44/fragment44_1F85B0/func_8AF0A900.s")

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/44/fragment44_1F85B0/func_8AF0AAF8.s")

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/44/fragment44_1F85B0/func_8AF0AB84.s")

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/44/fragment44_1F85B0/func_8AF0ACDC.s")

/* mkdraft:func_8AF0B544 begin */
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

M2C_UNK func_8AC006F4();                            /* extern */
M2C_UNK func_8AC007FC();                            /* extern */
M2C_UNK func_8AC063AC(M2C_UNK *, u16, s16);         /* extern */
M2C_UNK func_8AF00130(M2C_UNK);                     /* extern */
extern void *D_8AF263C0;
extern s32 D_8AF2694C;
extern s16 D_8AF2BAC8;
extern u16 D_8AF2BDC6;
extern s16 D_8AF2D300;
extern s16 D_8AF2D304;
extern void *D_8AF2D3C4;
extern void *D_8AF2D3C8;
extern M2C_UNK D_8AF2D490;
extern s16 D_8AF2D508;

s16 func_8AF0B544(void) {
    s16 sp1E;
    s16 var_a2;
    u16 temp_v0;

    func_8AC007FC();
    var_a2 = 0xA;
    if (D_8AF2D508 >= 5) {
        D_8AF2D508 = 4;
        temp_v0 = M2C_FIELD(D_8AF263C0, u16 *, 8);
        if (temp_v0 & 0x8000) {
            switch (D_8AF2D304) {                   /* irregular */
            case 0:
                func_8AF00130(0xC2);
                var_a2 = 0xC;
                D_8AF2694C = 0;
                break;
            case 1:
                func_8AF00130(0xC2);
                var_a2 = 0xB;
                D_8AF2694C = 0;
                break;
            }
        } else if (temp_v0 & 0x4000) {
            func_8AF00130(3);
            func_8AC006F4();
            var_a2 = D_8AF2D300;
            D_8AF2694C = 0;
        } else if (temp_v0 & 0x100) {
            if (D_8AF2D304 != 0) {
                sp1E = 0xA;
                func_8AF00130(1);
                var_a2 = 0xA;
            }
            D_8AF2D304 = 0;
        } else if (temp_v0 & 0x200) {
            if (D_8AF2D304 != 1) {
                sp1E = 0xA;
                func_8AF00130(1);
                var_a2 = 0xA;
            }
            D_8AF2D304 = 1;
        }
    }
    if (var_a2 != 0xA) {
        D_8AF2BAC8 = 0;
    }
    if (D_8AF2D304 == 1) {
        M2C_FIELD(D_8AF2D3C4, u16 *, 2) = (u16) (M2C_FIELD(D_8AF2D3C4, u16 *, 2) | 1);
        M2C_FIELD(D_8AF2D3C8, u16 *, 2) = (u16) (M2C_FIELD(D_8AF2D3C8, u16 *, 2) & 0xFFFE);
    } else {
        M2C_FIELD(D_8AF2D3C4, u16 *, 2) = (u16) (M2C_FIELD(D_8AF2D3C4, u16 *, 2) & 0xFFFE);
        M2C_FIELD(D_8AF2D3C8, u16 *, 2) = (u16) (M2C_FIELD(D_8AF2D3C8, u16 *, 2) | 1);
    }
    sp1E = var_a2;
    func_8AC063AC(&D_8AF2D490, D_8AF2BDC6, var_a2);
    D_8AF2D508 += 1;
    return sp1E;
}
/* mkdraft:func_8AF0B544 end */

extern Gfx *D_800D0510;

void func_8AF0B724(s32 arg0, s32 arg1) {
    gSPTextureRectangle(D_800D0510++, arg0 << 2, arg1 << 2,
                        (arg0 + 20) << 2, (arg1 + 20) << 2,
                        G_TX_RENDERTILE, 0, 0, 1024, 1024);
}

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/44/fragment44_1F85B0/func_8AF0B7BC.s")

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/44/fragment44_1F85B0/func_8AF0B850.s")

extern void func_80043E70(s32, s32);
extern s32 D_8AF2694C;

void func_8AF0BB04(void) {
    if (D_8AF2694C != 0) {
        func_80043E70(D_8AF2694C, 0);
    }
}
#endif

#include "global.h"


#ifdef VERSION_US
typedef struct { u8 first, second; } Func8822D140Pair;
void func_8822D140(Func8822D140Pair *arg0, Func8822D140Pair *arg1) {
    Func8822D140Pair temp = *arg0;
    *arg0 = *arg1;
    *arg1 = temp;
}

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

void func_8822D180(u32 arg0, s32 arg1, s32 (*arg2)(s32, s32)) {
    u32 temp_s4;
    u32 var_s0;
    u32 var_s3;

    temp_s4 = (arg1 * 4) + arg0;
    var_s3 = arg0;
    if (arg0 < temp_s4) {
        do {
            var_s0 = var_s3;
            if ((arg0 < var_s3) && (arg2(M2C_FIELD(var_s3, s32 *, -4), M2C_FIELD(var_s3, s32 *, 0)) > 0)) {
loop_3:
                func_8822D140(M2C_FIELD(var_s0, Func8822D140Pair **, 0), M2C_FIELD(var_s0, Func8822D140Pair **, -4));
                var_s0 -= 4;
                if (arg0 < var_s0) {
                    if (arg2(M2C_FIELD(var_s0, s32 *, -4), M2C_FIELD(var_s0, s32 *, 0)) > 0) {
                        goto loop_3;
                    }
                }
            }
            var_s3 += 4;
        } while (var_s3 < temp_s4);
    }
}
#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/31/fragment31_1A03C0/func_8822D238.s")

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/31/fragment31_1A03C0/func_8822D2F4.s")

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/31/fragment31_1A03C0/func_8822D3A8.s")

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/31/fragment31_1A03C0/func_8822D45C.s")

extern void Input_SetRepeatController(s32);
extern s32 D_80087200;
extern s32 D_880068B8;

void func_8822D750(void) {
    Input_SetRepeatController(D_80087200);
    D_880068B8 = 0;
}

extern s32 D_880068B4;
extern void Util_Free(s32);
extern u32 D_88234940;
void func_8822D778(void) {
    Input_SetRepeatController(D_80087200);
    D_880068B4 = 1;
    Util_Free(D_88234940);
}

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/31/fragment31_1A03C0/func_8822D7B4.s")

extern void func_8821D930(s32);
void func_8822D874(void) {
    func_8821D930(D_88234940 + 4);
}

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/31/fragment31_1A03C0/func_8822D89C.s")


void func_8822DB00(void) {
    Input_SetRepeatController(D_80087200);
    D_880068B8 = 0;
}

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/31/fragment31_1A03C0/func_8822DB28.s")

extern void func_88004990(u8, s32);
extern void *D_88234950;
void func_8822DC34(void) {
    func_88004990(*(*(u8 **)((u8 *)(D_88234950) + (4))), 0);
    func_88004990(*(*(u8 **)((u8 *)(D_88234950) + (8))), 0);
    D_880068B8 = 1;
}

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/31/fragment31_1A03C0/func_8822DC84.s")

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/31/fragment31_1A03C0/func_8822DEBC.s")

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/31/fragment31_1A03C0/func_8822E290.s")
#endif

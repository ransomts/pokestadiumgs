#include "global.h"


#ifdef VERSION_US
s32 func_87E043F0(u8 *arg0) {
    return (*(u16 *)(arg0 + 0x274) & 4) != 0;
}

/* mkdraft:func_87E04400 begin */
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

M2C_UNK func_87E10E64(s32);                         /* extern */
M2C_UNK func_87E10EA8(s32);                         /* extern */
M2C_UNK func_87E10F2C(s32);                         /* extern */
extern M2C_UNK D_87E19A44;
extern M2C_UNK D_87E19A74;

void func_87E04400(void *arg0) {
    void *sp1C;
    s32 temp_v1;
    void *var_v0;

    if (M2C_FIELD(M2C_FIELD(arg0, void **, 0x270), u8 *, 0x2180) == 0) {
        var_v0 = (M2C_FIELD(arg0, s32 *, 4) * 0xC) + &D_87E19A44;
    } else {
        var_v0 = (M2C_FIELD(arg0, s32 *, 4) * 0xC) + &D_87E19A74;
    }
    temp_v1 = M2C_FIELD(arg0, s32 *, 0);
    if ((temp_v1 == 2) || (temp_v1 == 3)) {
        func_87E10EA8(-1);
        func_87E10F2C(-1);
        return;
    }
    sp1C = var_v0;
    func_87E10E64(M2C_FIELD(var_v0, s32 *, 0));
    func_87E10EA8(M2C_FIELD(var_v0, s32 *, 4));
    func_87E10F2C(M2C_FIELD(var_v0, s32 *, 8));
}
/* mkdraft:func_87E04400 end */

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/63/fragment63_307D60/func_87E044B8.s")

/* mkdraft:func_87E0469C begin */
extern Gfx *D_800D0510;
extern void *D_8009491C;
extern void func_8003CD84(void);
typedef struct { u8 pad_60[0x60]; u8 red; u8 green; u8 blue; } Func87E0375CColor;

void func_87E0469C(s32 arg0, s32 arg1) {
    u8 *context;
    Func87E0375CColor *temp_a0;
    void *temp_a1;
    if (arg0 == 5) {
        context = (u8 *)D_8009491C;
        temp_a0 = *(Func87E0375CColor **)(context + 0x14);
        temp_a1 = *(void **)((u8 *)temp_a0 + 0x20);
        gDPPipeSync(D_800D0510++);
        gDPSetCombine(D_800D0510++, 0x50FFFF, -0xDC8);
        gDPSetEnvColor(D_800D0510++, temp_a0->red, temp_a0->green,
                       temp_a0->blue, 0xFF);
        gSPSegment(D_800D0510++, 0xF,
                   *(void **)((u8 *)(*(void **)((u8 *)temp_a1 + 0x4)) + 8));
        gSPDisplayList(D_800D0510++, *(void **)((u8 *)temp_a1 + 8));
        func_8003CD84();
    }}
/* mkdraft:func_87E0469C end */

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/63/fragment63_307D60/func_87E04790.s")

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/63/fragment63_307D60/func_87E049A4.s")

extern void func_87E04790(u8 *);
extern void func_87E134C0(void);
extern void func_87E13490(void);
extern void func_87E13480(u8 *);
void func_87E04A14(u8 *arg0) {
    switch (*(s8 *)(*(u8 **)(arg0 + 0x270) + 0x2181)) {
        case 0: *(s32 *)(arg0 + 4) = 3; break;
        case 1: *(s32 *)(arg0 + 4) = 2; break;
        case 2: *(s32 *)(arg0 + 4) = 1; break;
        case 3: *(s32 *)(arg0 + 4) = 0; break;
    }
    *(s32 *)arg0 = 0;
    func_87E04790(arg0);
    func_87E134C0();
    func_87E13490();
    func_87E13480(NULL);
}

extern void func_87F02684(s32);
void func_87E04AA4(s32 arg0) {
    func_87F02684(arg0 + 8);
}

s32 func_87E04AC4(u32 arg0) {
    u8 *entry = (u8 *)arg0 + 0x1C;
    s32 result = 1;
    s32 index;
    arg0 = 4;
    index = 0;
    do {
        index++;
        if (*(s32 *)(entry + 0x90) != 0) {
            result = 0;
            break;
        }
        entry += 0x94;
    } while (index != arg0);
    return result;
}

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/63/fragment63_307D60/func_87E04AFC.s")

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/63/fragment63_307D60/func_87E04D2C.s")

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/63/fragment63_307D60/func_87E04ED4.s")

extern void func_8004C8C0(s32);
void func_87E05128(void) {
    func_8004C8C0(426);
}

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/63/fragment63_307D60/func_87E05148.s")

extern void func_8005493C(void *);
extern void func_87E05128(void);
extern void func_87E05148(void *);
extern void func_87E049A4(void *);
void func_87E0520C(void *arg0, s32 arg1) {
    *(s32 *)((u8 *)arg0 + 0x270) = arg1;
    *(s32 *)arg0 = 0;
    func_8005493C((u8 *)arg0 + 0x274);
    func_87E05128();
    func_87E05148(arg0);
    func_87E049A4(arg0);
}

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/63/fragment63_307D60/func_87E05258.s")

extern void func_87E05258(void);
extern void BgStage_DrawFrame(void);
void func_87E053D0(void) {
    func_87E05258();
    BgStage_DrawFrame();
}
#pragma C_FUNCTION_PADDING(8)
#endif

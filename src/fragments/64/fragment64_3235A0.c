#include "global.h"


#ifdef VERSION_US
extern u8 *D_87F0F610;
u32 func_87F00930(void) {
    return ((u32)D_87F0F610[0x3D]) >> 7;
}

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/64/fragment64_3235A0/func_87F00944.s")

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/64/fragment64_3235A0/func_87F01110.s")

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/64/fragment64_3235A0/func_87F012BC.s")

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/64/fragment64_3235A0/func_87F014C4.s")

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/64/fragment64_3235A0/func_87F01870.s")

extern u8 D_800CE060[];
extern void func_80006148(u8 *);
void func_87F01934(void) {
    u8 *entry = D_800CE060;
    s32 offset;

    for (offset = 0; offset < 8; offset += 2) {
        *(u16 *)(D_87F0F610 + offset + 0x34) = *(u16 *)(entry + 0x10);
        func_80006148(entry);
        entry += 0x28;
    }
}

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/64/fragment64_3235A0/func_87F019A4.s")

extern void Audio_PlayDefaultSound(s32);
extern void func_8002809C();
void func_87F019F0(void) {
    func_8002809C();
    if ((*(s32 *)((u8 *)(D_87F0F610) + (0x30))) == 2) {
        Audio_PlayDefaultSound(0xCF08);
        return;
    }
    Audio_PlayDefaultSound(0xCF02);
}

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/64/fragment64_3235A0/func_87F01A40.s")

/* mkdraft:func_87F01D44 begin */
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

M2C_UNK func_800503A4(s32);                         /* extern */
M2C_UNK func_87F08FA0(u8);                          /* extern */
extern u8 *D_87F0F610;

void func_87F01D44(void) {
    if (M2C_FIELD(D_87F0F610, s8 *, 0x3D) < 0) {
        func_87F08FA0(M2C_FIELD(D_87F0F610, u8 *, 0x3C));
        func_800503A4(M2C_FIELD((D_87F0F610 + (M2C_FIELD(D_87F0F610, s32 *, 0x10) * 4)), s32 *, 0x20));
    }
}
/* mkdraft:func_87F01D44 end */
#endif
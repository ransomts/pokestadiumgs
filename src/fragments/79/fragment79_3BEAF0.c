#include "global.h"


void func_8414F260(void) {
}

#ifdef VERSION_US
#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/79/fragment79_3BEAF0/func_8414F268.s")
#endif

#ifdef VERSION_US
/* mkdraft:func_8414F2F4 begin */
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

s32 func_8414C960(s32);                             /* extern */
s32 func_84154B24();                                /* extern */
extern M2C_UNK D_841951F8;

void func_8414F2F4(void *arg0) {
    s32 temp_s3;
    s32 temp_v1;
    s32 var_s0;
    s32 var_s1;
    s32 var_s5;
    u8 temp_v1_2;
    void **temp_s2;

s32 func_84154B24();                                /* extern */
    temp_s2 = (temp_v1 * 4) + &D_841951F8;
    temp_s3 = temp_v1 * 2;
    var_s0 = 0;
    var_s1 = 0;
    var_s5 = M2C_FIELD(arg0, s32 *, 0x14);
    do {
        temp_v1_2 = M2C_FIELD((func_8414C960(((M2C_FIELD(*temp_s2, u8 *, 0xA) * 4) + var_s0) & 0xFF) + temp_s3), u8 *, 3);
        var_s0 += 1;
        if (var_s1 < (s32) temp_v1_2) {
            var_s1 = temp_v1_2 & 0xFF;
        }
    } while (var_s0 != 4);
    if (var_s1 != 0) {
        if (var_s5 < 0) {
            var_s5 = -var_s5;
        }
        if (var_s1 < 0x80) {
            M2C_FIELD(arg0, s32 *, 0x18) = (s32) ((s32) (-var_s5 * (var_s1 + 0xA)) / 255);
            return;
        }
        M2C_FIELD(arg0, s32 *, 0x18) = (s32) -var_s5;
    }
}
/* mkdraft:func_8414F2F4 end */
#endif

#ifdef VERSION_US
s32 func_84154B24();                                /* extern */
void func_8414F3FC(void *arg0) {
    u8 value = func_84154B24();
    if (*(u16 *)((u8 *)arg0 + value * 2 + 2) < 0xB2) {
        *(u8 *)arg0 |= 0x10;
    }
}
#endif

#ifdef VERSION_US
extern u8 *func_84154B64(u8);
extern s32 func_841556C4(u8 *, u8);
void func_8414F444(u8 *arg0, u8 arg1) {
    u8 value = func_84154B24();
    if (func_841556C4(func_84154B64(1 - value), arg1) != 0) {
        *(s32 *)(arg0 + 0x18) = *(s32 *)(arg0 + 0x18) - *(s32 *)(arg0 + 0x14);
    }
}
#endif

#ifdef VERSION_US
#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/79/fragment79_3BEAF0/func_8414F4A0.s")
#endif

#ifdef VERSION_US
extern void func_8414F268(void *);
extern void func_8414F2F4(void *);
void func_8414F5F0(void *arg0) {
    func_8414F268(arg0);
    func_8414F2F4(arg0);
}
#endif

#ifdef VERSION_US
extern void func_8414F5F0(void *);
extern void func_8414F3FC(void *);
void func_8414F618(void *arg0) {
    u8 value;
    u8 *ptr;
    func_8414F5F0(arg0);
    value = func_84154B24();
    ptr = func_84154B64(1 - value);
    if (*(u16 *)(ptr + 0x26) & 0x20) {
        func_8414F3FC(arg0);
    }
}
#endif

#ifdef VERSION_US
extern u8 *func_8414A3A0(u8);
extern void func_8414F444(u8 *, u8);
void func_8414F668(u8 *arg0) {
    u8 value = func_84154B24();
    u8 *ptr = func_8414A3A0(value);
    if ((*(s32 *)ptr << 15) >= 0) {
        func_8414F444(arg0, 0x11);
        func_8414F444(arg0, 0x5E);
        func_8414F444(arg0, 0x19);
        func_8414F444(arg0, 0x71);
    }
}
#endif

#ifdef VERSION_US
void func_8414F6D0(void *arg0) {
    u8 value;
    u8 *ptr;
    func_8414F2F4(arg0);
    value = func_84154B24();
    ptr = func_8414A3A0(value);
    if ((*(s32 *)ptr << 15) >= 0) {
        func_8414F444(arg0, 0x11);
        func_8414F444(arg0, 0x5E);
        func_8414F444(arg0, 0x19);
        func_8414F444(arg0, 0x71);
    }
}
#endif

#ifdef VERSION_US
#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/79/fragment79_3BEAF0/func_8414F748.s")
#endif

#ifdef VERSION_US
extern void func_8414F4A0(s32, s32);
void func_8414F894(s32 arg0) {
    func_8414F4A0(arg0, 83);
}
#endif

#ifdef VERSION_US
#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/79/fragment79_3BEAF0/func_8414F8B4.s")
#endif

#ifdef VERSION_US
#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/79/fragment79_3BEAF0/func_8414F93C.s")
#endif

#ifdef VERSION_US
#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/79/fragment79_3BEAF0/func_8414FA3C.s")
#endif

#ifdef VERSION_US
#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/79/fragment79_3BEAF0/func_8414FB24.s")
#endif
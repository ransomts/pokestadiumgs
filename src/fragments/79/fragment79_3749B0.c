#include "global.h"


#ifdef VERSION_US
/* mkdraft:func_84105120 begin */
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

M2C_UNK func_8410358C();                            /* extern */
M2C_UNK func_8410474C();                            /* extern */
M2C_UNK func_84105CA8();                            /* extern */
M2C_UNK func_84105D00();                            /* extern */
M2C_UNK func_841091CC();                            /* extern */
extern M2C_UNK D_84190078;
extern s32 D_84190180;
extern s32 D_84190184;
extern s32 D_84190188;
extern s32 D_84190190;
extern s32 D_841901A8;
extern M2C_UNK D_84190218;

void func_84105120(void) {
    D_84190180 = 0;
    D_84190184 = 0;
    D_84190190 = 0;
    D_84190188 = 0;
    M2C_FIELD(&D_84190078, f32 *, 0) = 1.0f;
    M2C_FIELD(&D_84190078, f32 *, 4) = 1.0f;
    M2C_FIELD(&D_84190078, f32 *, 8) = 1.0f;
    D_841901A8 = 0;
    M2C_FIELD(&D_84190218, s8 *, 0) = 0xFF;
    M2C_FIELD(&D_84190218, s8 *, 1) = 0xFF;
    M2C_FIELD(&D_84190218, s8 *, 2) = 0xFF;
    M2C_FIELD(&D_84190218, s8 *, 4) = 0xFF;
    M2C_FIELD(&D_84190218, s8 *, 5) = 0xFF;
    M2C_FIELD(&D_84190218, s8 *, 6) = 0xFF;
    M2C_FIELD(&D_84190218, s8 *, 8) = 0xFF;
    M2C_FIELD(&D_84190218, s8 *, 9) = 0xFF;
    M2C_FIELD(&D_84190218, s8 *, 0xA) = 0xFF;
    func_8410358C();
    func_8410474C();
    func_84105D00();
    func_84100134();
    func_841091CC();
    func_84105CA8();
}
/* mkdraft:func_84105120 end */

extern s32 D_841901AC;
extern s32 func_84108654(u16, u16);
extern s32 func_8410922C(s32, u16);
s32 func_841051D8(u16 arg0, u16 arg1) {
    if (arg0 < 0x2000) {
        return func_84108654(arg0, arg1);
    }
    if (arg0 & 0x1000) {
        D_841901AC = 1;
        return func_8410922C(arg0 - 0x3000, arg1);
    }
    D_841901AC = 0;
    return func_8410922C(arg0 - 0x2000, arg1);
}

extern s32 func_841051D8(u16, u16);
void func_84105250(u16 *arg0, u16 arg1) {
    u16 value;
    value = *arg0;
    while (value != 0) {
        func_841051D8(value, arg1);
        arg0++;
        value = *arg0;
    }
}

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/79/fragment79_3749B0/func_841052AC.s")

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/79/fragment79_3749B0/func_8410545C.s")

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/79/fragment79_3749B0/func_841054D4.s")

extern void func_841054D4(void);
extern void func_84105B90(u8 *);
extern void func_841052AC(void);
extern void func_8410545C(void);
extern void func_84107B68(void);
extern void func_841029DC(void);
extern void func_841092B8(u8 *);
extern void func_84105CE8(void);
void func_841055D8(u8 *arg0) {
    func_841054D4();
    func_84105B90(arg0);
    func_841052AC();
    func_8410545C();
    func_84107B68();
    func_841029DC();
    func_841092B8(arg0);
    func_84105CE8();
}

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/79/fragment79_3749B0/func_84105630.s")

extern void func_84105120(void);
extern void func_841055D8(u8 *);
extern void func_84105630(u8 *, s32);
s32 func_8410580C(s32 arg0, u8 *arg1, s32 arg2) {
    switch (arg0) {
    case 0:
        func_84105120();
        break;
    case 2:
        func_841055D8(arg1);
        break;
    case 5:
        func_84105630(arg1, arg2);
        break;
    }
    return 0;
}
#pragma C_FUNCTION_PADDING(12)
#endif

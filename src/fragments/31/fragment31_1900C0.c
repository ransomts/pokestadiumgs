#include "global.h"


#ifdef VERSION_US
#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/31/fragment31_1900C0/func_8821CE40.s")

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/31/fragment31_1900C0/func_8821D308.s")

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/31/fragment31_1900C0/func_8821D3FC.s")

/* mkdraft:func_8821D550 begin */
extern s32 func_80001FF0(void);
extern void StageFade_StartFromOpaque(s32);
extern void func_80064D28(void);
extern void func_8821D3FC(void);
extern f32 D_8823416C;

void func_8821D550(void) {
    u16 count;
    s32 i;
    count = (u16)((f32)func_80001FF0() * D_8823416C / 2);
    StageFade_StartFromOpaque(count);
    if (count != 0) {
        i = 0;
        do {
            func_80064D28();
            func_8821D3FC();
            i++;
        } while (i != count);
    }
}
/* mkdraft:func_8821D550 end */

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/31/fragment31_1900C0/func_8821D64C.s")

/* mkdraft:func_8821D74C begin */
extern s32 func_80001FF0(void);
extern void StageFade_StartFromTransparent(s32);
extern void func_80064D28(void);
extern void func_8821D3FC(void);
extern f32 D_88234188;

void func_8821D74C(void) {
    u16 count;
    s32 i;
    count = (u16)((f32)func_80001FF0() * D_88234188 / 2);
    StageFade_StartFromTransparent(count);
    if (count != 0) {
        i = 0;
        do {
            func_80064D28();
            func_8821D3FC();
            i++;
        } while (i != count);
    }
}
/* mkdraft:func_8821D74C end */

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/31/fragment31_1900C0/func_8821D848.s")
#endif

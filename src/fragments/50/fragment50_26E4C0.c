#include "global.h"


#ifdef VERSION_US
#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/50/fragment50_26E4C0/func_86207A80.s")

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/50/fragment50_26E4C0/func_86207BC0.s")

/* mkdraft:func_86207D40 begin */
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

M2C_UNK func_80035A10(f32, f32, void *);            /* extern */

s32 func_86207D40(void *arg0, f32 arg1, void *arg2, void *arg3, f32 *arg4) {
    f32 sp18;
    f32 temp_fa0;
    f32 temp_fa1;
    f32 temp_ft5;
    f32 temp_fv1;
    f32 var_fv0;
    f32 var_fv0_2;
    f32 var_fv0_3;
    s32 var_v1;

    var_v1 = 0;
    M2C_FIELD(arg3, f32 *, 0) = (f32) (M2C_FIELD(arg0, f32 *, 0) - M2C_FIELD(arg2, f32 *, 0));
    temp_fa1 = M2C_FIELD(arg3, f32 *, 0);
    M2C_FIELD(arg3, f32 *, 4) = (f32) (M2C_FIELD(arg0, f32 *, 4) - M2C_FIELD(arg2, f32 *, 4));
    M2C_FIELD(arg3, f32 *, 8) = (f32) (M2C_FIELD(arg0, f32 *, 8) - M2C_FIELD(arg2, f32 *, 8));
    if (temp_fa1 > 0.0f) {
        var_fv0 = temp_fa1;
    } else {
        var_fv0 = -temp_fa1;
    }
    if (var_fv0 <= arg1) {
        temp_fa0 = M2C_FIELD(arg3, f32 *, 4);
        if (temp_fa0 > 0.0f) {
            var_fv0_2 = temp_fa0;
        } else {
            var_fv0_2 = -temp_fa0;
        }
        if (var_fv0_2 <= arg1) {
            temp_fv1 = M2C_FIELD(arg3, f32 *, 8);
            if (temp_fv1 > 0.0f) {
                var_fv0_3 = temp_fv1;
            } else {
                var_fv0_3 = -temp_fv1;
            }
            if (var_fv0_3 <= arg1) {
                temp_ft5 = sqrtf((temp_fa1 * temp_fa1) + (temp_fa0 * temp_fa0) + (temp_fv1 * temp_fv1));
                if (temp_ft5 <= arg1) {
                    if ((temp_fa1 == 0.0f) && (temp_fa0 == 0.0f) && (temp_fv1 == 0.0f)) {
                        M2C_FIELD(arg3, f32 *, 0) = 1.0f;
                    } else {
                        sp18 = temp_ft5;
                        func_80035A10(temp_fa0, temp_fa1, arg3);
                    }
                    var_v1 = 1;
                    *arg4 = arg1 - temp_ft5;
                }
            }
        }
    }
    return var_v1;
}
/* mkdraft:func_86207D40 end */

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/50/fragment50_26E4C0/func_86207EB0.s")

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/50/fragment50_26E4C0/func_86207F34.s")
#endif

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

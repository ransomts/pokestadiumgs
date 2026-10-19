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

M2C_UNK func_87E0E3EC(u8 *);                      /* extern */

s32 func_87E0E714(u8 *arg0) {
    s32 sp24;
    s32 temp_v0;
    s32 var_v1;

    sp24 = 0;
    if ((M2C_FIELD(arg0, s32 *, 0x3F8) == 0) && (M2C_FIELD(arg0, s32 *, 0x3DC) == 0)) {
        sp24 = 1;
    } else {
        if ((((f32) func_80001FF0() / 60.0f) * 20.0f) >= 0.0f) {
            var_v1 = (s32) ((((f32) func_80001FF0() / 60.0f) * 20.0f) + 0.5f);
        } else {
            var_v1 = (s32) ((((f32) func_80001FF0() / 60.0f) * 20.0f) - 0.5f);
        }
        if ((var_v1 + 1) < M2C_FIELD(arg0, s32 *, 0x3FC)) {
            temp_v0 = M2C_FIELD(arg0, s32 *, 0x3F8);
            if (temp_v0 > 0) {
                M2C_FIELD(arg0, s32 *, 0x3F8) = (s32) (temp_v0 - 1);
                func_87E0E3EC(arg0);
                M2C_FIELD(arg0, s32 *, 0x3FC) = 0;
            }
        }
    }
    return sp24;
}

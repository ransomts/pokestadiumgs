s32 func_87C01FE0(void **arg0, s32 arg1);
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

void func_87C01E98(u8 *arg0, f32 arg1, f32 arg2) {
    f32 temp_fv0;
    f32 temp_fv1;
    s16 *temp_a1;
    s32 temp_v0;
    s32 temp_v0_2;

    temp_a1 = M2C_FIELD(arg0, s16 **, 4);
    if (temp_a1 != NULL) {
        temp_v0 = func_87C0177C(temp_a1);
        M2C_FIELD(arg0, s16 *, 0x16) = (s16) (s32) ((f32) temp_v0 * arg1);
        if (M2C_FIELD(arg0, s16 *, 0x16) >= temp_v0) {
            M2C_FIELD(arg0, s16 *, 0x16) = (s16) (temp_v0 - 1);
        }
        func_87C019B0(arg0, M2C_FIELD(arg0, s16 **, 4)[M2C_FIELD(arg0, s16 *, 0x16)]);
        temp_v0_2 = func_87C01FE0((u8 **) arg0, (s32) M2C_FIELD(arg0, s16 *, 0x14));
        temp_fv0 = (f32) temp_v0_2;
        temp_fv1 = temp_fv0 * arg2;
        M2C_FIELD(arg0, f32 *, 8) = temp_fv1;
        if (temp_fv0 <= temp_fv1) {
            M2C_FIELD(arg0, f32 *, 8) = (f32) (temp_v0_2 - 1);
        }
    }
}

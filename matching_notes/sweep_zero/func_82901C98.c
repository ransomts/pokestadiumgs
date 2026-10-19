f32 Math_StepToF(f32, f32, f32, f32);
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

M2C_UNK func_829012E4();                            /* extern */

void func_82901C98(void) {
    switch (M2C_FIELD(D_82918868, u8 *, 0x32)) {    /* irregular */
    case 1:
        M2C_FIELD(D_82918868, s16 *, 0x24) = 0;
        M2C_FIELD(D_82918868, s16 *, 0x26) = -0x6000;
        M2C_FIELD(D_82918868, u8 *, 0x32) = 2U;
        M2C_FIELD(D_82918868, f32 *, 0x2C) = 0.0f;
        break;
    case 2:
        M2C_FIELD(D_82918868, f32 *, 0x2C) = Math_StepToF(M2C_FIELD(D_82918868, f32 *, 0x2C), 220.0f, 55.0f, 55.0f);
        if (M2C_FIELD(D_82918868, f32 *, 0x2C) == 220.0f) {
            M2C_FIELD(D_82918868, u8 *, 0x32) = 3U;
        }
        break;
    case 4:
        M2C_FIELD(D_82918868, s16 *, 0x24) = 0;
        M2C_FIELD(D_82918868, s16 *, 0x26) = -0x6000;
        M2C_FIELD(D_82918868, u8 *, 0x32) = 5U;
        M2C_FIELD(D_82918868, f32 *, 0x2C) = 220.0f;
        break;
    case 5:
        M2C_FIELD(D_82918868, f32 *, 0x2C) = Math_StepToF(M2C_FIELD(D_82918868, f32 *, 0x2C), 0.0f, 55.0f, 55.0f);
        if (M2C_FIELD(D_82918868, f32 *, 0x2C) == 0.0f) {
            M2C_FIELD(D_82918868, u8 *, 0x32) = 6U;
        }
        break;
    }
    func_829012E4();
}

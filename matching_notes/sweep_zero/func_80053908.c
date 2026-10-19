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

s32 func_8005370C();                                /* extern */

void func_80053908(s32 arg0, s32 arg1) {
    s32 temp_s0;

    temp_s0 = func_8005370C();
    if (temp_s0 < func_80053230(arg0)) {
        switch (arg0) {
        case 16:
            M2C_FIELD(func_80050E88(0, D_800972C0, arg1), s8 *, 1) = (s8) (temp_s0 + 1);
            break;
        case 17:
            M2C_FIELD(func_80050F60(0, arg1), s8 *, 1) = (s8) (temp_s0 + 1);
            break;
        case 18:
            M2C_FIELD(func_80051028(0, arg1), s8 *, 1) = (s8) (temp_s0 + 1);
            break;
        case 22:
            M2C_FIELD(func_80051208(0), s8 *, 1) = (s8) (temp_s0 + 1);
            break;
        case 24:
            M2C_FIELD(func_800512E0(0), s8 *, 1) = (s8) (temp_s0 + 1);
            break;
        case 25:
            M2C_FIELD(func_8005134C(0), s8 *, 1) = (s8) (temp_s0 + 1);
            break;
        case 26:
            M2C_FIELD(func_800513B8(0), s8 *, 1) = (s8) (temp_s0 + 1);
            break;
        case 27:
            M2C_FIELD(func_80051424(0), s8 *, 1) = (s8) (temp_s0 + 1);
            break;
        }
        func_80051BF0(arg0, (u8 *) arg1, 2);
    }
}

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

u8 func_8005370C(s32 arg0, s32 arg1) {
    u8 var_v1;

    var_v1 = 0;
    switch (arg0) {
    case 16:
        var_v1 = M2C_FIELD(func_80050E88(0, D_800972C0, arg1), u8 *, 1);
        break;
    case 17:
        var_v1 = M2C_FIELD(func_80050F60(0, arg1), u8 *, 1);
        break;
    case 18:
        var_v1 = M2C_FIELD(func_80051028(0, arg1), u8 *, 1);
        break;
    case 19:
        var_v1 = 0x2D;
        break;
    case 22:
        var_v1 = M2C_FIELD(func_80051208(0), u8 *, 1);
        break;
    case 23:
        var_v1 = 0x1E;
        break;
    case 24:
        var_v1 = M2C_FIELD(func_800512E0(0), u8 *, 1);
        break;
    case 25:
        var_v1 = M2C_FIELD(func_8005134C(0), u8 *, 1);
        break;
    case 26:
        var_v1 = M2C_FIELD(func_800513B8(0), u8 *, 1);
        break;
    case 27:
        var_v1 = M2C_FIELD(func_80051424(0), u8 *, 1);
        break;
    case 28:
        var_v1 = 0x32;
        break;
    case 29:
        var_v1 = 0x64;
        break;
    case 30:
        var_v1 = 0x46;
        break;
    }
    return var_v1;
}

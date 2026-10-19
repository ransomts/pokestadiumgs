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

s32 func_8004C874(M2C_UNK, s32);                    /* extern */
M2C_UNK func_88002AA8(u8 *, M2C_UNK, u8 *, M2C_UNK, s32, s32, s32, s32, s32, s32, s32, s32, s32, M2C_UNK *); /* extern */
extern M2C_UNK D_88006020;

void func_889034DC(u8 *arg0) {
    s32 temp_v0;
    s32 var_s0;
    u8 *var_s1;

    var_s0 = 0;
    var_s1 = arg0;
    do {
        temp_v0 = func_8004C874(0x45, var_s0);
        var_s0 += 1;
        var_s1 += 4;
        M2C_FIELD(var_s1, s32 *, 0x34) = temp_v0;
    } while (var_s0 != 2);
    func_88002AA8(arg0 + 4, 0, arg0 + 0x38, 2, 8, 1, 6, 0xF, 0x10, 0xD, 0x10, 0, 0, &D_88006020);
    M2C_FIELD(arg0, s32 *, 0x40) = 0;
}

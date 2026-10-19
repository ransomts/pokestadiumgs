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

M2C_UNK func_8AF00130(M2C_UNK);                     /* extern */
M2C_UNK func_8AF1B5D4();                            /* extern */
extern u8 *D_8AF263C0;

s16 func_8AF086C4(s16 arg0) {
    u16 temp_v0;

    temp_v0 = M2C_FIELD(D_8AF263C0, u16 *, 8);
    if (temp_v0 & 0x800) {
        D_8AF2C960 = 1;
    } else if (temp_v0 & 0x200) {
        D_8AF2C960 = 3;
    } else if (temp_v0 & 0x100) {
        D_8AF2C960 = 4;
    } else if (temp_v0 & 0x8000) {
        func_8AF00130(0xBF);
        arg0 = 0x15;
        func_8AF1B5D4();
    }
    return arg0;
}

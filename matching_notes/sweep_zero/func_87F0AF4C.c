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

M2C_UNK func_80007328(M2C_UNK *, s32);              /* extern */
M2C_UNK func_800088DC();                            /* extern */
extern M2C_UNK D_800D0510;

void func_87F0AF4C(u8 *arg0) {
    M2C_UNK (*temp_v0)(u8 *);
    u8 *temp_s0;
    u8 *var_s1;

    var_s1 = M2C_FIELD(arg0, u8 **, 0xC);
    if (var_s1 != NULL) {
        do {
            temp_s0 = M2C_FIELD(var_s1, u8 **, 0x38);
            func_80007328(&D_800D0510, M2C_FIELD(temp_s0, s32 *, 4));
            temp_v0 = M2C_FIELD(temp_s0, M2C_UNK (**)(u8 *), 8);
            if (temp_v0 != NULL) {
                temp_v0(temp_s0);
            }
            var_s1 = M2C_FIELD(var_s1, u8 **, 4);
        } while (var_s1 != NULL);
    }
    func_800088DC();
}

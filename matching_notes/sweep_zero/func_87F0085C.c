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

M2C_UNK func_800495BC(M2C_UNK, M2C_UNK, M2C_UNK *, s32); /* extern */
M2C_UNK func_800496A4(M2C_UNK, M2C_UNK);            /* extern */
M2C_UNK func_8004972C(M2C_UNK, M2C_UNK, M2C_UNK, s32); /* extern */
M2C_UNK func_800498C4();                            /* extern */
extern M2C_UNK D_87F11430;
extern M2C_UNK D_87F11434;

void func_87F0085C(void) {
    s32 temp_a3;

    if (!(M2C_FIELD(D_87F11768, s32 *, 8) & 1) && (M2C_FIELD(D_87F11768, s32 *, 0x10) < 4)) {
        func_800498C4();
        func_800496A4(8, 0);
        func_8004972C(0xFF, 0xFF, 0, (s32) (M2C_FIELD(D_87F11768, f32 *, 0x14) * 255.0f));
        temp_a3 = M2C_FIELD(D_87F11768, s32 *, 0x10);
        if (temp_a3 == 0) {
            func_800495BC(0x80, 0x6E, &D_87F11430, temp_a3);
            return;
        }
        func_800495BC(0x90, 0x6E, &D_87F11434, temp_a3);
    }
}

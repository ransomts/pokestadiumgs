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

s32 func_8004C874(M2C_UNK, s16);                    /* extern */
M2C_UNK func_88903C50(s32, M2C_UNK, M2C_UNK, M2C_UNK, s32, s32, s32, s32, s32, s32, u8 *, M2C_UNK *, void (*)()); /* extern */
extern M2C_UNK D_88000E4C;

void func_88501274(s16 arg0) {
    func_88903C50(func_8004C874(0x34, arg0), 0x141, 0x108, 4, 0xFF, 0xAA, 0x8C, 0, 2, M2C_FIELD(D_8850D6D0, s32 *, 4) + 0x2C, D_8850D6D0 + 0x88, &D_88000E4C, func_8000612C);
}

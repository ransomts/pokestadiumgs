void func_80023A3C(s32, s32, s32);
extern u8 D_84195248[];
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

void func_84137DB8(void) {
    if (M2C_FIELD(D_84195280, u8 *, 0x4D80) != M2C_FIELD(D_84195280, u8 *, 0x4D81)) {
        if (D_84195278 == 3) {
            func_84137D04(0U);
            func_84137D04(1U);
            if ((M2C_FIELD(D_84195248, u8 *, 0xE) == 5) || (M2C_FIELD(D_84195248, u8 *, 0x26) == 5)) {
                func_84147228(0x17, 0U, 0, 7, 1);
                func_84147228(0x17, 0U, 0, 0xB, 4);
            } else {
                func_84147228(0x17, 0U, 0, 7, 0);
                func_84147228(0x17, 0U, 0, 0xB, 2);
            }
            func_84147228(0x17, 0U, 0, 4, 4);
            func_80023A3C(0x27, 0, 0);
        }
        D_84195278 = 2;
        func_84134968();
    }
}

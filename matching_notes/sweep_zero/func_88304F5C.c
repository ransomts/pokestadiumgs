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

M2C_UNK func_88300B48();                            /* extern */
extern s32 D_88006860;
extern u8 *D_88308DE8;
extern s32 D_886017AC;

void func_88304F5C(void) {
    D_886017AC = 1;
    M2C_FIELD(D_88308DF0, u16 *, 0) = (u16) (M2C_FIELD(D_88308DF0, u16 *, 0) | 4);
    M2C_FIELD(D_88308DE8, u16 *, 0) = (u16) (M2C_FIELD(D_88308DE8, u16 *, 0) | 4);
    M2C_FIELD(D_88308DE8, u16 *, 0) = (u16) (M2C_FIELD(D_88308DE8, u16 *, 0) | 2);
    M2C_FIELD(M2C_FIELD(D_88308DF0, u8 **, 0x1C), s32 *, 0x4C) = 0x10000;
    M2C_FIELD(M2C_FIELD(D_88308DE8, u8 **, 0x1C), s32 *, 0x4C) = 0x10000;
    if (D_88006860 == 1) {
        do {
            func_80064D28();
            func_88300B48();
            func_88301C00(1);
        } while (D_88006860 == 1);
    }
}

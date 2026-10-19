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

M2C_UNK func_8004972C(M2C_UNK, M2C_UNK, M2C_UNK, s16); /* extern */
M2C_UNK func_8820AAD0(s16, s16, s32);               /* extern */
M2C_UNK func_88230D80(s16 *, s16 *);                /* extern */
extern u8 *D_8800EF54;
extern s16 D_8800EF58;

void func_882321F8(void) {
    s16 sp1E;
    s16 sp1C;
    u8 *sp18;

    sp18 = D_8800EF54;
    func_88230D80(&sp1E, &sp1C);
    if (sp1E < D_8800EF58) {
        func_8004972C(0xFF, 0xFF, 0xFF, sp1C);
        func_8820AAD0((s16) ((M2C_FIELD(sp18, u8 *, 5) * 0x129) + 0x4D), (s16) ((M2C_FIELD(sp18, s8 *, 4) * 0x1B) + 0x80), M2C_FIELD(sp18, s32 *, 0) + 8);
    }
}

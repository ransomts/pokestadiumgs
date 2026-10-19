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

M2C_UNK func_8AC0619C(M2C_UNK *, u16);              /* extern */
M2C_UNK func_8AC06220(M2C_UNK *, u16);              /* extern */
M2C_UNK func_8AC0686C(M2C_UNK *, s16);              /* extern */
M2C_UNK func_8AF00130(M2C_UNK);                     /* extern */
s32 func_8AF0326C(u8 *);                          /* extern */
extern u8 *D_8AF263C0;
extern u8 *D_8AF279A0;
extern u16 D_8AF2BDC6;
extern M2C_UNK D_8AF39840;
extern M2C_UNK D_8AF398B8;
extern M2C_UNK D_8AF39930;

s16 func_8AF20DB0(void) {
    s16 sp1E;
    u8 *sp18;

    sp1E = 0x1A;
    sp18 = D_8AF279A0;
    if ((func_8AF0326C(D_8AF279A0) == 0) && (M2C_FIELD(D_8AF263C0, u16 *, 8) & 0x4000)) {
        func_8AF00130(3);
        sp1E = 0x18;
    }
    func_8AC0686C(&D_8AF39930, M2C_FIELD(sp18, s16 *, 0x38));
    func_8AC0619C(&D_8AF39840, D_8AF2BDC6);
    func_8AC06220(&D_8AF398B8, D_8AF2BDC6);
    return sp1E;
}

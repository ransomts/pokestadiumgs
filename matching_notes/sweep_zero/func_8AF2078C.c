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
M2C_UNK func_8AF1F978();                            /* extern */
extern u8 *D_8AF263C0;
extern u8 *D_8AF27970;
extern u16 D_8AF2BDC6;
extern s16 D_8AF39430;
extern M2C_UNK D_8AF39498;
extern M2C_UNK D_8AF39510;
extern M2C_UNK D_8AF39588;

s16 func_8AF2078C(void) {
    s16 sp1E;
    u8 *sp18;
    u16 temp_v1;

    sp1E = 0x1D;
    sp18 = D_8AF27970;
    if ((func_8AF0326C(D_8AF27970) == 0) && (M2C_FIELD(sp18, s16 *, 0x3A) == 0)) {
        temp_v1 = M2C_FIELD(D_8AF263C0, u16 *, 8);
        if (temp_v1 & 0x4000) {
            func_8AF00130(3);
            func_8AF1FC80();
            sp1E = 0x1C;
        } else if (D_8AF39430 == 0) {
            switch (D_8AF39228) {                   /* irregular */
            case 0:
                if (temp_v1 & 0x400) {
                    func_8AF00130(1);
                    D_8AF39228 = 1;
                    func_8AF1FC80();
                    func_8AF1F978();
                }
                break;
            case 1:
                if (temp_v1 & 0x800) {
                    func_8AF00130(1);
                    D_8AF39228 = 0;
                    func_8AF1FC80();
                    func_8AF1F978();
                }
                break;
            }
        }
    }
    func_8AC0686C(&D_8AF39588, M2C_FIELD(sp18, s16 *, 0x38));
    func_8AC0619C(&D_8AF39498, D_8AF2BDC6);
    func_8AC06220(&D_8AF39510, D_8AF2BDC6);
    return sp1E;
}

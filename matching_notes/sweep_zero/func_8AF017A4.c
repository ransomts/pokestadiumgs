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

M2C_UNK func_8AF0282C(M2C_UNK *, M2C_UNK);          /* extern */
extern M2C_UNK D_8AF2BDE0;
extern M2C_UNK D_8AF2BDF8;
extern M2C_UNK D_8AF2BE10;
extern s32 D_8AF2BE24;
extern M2C_UNK D_8AF2BE28;
extern s32 D_8AF2BE3C;
extern M2C_UNK D_8AF2BE48;
extern s32 D_8AF2BE5C;
extern M2C_UNK D_8AF2BE60;
extern s32 D_8AF2BE74;

void func_8AF017A4(void) {
    s32 var_v0;

    if (M2C_FIELD(&D_8AF2BDE0, s32 *, 0x14) != 0) {
        func_8AF0282C(&D_8AF2BDE0, 1);
        func_8AF0282C(&D_8AF2BDE0, 2);
    }
    if (M2C_FIELD(&D_8AF2BDF8, s32 *, 0x14) != 0) {
        func_8AF0282C(&D_8AF2BDF8, 1);
        func_8AF0282C(&D_8AF2BDF8, 2);
    }
    if (D_8AF2BE24 != 0) {
        func_8AF0282C(&D_8AF2BE10, 1);
    }
    if (D_8AF2BE3C != 0) {
        func_8AF0282C(&D_8AF2BE28, 1);
    }
    if (D_8AF2BE5C != 0) {
        func_8AF0282C(&D_8AF2BE48, 1);
    }
    var_v0 = M2C_FIELD(&D_8AF2BE60, s32 *, 0x14);
    if (var_v0 != 0) {
        func_8AF0282C(&D_8AF2BE60, 1);
        var_v0 = D_8AF2BE74;
    }
    if (var_v0 != 0) {
        func_8AF0282C(&D_8AF2BE60, 2);
    }
    if (D_8AF2BE5C != 0) {
        func_8AF0282C(&D_8AF2BE48, 2);
    }
    if (D_8AF2BE3C != 0) {
        func_8AF0282C(&D_8AF2BE28, 2);
    }
    if (D_8AF2BE24 != 0) {
        func_8AF0282C(&D_8AF2BE10, 2);
    }
}

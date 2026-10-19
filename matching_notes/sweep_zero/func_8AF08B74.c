extern s16 D_8AF2CB74;
extern s16 D_8AF2CB1C;
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

M2C_UNK func_8AF01020(s16, s16);                    /* extern */
extern u8 *D_8AF2CB20;
extern u8 *D_8AF2CB24;

void func_8AF08B74(void) {
    s16 sp1E;
    s16 sp1C;

    M2C_FIELD(D_8AF2CB20, u16 *, 2) = (u16) (M2C_FIELD(D_8AF2CB20, u16 *, 2) & 0xFFFD);
    M2C_FIELD(D_8AF2CB24, u16 *, 2) = (u16) (M2C_FIELD(D_8AF2CB24, u16 *, 2) & 0xFFFD);
    func_8AF08B68((u8 *) D_8AF2CB40, -0x3C5FA501, -0x1E3C7301);
    func_8AF08B68((u8 *) D_8AF2CB44, -0x3C5FA501, -0x1E3C7301);
    if (D_8AF2CB74 == 0) {
        switch (D_8AF2CB1C) {                       /* irregular */
        case 0:
            sp1E = M2C_FIELD(D_8AF2CB20, s16 *, 8);
            sp1C = M2C_FIELD(D_8AF2CB20, s16 *, 0xA);
            func_8AF08B68((u8 *) D_8AF2CB40, -0xFF01, -0xFF01);
            break;
        case 1:
            sp1E = M2C_FIELD(D_8AF2CB24, s16 *, 8);
            sp1C = M2C_FIELD(D_8AF2CB24, s16 *, 0xA);
            func_8AF08B68((u8 *) D_8AF2CB44, -0xFF01, -0xFF01);
            break;
        }
        func_8AF01020(sp1E, sp1C);
    }
}

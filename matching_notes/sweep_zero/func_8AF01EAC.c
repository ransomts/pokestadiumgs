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

M2C_UNK StageFade_StartFromOpaque(M2C_UNK);         /* extern */
M2C_UNK func_800086A4(M2C_UNK);                     /* extern */
s32 func_80043678(s32);                             /* extern */
M2C_UNK func_8AC0080C(M2C_UNK);                     /* extern */
M2C_UNK func_8AF0007C(s32);                         /* extern */
M2C_UNK func_8AF01910();                            /* extern */
s32 func_8AF01D7C(s32);                             /* extern */
M2C_UNK func_8AF0282C(M2C_UNK *, M2C_UNK);          /* extern */
extern s32 D_8AF2BA84;
extern s32 D_8AF2BA8C;
extern s16 D_8AF2BAC8;
extern M2C_UNK D_8AF2BDE0;
extern M2C_UNK D_8AF2BDF8;
extern M2C_UNK D_8AF2BE10;
extern M2C_UNK D_8AF2BE28;
extern M2C_UNK D_8AF2BE48;
extern M2C_UNK D_8AF2BE60;
extern s32 D_8AF2BE80;

void func_8AF01EAC(void) {
    s32 temp_v0;
    s32 var_s1;

    var_s1 = 0;
    func_800086A4(2);
    StageFade_StartFromOpaque(5);
    D_8AF2BDD0 = 0;
    D_8AF2BDD4 = 0;
    D_8AF2BE78 = 0;
    D_8AF2BE80 = 0;
    func_8AF0282C(&D_8AF2BDE0, 0);
    func_8AF0282C(&D_8AF2BDF8, 0);
    func_8AF0282C(&D_8AF2BE10, 0);
    func_8AF0282C(&D_8AF2BE28, 0);
    func_8AF0282C(&D_8AF2BE48, 0);
    func_8AF0282C(&D_8AF2BE60, 0);
    func_8AC0080C(0xC);
    do {
        func_8AF0007C(var_s1);
        func_8AF01750();
        if (D_8AF2BAC8 == 1) {
            D_8AF2BA8C = func_80043678(D_8AF2BA84);
            D_8AF2BAC8 = 2;
        }
        func_8AF01910();
        temp_v0 = func_8AF01D7C(var_s1);
        var_s1 = temp_v0;
    } while (temp_v0 != 4);
}

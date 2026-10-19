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

M2C_UNK func_80008648();                            /* extern */
M2C_UNK func_800088DC();                            /* extern */
M2C_UNK func_80049064(M2C_UNK, M2C_UNK, M2C_UNK, s32); /* extern */
M2C_UNK func_800496A4(M2C_UNK, M2C_UNK);            /* extern */
M2C_UNK func_800498C4();                            /* extern */
M2C_UNK func_800499EC();                            /* extern */
s32 func_8004C874(M2C_UNK, M2C_UNK);                /* extern */
M2C_UNK func_88004180();                            /* extern */
M2C_UNK func_8850C998();                            /* extern */
extern s32 D_880068B8;
extern s32 D_8850D670;

void func_88500494(void) {
    func_800088DC();
    if (D_880068B8 != 0) {
        func_8850C998();
        if (D_8850D670 == 1) {
            func_800498C4();
            func_800496A4(0x10, 2);
            func_80049064(0x140, 0x168, 1, func_8004C874(0x34, 0));
            func_800499EC();
        }
    }
    func_88004180();
    func_80008648();
}

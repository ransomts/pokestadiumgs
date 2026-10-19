extern s32 D_882345F4;
extern u32 D_88234910;
extern s32 D_880068B8;
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

M2C_UNK func_800226C0(M2C_UNK);                     /* extern */
M2C_UNK func_88004990(u8, M2C_UNK);                 /* extern */
M2C_UNK func_882026A4(s32, s32);                    /* extern */

void func_8822B580(s32 arg0) {
    func_800226C0(0x47);
    func_882026A4(D_882345F4, arg0);
    M2C_FIELD(D_88234910, s32 *, 0x190) = 1;
    M2C_FIELD(D_88234910, s32 *, 0x194) = arg0;
    if (M2C_FIELD(D_88234910, s32 *, 0x18C) != 0) {
        func_88004990(*M2C_FIELD(D_88234910, u8 **, 0), 8);
    } else {
        func_88004990(*M2C_FIELD(D_88234910, u8 **, 0), 0);
    }
    D_880068B8 = 1;
}

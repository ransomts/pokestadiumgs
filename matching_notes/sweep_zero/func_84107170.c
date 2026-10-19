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

M2C_UNK func_84100020(u8 *, M2C_UNK);             /* extern */
extern s32 D_84190194;
extern s32 D_841901A4;

void func_84107170(u8 *arg0, u8 *arg1) {
    u8 *temp_s1;

    temp_s1 = M2C_FIELD(arg0, u8 **, 0);
    M2C_FIELD(arg1, u8 **, 0x10) = temp_s1;
    M2C_FIELD(arg1, u8 *, 0x7C) = (u8) M2C_FIELD(arg0, u8 *, 9);
    M2C_FIELD(arg1, u16 *, 0x68) = (u16) M2C_FIELD(arg0, u16 *, 0xA);
    M2C_FIELD(arg1, s32 *, 8) = (s32) D_84190194;
    if (M2C_FIELD(temp_s1, s32 *, 4) & 0x10) {
        func_84100020(arg1, 1);
    }
    if (M2C_FIELD(temp_s1, s32 *, 4) & 0x400) {
        func_84100020(arg1, 0x40);
    }
    if (M2C_FIELD(temp_s1, s32 *, 4) & 8) {
        func_84100020(arg1, 0x200);
    }
    if (M2C_FIELD(temp_s1, s32 *, 4) & 0x20000000) {
        func_84100020(arg1, 0x10000);
    }
    if (M2C_FIELD(temp_s1, s32 *, 4) & 4) {
        func_84100020(arg1, 0x100);
    }
    if (M2C_FIELD(temp_s1, s32 *, 4) & 0x100) {
        func_84100020(arg1, 0x400);
    }
    if (M2C_FIELD(temp_s1, s32 *, 4) & 0x10000000) {
        func_84100020(arg1, 0x20000);
    }
    if (M2C_FIELD(temp_s1, s32 *, 4) & 0x08000000) {
        func_84100020(arg1, 0x8000);
    }
    if (M2C_FIELD(temp_s1, s32 *, 4) & 0x80000000) {
        func_84100020(arg1, 0x40000);
    }
    if (M2C_FIELD(temp_s1, s32 *, 8) & 4) {
        func_84100020(arg1, 0x80000);
        D_841901A4 = 0;
    }
}

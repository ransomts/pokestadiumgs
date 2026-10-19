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

M2C_UNK GfxImage_FillCurrent(M2C_UNK *, M2C_UNK);   /* extern */
M2C_UNK func_80007444(M2C_UNK *, M2C_UNK, M2C_UNK, M2C_UNK, s32, s32); /* extern */
M2C_UNK func_80008648();                            /* extern */
M2C_UNK func_800088DC();                            /* extern */
M2C_UNK func_800495F8(); /* extern */
M2C_UNK func_800496A4(M2C_UNK, M2C_UNK);            /* extern */
M2C_UNK func_8004972C(M2C_UNK, M2C_UNK, M2C_UNK, M2C_UNK); /* extern */
M2C_UNK func_800498C4();                            /* extern */
M2C_UNK func_800499EC();                            /* extern */
extern M2C_UNK D_800D0510;
extern u8 *D_88A01C64;
extern M2C_UNK D_88D00940;
extern M2C_UNK D_88D0094C;
extern M2C_UNK D_88D00984;
extern M2C_UNK D_88D00990;
extern M2C_UNK D_88D009BC;
extern M2C_UNK D_88D009EC;
extern M2C_UNK D_88D00A20;
extern M2C_UNK D_88D00A44;
extern M2C_UNK D_88D00A50;
extern M2C_UNK D_88D00A5C;
extern M2C_UNK D_88D00A68;

void func_88D00178(void) {
    func_800088DC();
    GfxImage_FillCurrent(&D_800D0510, 1);
    func_80007444(&D_800D0510, 0x32, 0x5A, 0x136, 0x67, 0x7C67);
    func_800498C4();
    func_800496A4(0x10, 2);
    func_8004972C(0x32, 0x80, 0xFF, 0xFF);
    func_800495F8(0x3C, 0x64, 0, &D_88D00940);
    func_8004972C(0xFF, 0xC8, 0xC8, 0xFF);
    func_800495F8(0x32, 0xD2, 0, &D_88D0094C);
    func_800495F8(0x32, 0xF0, 0, &D_88D00984);
    func_800495F8(0x32, 0x10E, 0, &D_88D00990);
    func_8004972C(0xFF, 0xFF, 0xFF, 0xFF);
    func_800495F8(0x32, 0x136, 0, &D_88D009BC);
    func_8004972C(0xFF, 0x64, 0x64, 0xFF);
    func_800495F8(0x32, 0x168, 0, &D_88D009EC);
    func_800495F8(0x32, 0x186, 0, &D_88D00A20);
    func_800496A4(8, 1);
    func_8004972C(0xFF, 0xFF, 0xFF, 0xFF);
    func_800495F8(0x3C, 0x8C, 0, &D_88D00A44);
    func_800495F8(0x3C, 0xA5, 0, &D_88D00A50);
    func_800495F8(0x15E, 0x8C, 2, &D_88D00A5C, (s32) M2C_FIELD(D_88A01C64, u8 *, 0xF4));
    func_800495F8(0x15E, 0xA5, 2, &D_88D00A68, (s32) M2C_FIELD(D_88A01C64, u8 *, 0xFC));
    func_800499EC();
    func_80008648();
}

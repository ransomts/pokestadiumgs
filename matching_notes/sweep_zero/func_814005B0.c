extern u8 *D_814077C0;
extern u8 *D_814077D0[];
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

M2C_UNK func_800476A0(M2C_UNK *, M2C_UNK);          /* extern */
M2C_UNK func_800476FC(M2C_UNK *, M2C_UNK);          /* extern */
M2C_UNK func_80047738(M2C_UNK, u8 *, M2C_UNK, M2C_UNK); /* extern */
M2C_UNK func_8004C4B0(M2C_UNK);                     /* extern */
u8 *func_8004C990(M2C_UNK, M2C_UNK);                /* extern */
extern u8 *D_814077C4;
extern u8 *D_814077C8;
extern u8 *D_814077CC;
extern u8 *D_814077D4;
extern u8 *D_814077D8;
extern u8 *D_814077DC;
extern u8 *D_814077E0;
extern u8 *D_814077E4;
extern u8 *D_814077E8;
extern u8 *D_814077EC;
extern u8 *D_814077F0;
extern u8 *D_814077F4;
extern u8 *D_814077F8;
extern u8 *D_814077FC;
extern u8 *D_81407800;
extern u8 *D_81407804;
extern u8 *D_81407808;
extern u8 *D_8140780C;
extern u8 *D_81407810;
extern u8 *D_81407814;
extern u8 *D_81407818;
extern u8 *D_8140781C;
extern u8 *D_81407820;
extern u8 *D_81407824;
extern u8 *D_81407828;
extern M2C_UNK D_81420B20;

void func_814005B0(void) {
    func_8004C8C0(0x31);
    func_8004C4B0(0x11);
    func_8004C4B0(8);
    func_8004C4B0(0xC);
    func_8004C4B0(0xD);
    func_8004C4B0(6);
    func_8004C8C0(0x32);
    func_8004C8C0(0x3D);
    func_8004C8C0(0x3F);
    func_8004C8C0(0x3E);
    func_8004C8C0(0x40);
    func_8004C8C0(0x33);
    D_814077C0 = func_8004C990(0x3F, 0);
    D_814077C4 = func_8004C990(0x40, 0);
    D_814077C8 = func_8004C990(0x3E, 0);
    D_814077CC = func_8004C990(0x3E, 1);
    *D_814077D0 = func_8004C990(0x3D, 0);
    D_814077D4 = func_8004C990(0x3D, 1);
    D_814077D8 = func_8004C990(0x3D, 2);
    D_814077DC = func_8004C990(0x3D, 3);
    D_814077E8 = func_8004C990(0x3F, 4);
    D_814077EC = func_8004C990(0x3F, 7);
    D_814077F0 = func_8004C990(0x3F, 9);
    D_814077F4 = func_8004C990(0x3F, 0xA);
    D_814077F8 = func_8004C990(0x3F, 1);
    D_814077FC = func_8004C990(0x3F, 2);
    D_81407800 = func_8004C990(0x3F, 3);
    D_81407804 = func_8004C990(0x3F, 5);
    D_81407808 = func_8004C990(0x3F, 6);
    D_8140780C = func_8004C990(0x3F, 8);
    D_81407810 = func_8004C990(0x3F, 0xB);
    D_81407814 = func_8004C990(0x33, 1);
    D_81407818 = func_8004C990(0x33, 4);
    D_8140781C = func_8004C990(0x33, 6);
    D_81407820 = func_8004C990(0x33, 0);
    D_81407824 = func_8004C990(0x33, 3);
    D_81407828 = func_8004C990(0x33, 5);
    D_814077E0 = func_8004C990(0x32, 0);
    D_814077E4 = func_8004C990(0x32, 1);
    func_800476A0(&D_81420B20, 1);
    func_800476FC(&D_81420B20, 1);
    func_80047738(0, func_8004C990(0x31, 0), 0, 0);
}

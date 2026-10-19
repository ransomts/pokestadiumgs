void _bcopy(void *, void *, s32);
void func_841352DC(u8 arg0);
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

M2C_UNK func_8003F6E0(u8 *, u8 *, u8);              /* extern */

void func_8412B1D4(void) {
    s32 var_a1;
    u8 *temp_v0;
    u8 *temp_v0_2;
    u8 *temp_v0_3;
    u8 temp_a0;

    M2C_FIELD(D_84195208[D_841951BC], s8 *, 0x26) = 0;
    M2C_FIELD(D_84195208[D_841951BC], s8 *, 0x27) = 0;
    temp_v0 = D_84195208[D_841951BD];
    if ((M2C_FIELD(temp_v0, u8 *, 0x11) & 8) || (M2C_FIELD(temp_v0, u8 *, 0xF) & 0x60)) {
        func_84134E7C(0U, 1U);
        func_841366C4(D_841951BC, -1);
        func_84135B40(0xB5U);
        return;
    }
    temp_v0_2 = D_84195208[D_841951BC];
    M2C_FIELD(temp_v0_2, u8 *, 0x11) = (u8) (M2C_FIELD(temp_v0_2, u8 *, 0x11) | 8);
    M2C_FIELD(D_84195208[D_841951BC], s8 *, 0x15) = 0;
    M2C_FIELD(D_84195208[D_841951BC], s8 *, 0x25) = 0;
    *D_84195208[D_841951BC] = *D_84195208[D_841951BD];
    M2C_FIELD(D_84195208[D_841951BC], u16 *, 0x2C) = (u16) M2C_FIELD(D_84195208[D_841951BD], u16 *, 0x2C);
    M2C_FIELD(D_84195208[D_841951BC], u16 *, 0x2E) = (u16) M2C_FIELD(D_84195208[D_841951BD], u16 *, 0x2E);
    M2C_FIELD(D_84195208[D_841951BC], u8 *, 0x2A) = (u8) M2C_FIELD(D_84195208[D_841951BD], u8 *, 0x2A);
    _bcopy(D_84195208[D_841951BD] + 5, D_84195208[D_841951BC] + 5, 4);
    _bcopy(D_84195208[D_841951BD] + 1, D_84195208[D_841951BC] + 1, 2);
    _bcopy(D_84195208[D_841951BD] + 0x32, D_84195208[D_841951BC] + 0x32, 0xA);
    _bcopy(D_84195208[D_841951BD] + 0x3C, D_84195208[D_841951BC] + 0x3C, 0xA);
    _bcopy(D_84195208[D_841951BD] + 0x1E, D_84195208[D_841951BC] + 0x1E, 7);
    func_8003F6E0(D_84195208[D_841951BC] + 0x50, D_84195200[D_841951BC], *D_84195208[D_841951BD]);
    var_a1 = 0;
    do {
        temp_v0_3 = &D_84195208[D_841951BC][var_a1];
        temp_a0 = M2C_FIELD(temp_v0_3, u8 *, 5);
        var_a1 = (var_a1 + 1) & 0xFF;
        if (temp_a0 == 0) {
            M2C_FIELD(temp_v0_3, s8 *, 9) = 0;
        } else if (temp_a0 == 0xA6) {
            M2C_FIELD(temp_v0_3, s8 *, 9) = 1;
        } else {
            M2C_FIELD(temp_v0_3, s8 *, 9) = 5;
        }
    } while (var_a1 < 4);
    func_841366C4(D_841951BC, -1);
    func_84135B40(0x3DU);
    func_841352DC(D_841951BC);
}

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

s32 func_80062CE0(u8);                              /* extern */
extern u8 D_841951C0;

void func_8412BDF0(void) {
    M2C_FIELD(D_84195208[D_841951BC], s8 *, 0x26) = 0;
    M2C_FIELD(D_84195208[D_841951BC], s8 *, 0x27) = 0;
    if (func_8412BD3C() != 0) {
        M2C_FIELD(&D_84195208[D_841951BC][D_841951C0], u8 *, 5) = (u8) M2C_FIELD(D_84195208[D_841951BD], u8 *, 0x26);
        M2C_FIELD(&D_84195208[D_841951BC][D_841951C0], s8 *, 9) = 5;
        func_84136678(D_841951BC, -1);
        func_8004C54C(0x1EU, func_80062CE0(M2C_FIELD(D_84195208[D_841951BD], u8 *, 0x26)));
        func_84135B00(0x85U);
    } else {
        func_84136678(D_841951BC, -1);
        if (M2C_FIELD(D_84195208[D_841951BD], u8 *, 0xD) & 4) {
            func_84135B00(0xB6U);
        } else {
            func_84135B00(0xB5U);
        }
    }
    func_84124594(D_841951BC);
    func_84136CA8();
}

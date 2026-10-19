void func_84124798(u8);
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

s32 func_800630C0(u8);                              /* extern */
M2C_UNK func_841562BC(u8, u8, M2C_UNK);             /* extern */

void func_84130EA8(void) {
    func_84124798(D_841951BD);
    func_841248DC(D_841951BD);
    func_84124954(D_841951BD);
    func_841249D8(D_841951BD);
    if (D_841951BF == 6) {
        func_84136678(D_841951BC, -1);
        func_84135B00(0x88U);
    }
    func_84124A7C();
    func_84136A9C(D_841951BD, -1, (s16) ((s16) D_841951E8 * -1), 2U);
    if ((s16) D_841951E8 == M2C_FIELD(D_84195200[D_841951BD], u16 *, 0x28)) {
        if (func_84127140(D_841951BD) != 0) {
            func_84136218(D_841951BD, 1U);
        } else if (func_84127140(D_841951BC) != 0) {
            func_84136218(D_841951BC, 2U);
        }
    }
    if ((s16) D_841951E8 > 0) {
        if (M2C_FIELD(D_841951F8[D_841951BC], u8 *, 0x49A) != 0) {
            if (func_800630C0(D_841951BF) != 0) {
                func_841562BC(D_841951BD, M2C_FIELD(D_841951F8[D_841951BD], u8 *, 0xA), 1);
            } else {
                func_841562BC(D_841951BD, M2C_FIELD(D_841951F8[D_841951BD], u8 *, 0xA), 4);
            }
        }
        if (M2C_FIELD(D_841951F8[D_841951BD], u8 *, 0x49A) != 0) {
            if (func_800630C0(D_841951BF) != 0) {
                func_841562BC(D_841951BC, M2C_FIELD(D_841951F8[D_841951BC], u8 *, 0xA), 0);
            } else {
                func_841562BC(D_841951BC, M2C_FIELD(D_841951F8[D_841951BC], u8 *, 0xA), 3);
            }
        }
    }
    func_84124604(D_841951BD, D_841951BF);
    func_84136D40(2U);
    func_84136CA8();
    func_84124A14(D_841951BD);
}

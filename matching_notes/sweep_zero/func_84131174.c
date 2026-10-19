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

void func_84131174(void) {
    s32 temp_v1;
    u8 *var_v0;
    u8 var_a2;

    func_84136678(D_841951BD, -1);
    func_84124798(D_841951BD);
    var_v0 = D_84195208[D_841951BC];
    if (!(M2C_FIELD(var_v0, u8 *, 0xF) & 4)) {
        func_841248DC(D_841951BD);
        func_84135034(0U, 1U);
        func_84136D40(1U);
    } else {
        var_a2 = M2C_FIELD(var_v0, u8 *, 0x12);
        if (var_a2 == 1) {
            func_84136678(D_841951BD, -1);
            if (D_841951BF != 0xFB) {
                func_8004C594(1, M2C_FIELD(D_84195208[D_841951BC], s32 *, 0x4C));
                func_84135B00(0x9CU);
            }
            func_84124954(D_841951BD);
            var_v0 = D_84195208[D_841951BC];
            var_a2 = M2C_FIELD(var_v0, u8 *, 0x12);
        }
        temp_v1 = M2C_FIELD(var_v0, s32 *, 0x4C);
        func_84135034((temp_v1 - var_a2) & 0xFF, (temp_v1 - 1) & 0xFF);
    }
    func_841249D8(D_841951BD);
    func_84124A7C();
    func_84136A9C(D_841951BD, -1, (s16) ((s16) D_841951E8 * -1), 2U);
    func_84124604(D_841951BD, D_841951BF);
    func_84136CA8();
    func_84124A14(D_841951BD);
}

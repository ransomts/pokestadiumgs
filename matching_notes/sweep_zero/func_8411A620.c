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

s32 func_8411E244(u8 *, M2C_UNK);                   /* extern */

void func_8411A620(u8 *arg0) {
    if ((M2C_FIELD(arg0, s8 *, 0x7F6) != 3) && (func_841133EC((s32) arg0) == 0)) {
        if (M2C_FIELD(arg0, s8 *, 0x7F6) == 0) {
            if (M2C_FIELD(arg0, u8 *, 0x619) == M2C_FIELD(arg0, s16 *, 0x7E8)) {
                if (func_8411E244(arg0, 0x119) != 0xFF) {
                    func_8410890C(0x119, (s32) arg0);
                    func_80023A3C(7, (s32) M2C_FIELD(arg0, s16 *, 0x1A), 0);
                }
                func_84112580((s32) arg0);
            }
            if (M2C_FIELD(arg0, u8 *, 0x61A) == M2C_FIELD(arg0, s16 *, 0x7E8)) {
                func_80023A3C(6, 0, 0);
                func_8410890C(0x11A, (s32) arg0);
                func_8411FEE8(0);
                M2C_FIELD(arg0, s8 *, 0x7F6) = 2;
            }
        }
        if ((M2C_FIELD(arg0, u16 *, 0x7EC) & 1) && ((M2C_FIELD(arg0, u8 *, 0x61A) + 0x19) == M2C_FIELD(arg0, s16 *, 0x7E8))) {
            func_8411EE74(arg0);
        }
        func_8411A310(arg0);
    }
}

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

s32 func_8006A3E0();                                /* extern */
s32 func_8006AC70();                                /* extern */
M2C_UNK func_84113590(s32);                         /* extern */
extern s32 D_841910D8;

void func_8411D65C(void) {
    s32 temp_v1;

    temp_v1 = func_8006A3E0() & 0xFF00;
    switch (temp_v1) {                              /* irregular */
    case 0x300:
        if ((D_841910D8 >= 9) && (D_841910D8 < 0xD)) {
            func_84113590(5);
            return;
        }
        if (func_8006AC70() == 0) {
            func_84113590(5);
            return;
        }
        func_84113590((func_8003570C() % 5U) & 0xFF);
        return;
    case 0x0:
        func_84113590((func_8003570C() % 5U) & 0xFF);
        return;
    case 0x400:
        func_84113590((func_8003570C() % 5U) & 0xFF);
        return;
    case 0x200:
        if ((D_841910D8 >= 0x17) && (D_841910D8 < 0x1D)) {
            func_84113590((func_8003570C() % 5U) & 0xFF);
            return;
        }
        func_84113590(5);
        return;
    case 0x600:
        func_84113590(5);
        return;
    default:
        func_84113590((func_8003570C() % 5U) & 0xFF);
        return;
    }
}

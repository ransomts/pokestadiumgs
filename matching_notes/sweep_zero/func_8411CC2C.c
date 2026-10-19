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

M2C_UNK func_84113590(M2C_UNK);                     /* extern */

void func_8411CC2C(s32 arg0) {
    func_84112158(D_84191208, 0xFC);
    func_80024480(M2C_FIELD(D_84191208, s16 *, 0x1A), 4);
    func_84112158(D_8419120C, 0xFB);
    M2C_FIELD(D_84191208, s16 *, 0x7EA) = 0;
    M2C_FIELD(D_8419120C, s16 *, 0x7EA) = 0;
    M2C_FIELD(D_84191208, s8 *, 0x7F6) = 1;
    M2C_FIELD(D_841911E0, s16 *, 0x98) = 0;
    func_84111348(arg0, 0x1A);
    func_841112C8();
    func_84113590(4);
    func_8410C304(M2C_FIELD(D_841911E4, u8 **, 0), D_8419120C, (s32) M2C_FIELD(D_841911E4, s16 *, 0x98));
    func_8411EF08((u8 *) arg0);
    M2C_FIELD(arg0, s8 *, 0x1D) = 0;
    func_8411EF20((u8 *) D_8419120C);
    func_8411EE74((u8 *) D_8419120C);
    func_84112564(arg0);
    M2C_FIELD((arg0 + (D_841911F4 * 4)), s32 *, 0x5C8) = (s32) D_84183D50;
}

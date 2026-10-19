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

M2C_UNK func_8005053C(u8 *, s32);                 /* extern */
M2C_UNK func_80050578(u8 *, s32);                 /* extern */

void func_87F0AA80(TreeNode_80050428 *arg0, s32 arg1, s32 arg2) {
    u8 *sp24;
    s32 sp20;
    s32 sp1C;
    s32 temp_v0;

    sp24 = func_8005049C(arg0, arg1);
    temp_v0 = MainPool_AllocState(main_pool_get_available(), 0);
    sp1C = temp_v0;
    sp20 = MainPool_AllocAligned(temp_v0, 0xC, 4);
    MainPool_FinalizeAllocation(sp1C);
    if (sp24 == NULL) {
        func_87F0A5F0(arg1);
        return;
    }
    func_8005053C(sp24, sp20);
    func_80050578(sp24, arg2);
}
/* Warning: struct TreeNode_80050428 is not defined (only forward-declared) */

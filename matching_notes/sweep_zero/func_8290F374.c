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

M2C_UNK GfxRect_DrawTextured(s16, s16, s16, s16, s32, s32, s32, s32, s32); /* extern */
M2C_UNK func_800459AC(s32, u8, u8, u16, s32, s32, s32, s32, s32, s32, s32, s32, s32); /* extern */
s32 func_8004CA60(u8 *);                          /* extern */

void func_8290F374(s16 arg0, s16 arg1, s16 arg2, s16 arg3, u8 *arg4) {
    if (arg4 != NULL) {
        func_800459AC(func_8004CA60(arg4), M2C_FIELD(arg4, u8 *, 4), M2C_FIELD(arg4, u8 *, 5), M2C_FIELD(arg4, u16 *, 0), (s32) M2C_FIELD(arg4, u16 *, 2), 1, 0, 2, 2, 0, 0, 0, 0);
    }
    GfxRect_DrawTextured(arg0, arg1, arg2, arg3, 0, 0, 0x400, 0x400, 0);
}

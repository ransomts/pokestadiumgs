extern u8 **D_88234970;
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

s32 MainPool_AllocAligned(s32, s32, M2C_UNK);       /* extern */
s32 MainPool_AllocState(s32, M2C_UNK);              /* extern */
M2C_UNK MainPool_FinalizeAllocation(s32);           /* extern */
u8 **Util_Malloc(M2C_UNK);                          /* extern */
M2C_UNK func_8004C8C0(M2C_UNK);                     /* extern */
s32 func_8004C990(M2C_UNK, M2C_UNK);                /* extern */
s8 func_800532C4(M2C_UNK);                          /* extern */
s32 func_8005CAA4(M2C_UNK);                         /* extern */
s32 main_pool_get_available();                      /* extern */
M2C_UNK main_pool_push_state(M2C_UNK);              /* extern */

void func_8822E950(void) {
    s32 sp24;
    s32 sp20;
    s32 temp_v0;

    main_pool_push_state(0x50495550);
    D_88234970 = Util_Malloc(0x30);
    sp20 = func_8005CAA4(0x21);
    if (func_800532C4(0x11) < sp20) {
        M2C_FIELD(D_88234970, s8 *, 0x1C) = func_8005CAA4(0x21);
    } else {
        M2C_FIELD(D_88234970, s8 *, 0x1C) = func_800532C4(0x11);
    }
    temp_v0 = MainPool_AllocState(main_pool_get_available(), 0);
    sp24 = temp_v0;
    M2C_FIELD(D_88234970, s32 *, 0xC) = MainPool_AllocAligned(temp_v0, (u8) M2C_FIELD(D_88234970, s8 *, 0x1C) * 0xC80, 8);
    MainPool_FinalizeAllocation(sp24);
    func_8004C8C0(0x9A);
    M2C_FIELD(D_88234970, s32 *, 0x10) = func_8004C990(0x9A, 0);
    func_8004C8C0(0xF1);
    M2C_FIELD(D_88234970, s32 *, 0x14) = func_8004C990(0xF1, 0);
    func_8004C8C0(0xF3);
    M2C_FIELD(D_88234970, s32 *, 0x18) = func_8004C990(0xF3, 0);
}

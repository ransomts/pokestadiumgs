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

M2C_UNK Gfx_FreeDisplayListBuffers();               /* extern */
M2C_UNK Gfx_InitDisplayListBuffers(M2C_UNK, M2C_UNK); /* extern */
M2C_UNK Util_Free(u8 *);                            /* extern */
s32 func_800082E0(M2C_UNK, M2C_UNK, M2C_UNK, M2C_UNK, s32, s32); /* extern */
M2C_UNK func_80008514(s32);                         /* extern */
M2C_UNK func_80008574();                            /* extern */
s32 func_80047588(M2C_UNK, M2C_UNK);                /* extern */
M2C_UNK func_80047610();                            /* extern */
M2C_UNK func_8004C09C(M2C_UNK);                     /* extern */
M2C_UNK func_8004C398();                            /* extern */
M2C_UNK func_881023CC();                            /* extern */
M2C_UNK func_881024F8(s32);                         /* extern */
M2C_UNK main_pool_pop_state(M2C_UNK);               /* extern */
M2C_UNK main_pool_push_state(M2C_UNK);              /* extern */
extern s32 D_8800687C;

s32 func_88102E78(s32 arg0, M2C_UNK arg1) {
    s32 sp24;

    main_pool_push_state(0x4C41424F);
    Gfx_InitDisplayListBuffers(0x14000, 0);
    sp24 = func_800082E0(1, 0, 2, 0, 2, 1);
    func_8004C09C(7);
    D_8800687C = func_80047588(0xC, 0);
    func_881024F8(arg0);
    func_80008514(sp24);
    func_88102234();
    func_88102338();
    func_881023CC();
    func_80008574();
    Util_Free(D_88104E80);
    func_80047610();
    func_8004C398();
    Gfx_FreeDisplayListBuffers();
    main_pool_pop_state(0x4C41424F);
    return D_88006860;
}

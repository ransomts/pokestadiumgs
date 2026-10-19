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

M2C_UNK Font_EnableLineBreak();                     /* extern */
M2C_UNK Gfx_FreeDisplayListBuffers();               /* extern */
M2C_UNK Gfx_InitDisplayListBuffers(M2C_UNK, M2C_UNK); /* extern */
M2C_UNK Util_Free(s32);                             /* extern */
s32 func_800082E0(M2C_UNK, M2C_UNK, M2C_UNK, M2C_UNK, s32, s32); /* extern */
M2C_UNK func_80008514(s32);                         /* extern */
M2C_UNK func_80008574();                            /* extern */
M2C_UNK func_8002602C();                            /* extern */
s32 func_80047588(M2C_UNK, M2C_UNK);                /* extern */
M2C_UNK func_80047610();                            /* extern */
M2C_UNK func_8004C09C(M2C_UNK);                     /* extern */
M2C_UNK func_8004C398();                            /* extern */
M2C_UNK func_88304F5C();                            /* extern */
M2C_UNK func_88305020();                            /* extern */
M2C_UNK func_883051E4(s32, s32);                    /* extern */
M2C_UNK main_pool_pop_state(M2C_UNK);               /* extern */
M2C_UNK main_pool_push_state(M2C_UNK);              /* extern */
extern s32 D_80128C60;
extern s32 D_88006860;
extern s32 D_8800687C;
extern s32 D_88601890;
extern s32 D_88601898;

s32 func_883059F0(s32 arg0, s32 arg1) {
    s32 sp24;
    s32 sp20;

    main_pool_push_state(0x424F4F4B);
    Gfx_InitDisplayListBuffers(0x14000, 0);
    sp24 = func_800082E0(1, 0, 2, 0, 2, 1);
    func_8004C09C(7);
    D_8800687C = func_80047588(0x1C, 0);
    Font_EnableLineBreak();
    func_883051E4(arg0, arg1);
    func_80008514(sp24);
    func_88304E60();
    func_88304F5C();
    func_88305020();
    func_80008574();
    main_pool_pop_state(0x70617274);
    func_80047610();
    func_8004C398();
    Gfx_FreeDisplayListBuffers();
    if (D_88006860 == 7) {
        Util_Free(D_88601898);
        func_8002602C();
        Util_Free(D_88601890);
    }
    sp20 = (s32) *D_88308DF8;
    main_pool_pop_state(0x424F4F4B);
    D_80128C60 = D_88006860;
    return sp20;
}

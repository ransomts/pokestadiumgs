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

M2C_UNK Asset_LoadToSegment(u32, M2C_UNK *, M2C_UNK *, M2C_UNK); /* extern */
M2C_UNK Gfx_FreeDisplayListBuffers();               /* extern */
M2C_UNK Gfx_InitDisplayListBuffers(M2C_UNK, M2C_UNK); /* extern */
M2C_UNK StageFade_StartFromOpaque(M2C_UNK);         /* extern */
s32 func_800082E0(M2C_UNK, M2C_UNK, M2C_UNK, M2C_UNK, s32, s32); /* extern */
M2C_UNK func_80008514(s32);                         /* extern */
M2C_UNK func_80008574();                            /* extern */
M2C_UNK func_80035424(M2C_UNK);                     /* extern */
M2C_UNK func_80047610();                            /* extern */
M2C_UNK func_8004C09C(M2C_UNK);                     /* extern */
M2C_UNK func_8004C398();                            /* extern */
M2C_UNK func_8410AA18(s32, s32, u8 *);              /* extern */
M2C_UNK func_8413D37C();                            /* extern */
M2C_UNK func_8413DE28(s32, s32);                    /* extern */
M2C_UNK func_8414831C(u8);                          /* extern */
M2C_UNK main_pool_pop_state(M2C_UNK);               /* extern */
M2C_UNK main_pool_push_state(M2C_UNK);              /* extern */
extern M2C_UNK D_1000000;
extern M2C_UNK D_446E30;
extern M2C_UNK D_447D00;
extern u8 D_8419A0A2;
extern s8 D_8419A0A3;

u8 func_8413E2EC(s32 arg0, s32 arg1) {
    s32 sp24;

    main_pool_push_state(0x504D4254);
    Gfx_InitDisplayListBuffers(0x20000, 0);
    sp24 = func_800082E0(0, 1, 3, 1, 2, 1);
    Asset_LoadToSegment((u32) ((s32) &D_1000000 & 0x0F000000) >> 0x18, &D_446E30, &D_447D00, 0);
    func_8004C09C(0x43);
    func_8413DE28(arg0, arg1);
    func_8410AA18(sp24, arg0, D_84199D80);
    func_8414831C(*D_8419A0A0);
    func_84136564();
    func_80008514(sp24);
    StageFade_StartFromOpaque(0xA);
    D_8419A0A3 = 0xA;
    func_8413D37C();
    func_80008574();
    func_80035424(4);
    func_80047610();
    func_8004C398();
    Gfx_FreeDisplayListBuffers();
    main_pool_pop_state(0x504D4254);
    return D_8419A0A2;
}

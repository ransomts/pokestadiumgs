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
s32 func_800082E0(M2C_UNK, M2C_UNK, M2C_UNK, M2C_UNK, s32, s32); /* extern */
M2C_UNK func_80008514(s32);                         /* extern */
M2C_UNK func_80008574();                            /* extern */
M2C_UNK func_80027EE0(M2C_UNK);                     /* extern */
M2C_UNK func_80047588(s32, M2C_UNK);                /* extern */
M2C_UNK func_80047610();                            /* extern */
M2C_UNK func_8004C09C(M2C_UNK);                     /* extern */
M2C_UNK func_8004C398();                            /* extern */
M2C_UNK func_8004C8C0(M2C_UNK);                     /* extern */
M2C_UNK func_86706E34();                            /* extern */
M2C_UNK func_8670A790();                            /* extern */
M2C_UNK func_87F00030();                            /* extern */
M2C_UNK func_87F01F34(u8 *);                      /* extern */
M2C_UNK func_87F06EAC(M2C_UNK, M2C_UNK *, u8 *);  /* extern */
s32 func_87F08E3C(s32, M2C_UNK);                    /* extern */
M2C_UNK func_87F0C980();                            /* extern */
M2C_UNK func_87F0F480(u8 *);                      /* extern */
M2C_UNK main_pool_pop_state(M2C_UNK);               /* extern */
M2C_UNK main_pool_push_state(M2C_UNK);              /* extern */
extern M2C_UNK D_1000000;
extern M2C_UNK D_446E30;
extern M2C_UNK D_447D00;
extern s32 D_8670BB90;
extern s32 D_8670C958;
extern M2C_UNK D_8670D880;
extern s32 D_8670D888;
extern s32 D_8670D8D8;

s32 func_8670A96C(s32 arg0, u8 *arg1) {
    s32 sp24;

    D_8670FEB0 = arg1;
    if (M2C_FIELD(D_8670FEB0, u8 *, 0x2180) == 4) {
        func_80027EE0(0xFFF);
    }
    main_pool_push_state(0x4D523033);
    Gfx_InitDisplayListBuffers(0x20000, 0);
    sp24 = func_800082E0(0, 1, 3, 1, 2, 1);
    func_8004C09C(0x123);
    func_87F06EAC(0x6C, &D_8670D880, D_8670FEB0);
    func_8004C8C0(0xE2);
    func_8004C8C0(0xE3);
    func_8004C8C0(0x1B2);
    func_8004C8C0(0x133);
    func_8004C8C0(0xE0);
    func_8004C8C0(0x3E);
    func_8004C8C0(0x182);
    func_8004C8C0(0x183);
    func_8004C8C0(0xCD);
    D_8670C96C = func_87F08E3C(func_8004C990(0xE3, 0), 0x0F000000);
    D_8670C958 = func_87F08E3C(func_8004C990(0xCD, 0), 0x0F000000);
    func_80047588(D_8670D888 | 5 | D_8670D8D8, 0);
    Asset_LoadToSegment((u32) ((s32) &D_1000000 & 0x0F000000) >> 0x18, &D_446E30, &D_447D00, 0);
    func_87F00030();
    func_87F01F34(D_8670FEB0);
    func_87F0C980();
    func_86706E34();
    func_80008514(sp24);
    func_8670A790();
    func_80008574();
    func_80047610();
    func_8004C398();
    Gfx_FreeDisplayListBuffers();
    main_pool_pop_state(0x4D523033);
    func_87F0F480(D_8670FEB0);
    func_80027EE0(0xFFE);
    return D_8670BB90;
}

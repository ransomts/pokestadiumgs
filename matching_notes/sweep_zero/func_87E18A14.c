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

s32 MainPool_AllocState(s32, M2C_UNK);              /* extern */
M2C_UNK MainPool_FinalizeAllocation(s32);           /* extern */
s32 func_80040E80(s32, M2C_UNK *);                  /* extern */
M2C_UNK func_8004C8C0(M2C_UNK, s32);                /* extern */
M2C_UNK func_87E10E64(M2C_UNK);                     /* extern */
M2C_UNK func_87E10EA8(M2C_UNK);                     /* extern */
M2C_UNK func_87E10F2C(M2C_UNK);                     /* extern */
M2C_UNK func_87E13480(M2C_UNK);                     /* extern */
M2C_UNK func_87E13490();                            /* extern */
M2C_UNK func_87E134C0();                            /* extern */
M2C_UNK func_87E18828(u8 *);                      /* extern */
s32 main_pool_get_available();                      /* extern */
M2C_UNK main_pool_push_state(M2C_UNK);              /* extern */
extern M2C_UNK D_87E1B410;

void func_87E18A14(u8 *arg0, s32 arg1, s32 arg2) {
    s32 sp24;
    s32 temp_v0;

    main_pool_push_state(0x4D51414C);
    M2C_FIELD(arg0, s32 *, 0x28) = arg2;
    switch (arg1) {                                 /* irregular */
    default:
        M2C_FIELD(arg0, s32 *, 0) = 1;
        break;
    case 2:
        M2C_FIELD(arg0, s32 *, 0) = 0;
        break;
    case 1:
        M2C_FIELD(arg0, s32 *, 0) = 1;
        break;
    case 0:
        M2C_FIELD(arg0, s32 *, 0) = 2;
        break;
    }
    M2C_FIELD(arg0, s32 *, 4) = 0;
    M2C_FIELD(arg0, s32 *, 8) = 0;
    func_8004C8C0(0x1AA, arg1);
    temp_v0 = MainPool_AllocState(main_pool_get_available(), 0);
    sp24 = temp_v0;
    M2C_FIELD(arg0, s32 *, 0x24) = func_80040E80(temp_v0, &D_87E1B410);
    MainPool_FinalizeAllocation(sp24);
    func_87E18828(arg0);
    func_87E134C0();
    func_87E13490();
    func_87E13480(0);
    func_87E10E64(1);
    func_87E10EA8(-1);
    func_87E10F2C(-1);
}

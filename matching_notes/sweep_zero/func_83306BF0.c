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

s32 ModelAnim_IsFinished(M2C_UNK *);                /* extern */
M2C_UNK func_80024480(s32, M2C_UNK);                /* extern */
M2C_UNK func_8003F2C4(s32, M2C_UNK *, s32);         /* extern */
M2C_UNK func_8003F3BC(M2C_UNK *, s32);              /* extern */
M2C_UNK func_83300020(M2C_UNK);                     /* extern */
M2C_UNK func_833003B0(M2C_UNK);                     /* extern */
M2C_UNK func_83303640(M2C_UNK);                     /* extern */
extern u8 *D_83308E34;
extern s32 D_8330A4CC;
extern M2C_UNK D_8330A4D0;
extern s32 D_8330ABD8;

void func_83306BF0(void) {
    func_83300020(1);
    func_83303640(1);
    if ((ModelAnim_IsFinished(&D_8330A4D0) == 1) && ((M2C_FIELD(&D_8330A2B0, s32 *, 0xC) >= 0x5B) || (M2C_FIELD(D_83308E34, s16 *, 2) == -1))) {
        if (M2C_FIELD(&D_8330A2B0, s32 *, 0x30) == 0) {
            if (M2C_FIELD(&D_8330A2B0, s32 *, 0x48) == 1) {
                M2C_FIELD(&D_8330A2B0, s32 *, 0) = 9;
                func_80024480(D_8330ABD8, 4);
                func_8003F2C4(D_8330A4CC, &D_8330A4D0, M2C_FIELD(&D_8330A2B0, s32 *, 0x34));
                func_8003F3BC(&D_8330A4D0, M2C_FIELD(&D_8330A2B0, s32 *, 0x38));
                M2C_FIELD(&D_8330A2B0, s32 *, 0x30) = 1;
            }
        } else {
            func_8003F2C4(D_8330A4CC, &D_8330A4D0, 0);
            func_8003F3BC(&D_8330A4D0, 0);
            M2C_FIELD(&D_8330A2B0, s32 *, 0) = 9;
        }
        if (M2C_FIELD(&D_8330A2B0, s32 *, 0) == 9) {
            func_833003B0(4);
            M2C_FIELD(&D_8330A2B0, s32 *, 0xC) = 0;
        }
    }
}

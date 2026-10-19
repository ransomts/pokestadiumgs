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

M2C_UNK func_84100020(u8 *, M2C_UNK);             /* extern */
extern u8 *D_8418C950;

void func_84108E00(s32 arg0, s32 arg1) {
    s16 *temp_v1;
    s16 *temp_v1_2;
    s16 *temp_v1_3;
    s32 var_s1;
    u8 *temp_v0;
    u8 *temp_v0_2;
    u8 *temp_v0_3;
    u8 *temp_v0_4;
    u8 *temp_v0_5;
    u8 *var_s0;

    var_s0 = D_8418C950;
    var_s1 = 0;
    do {
        if ((M2C_FIELD(var_s0, s8 *, 0x98) != 0) && (arg0 == M2C_FIELD(var_s0, s32 *, 8))) {
            switch (arg1) {                         /* irregular */
            case 0:
                temp_v0 = M2C_FIELD(var_s0, u8 **, 0x10);
                if (temp_v0 != NULL) {
                    temp_v1 = M2C_FIELD(temp_v0, s16 **, 0x14);
                    if ((temp_v1 != NULL) && (*temp_v1 == 0xD3)) {
                        temp_v0_2 = M2C_FIELD(var_s0, u8 **, 0xC);
                        if (temp_v0_2 != NULL) {
                            M2C_FIELD(temp_v0_2, u8 *, 1) = (u8) (M2C_FIELD(temp_v0_2, u8 *, 1) & ~1);
                        }
                    }
                }
                break;
            case 1:
                temp_v0_3 = M2C_FIELD(var_s0, u8 **, 0x10);
                if (temp_v0_3 != NULL) {
                    temp_v1_2 = M2C_FIELD(temp_v0_3, s16 **, 0x14);
                    if ((temp_v1_2 != NULL) && (*temp_v1_2 == 0x13D)) {
                        temp_v0_4 = M2C_FIELD(var_s0, u8 **, 0xC);
                        if (temp_v0_4 != NULL) {
                            M2C_FIELD(temp_v0_4, u8 *, 1) = (u8) (M2C_FIELD(temp_v0_4, u8 *, 1) & ~1);
                        }
                    }
                }
                break;
            case 2:
                temp_v0_5 = M2C_FIELD(var_s0, u8 **, 0x10);
                if (temp_v0_5 != NULL) {
                    temp_v1_3 = M2C_FIELD(temp_v0_5, s16 **, 0x14);
                    if ((temp_v1_3 != NULL) && (*temp_v1_3 == 0x12)) {
                        func_84100020(var_s0, 0x100000);
                    }
                }
                break;
            }
        }
        var_s1 += 1;
        var_s0 += 0x9C;
    } while (var_s1 != 0x12C);
}

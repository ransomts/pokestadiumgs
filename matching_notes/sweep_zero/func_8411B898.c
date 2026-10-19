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

void func_8411B898(u8 *arg0) {
    s8 temp_v0;
    u16 temp_v0_2;
    u16 temp_v0_3;

    temp_v0 = M2C_FIELD(arg0, s8 *, 0x7F6);
    switch (temp_v0) {                              /* switch 1; irregular */
    case 1:                                         /* switch 1 */
        M2C_FIELD(arg0, s16 *, 0x7E8) = 0;
        M2C_FIELD(arg0, s8 *, 0x7F6) = 2;
        if (M2C_FIELD(D_841911E0, s16 *, 0x98) != 0x21) {
            M2C_FIELD(arg0, s16 *, 0x7EA) = 0;
            M2C_FIELD(D_841911E0, s16 *, 0x98) = 0;
            func_84111348((s32) arg0, 0);
            return;
        }
        return;
    case 2:                                         /* switch 1 */
        if (M2C_FIELD(arg0, s16 *, 0x7E8) == 5) {
            temp_v0_2 = M2C_FIELD(D_84193DD0, u16 *, 4);
            switch (temp_v0_2) {                    /* switch 2; irregular */
            case 45:                                /* switch 2 */
                func_84112158((s32) arg0, 0xFB);
                break;
            case 46:                                /* switch 2 */
                func_84112464(arg0);
                break;
            case 47:                                /* switch 2 */
                func_84112324(arg0);
                break;
            }
            M2C_FIELD(arg0, s16 *, 0x7E8) = 0;
            M2C_FIELD(arg0, s8 *, 0x7F6) = 3;
            func_84112564((s32) arg0);
            return;
        }
        break;
    case 3:                                         /* switch 1 */
        temp_v0_3 = M2C_FIELD(D_84193DD0, u16 *, 4);
        switch (temp_v0_3) {                        /* switch 3; irregular */
        case 45:                                    /* switch 3 */
            if (M2C_FIELD(arg0, s16 *, 0x7E8) == 0x3C) {
                func_841206D0(arg0);
                func_8411FEE8(0);
                M2C_FIELD(arg0, s8 *, 0x7F6) = 6;
                return;
            }
            break;
        case 47:                                    /* switch 3 */
            if (M2C_FIELD(arg0, s16 *, 0x7E8) == 6) {
                func_8410890C(0x100, (s32) arg0);
            }
            func_84112418(arg0);
            if (M2C_FIELD(arg0, s16 *, 0x7E8) == 0x3C) {
                M2C_FIELD(arg0, u16 *, 0x7F4) = (u16) (M2C_FIELD(arg0, u16 *, 0x7F4) & 0xFFFE);
                func_841206D0(arg0);
                func_8411FEE8(0);
                M2C_FIELD(arg0, s8 *, 0x7F6) = 6;
                return;
            }
            break;
        case 46:                                    /* switch 3 */
            if (M2C_FIELD(arg0, s16 *, 0x7E8) == 6) {
                func_8410890C(0xFE, (s32) arg0);
            }
            if (M2C_FIELD(arg0, s16 *, 0x7E8) == 0x3C) {
                M2C_FIELD(arg0, u16 *, 0x7F4) = (u16) (M2C_FIELD(arg0, u16 *, 0x7F4) & 0xFFFD);
                func_841206D0(arg0);
                func_8411FEE8(0);
                M2C_FIELD(arg0, s8 *, 0x7F6) = 6;
            }
            break;
        }
        break;
    }
}

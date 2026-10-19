extern s16 D_8AF3500C;
extern s16 D_8AF34FAC;
extern s16 D_8AF34FAE;
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

extern u8 *D_8AF34FB0;
extern u8 *D_8AF34FB4;
extern u8 *D_8AF34FE0;
extern u8 *D_8AF34FE4;
extern u8 *D_8AF34FE8;
extern u8 *D_8AF34FEC;

void func_8AF17F18(void) {
    M2C_FIELD(D_8AF34FB0, u16 *, 2) = (u16) (M2C_FIELD(D_8AF34FB0, u16 *, 2) & 0xFFFE);
    M2C_FIELD(D_8AF34FB4, u16 *, 2) = (u16) (M2C_FIELD(D_8AF34FB4, u16 *, 2) & 0xFFFE);
    func_8AF17F0C(D_8AF34FE0, -0x3C5FA501, -0x1E3C7301);
    func_8AF17F0C(D_8AF34FE4, -0x3C5FA501, -0x1E3C7301);
    func_8AF17F0C(D_8AF34FE8, -0x3C5FA501, -0x1E3C7301);
    func_8AF17F0C(D_8AF34FEC, -0x3C5FA501, -0x1E3C7301);
    switch (D_8AF3500C) {                           /* switch 1; irregular */
    case 0:                                         /* switch 1 */
        switch (D_8AF34FAC) {                       /* switch 2; irregular */
        case 2:                                     /* switch 2 */
            M2C_FIELD(D_8AF34FB0, u16 *, 2) = (u16) (M2C_FIELD(D_8AF34FB0, u16 *, 2) | 1);
            func_8AF17F0C(D_8AF34FE8, -0xFF01, -0xFF01);
            return;
        case 3:                                     /* switch 2 */
            M2C_FIELD(D_8AF34FB4, u16 *, 2) = (u16) (M2C_FIELD(D_8AF34FB4, u16 *, 2) | 1);
            func_8AF17F0C(D_8AF34FEC, -0xFF01, -0xFF01);
            return;
        }
        break;
    case 7:                                         /* switch 1 */
        switch (D_8AF34FAE) {                       /* switch 3; irregular */
        case 0:                                     /* switch 3 */
            M2C_FIELD(D_8AF34FB0, u16 *, 2) = (u16) (M2C_FIELD(D_8AF34FB0, u16 *, 2) | 1);
            func_8AF17F0C(D_8AF34FE0, -0xFF01, -0xFF01);
            return;
        case 1:                                     /* switch 3 */
            M2C_FIELD(D_8AF34FB4, u16 *, 2) = (u16) (M2C_FIELD(D_8AF34FB4, u16 *, 2) | 1);
            func_8AF17F0C(D_8AF34FE4, -0xFF01, -0xFF01);
            return;
        }
        break;
    }
}

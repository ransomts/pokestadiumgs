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

M2C_UNK func_80008648();                            /* extern */
M2C_UNK func_800088DC();                            /* extern */
M2C_UNK func_8002B1CC();                            /* extern */
M2C_UNK func_80064D28();                            /* extern */
M2C_UNK func_8410A608();                            /* extern */
M2C_UNK func_8410A884();                            /* extern */
M2C_UNK func_8410A9B4();                            /* extern */
M2C_UNK func_84136D9C();                            /* extern */
M2C_UNK func_84137778();                            /* extern */
M2C_UNK func_8413C820();                            /* extern */
M2C_UNK func_8413CE84();                            /* extern */
M2C_UNK func_84145BA0(u8);                          /* extern */
M2C_UNK func_8414605C();                            /* extern */
M2C_UNK func_841482BC();                            /* extern */
extern u8 *D_80087200;
extern s32 D_84186150;
extern s32 D_84186174;
extern s8 D_8419A0A2;
extern u8 D_8419A0A3;

void func_8413D37C(void) {
    s32 var_s7;

    var_s7 = 0;
    if (M2C_FIELD(D_841951F0, u8 *, 0x9C2) == 2) {
        func_84147228(0x19, 0U, 0, 5, 3);
    }
    if (*D_8419A0A0 != 0) {
        func_84147228(0x1A, 0U, 0, 5, 3);
    } else {
        func_84134CBC(0U, 0x65U);
        func_84136CA8();
    }
    func_84147228(0x18, 0U, 0, 7, 1);
    func_84134920();
    if (*D_8419A0A0 != 0) {
        D_84195278 = 1;
    } else {
        M2C_FIELD((D_84195280 + (M2C_FIELD(D_84195280, u8 *, 0x4D81) * 0x280)), s8 *, -0x27E) = 0;
    }
    func_84147228(1, 0U, 0, 0xF, 0);
    func_84147228(1, 1U, 0, 0xF, 0);
    do {
        func_80064D28();
        func_8413CE84();
        if ((s32) D_8419A0A3 > 0) {
            D_8419A0A3 -= 1;
        }
        func_841482BC();
        func_8413C820();
        if (var_s7 == 0) {
            var_s7 = 1;
            func_8002B1CC();
        }
        if ((D_84195278 != 8) && (D_84186170 != 0)) {
            func_8410A608();
        }
        if (D_84195278 != 8) {
            func_841359D0();
        }
        func_84137778();
        func_84136D9C();
        func_84137CA4();
        func_800088DC();
        if (D_84186170 != 0) {
            func_8410A884();
        } else {
            func_8413C7C0();
        }
        switch (D_84195278) {
        case 8:
            func_8410A9B4();
            break;
        case 1:
        case 2:
        case 3:
        case 4:
        case 5:
        case 7:
            if (D_84186174 != 0) {
                func_84145BA0(*D_8419A0A0);
            }
            break;
        case 6:
            func_8414605C();
            break;
        }
        func_80008648();
        if ((*D_8419A0A0 != 0) && (D_8419A0A3 == 0) && (D_84195278 != 7) && (M2C_FIELD(D_80087200, u16 *, 8) & 0xD000)) {
            func_8413584C(0x14U);
        }
        if ((M2C_FIELD(D_841951F0, u8 *, 0x9C2) == 2) && (D_8419A0A3 == 0) && (D_84195278 != 7) && (M2C_FIELD(D_80087200, u16 *, 8) & 0x1000)) {
            func_8413584C(0x14U);
            D_8419A0A2 = 1;
        }
    } while (D_84186150 != 0);
    func_84134944();
}

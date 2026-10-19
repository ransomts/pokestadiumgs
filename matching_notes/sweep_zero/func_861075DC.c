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

M2C_UNK func_87F04314(M2C_UNK, M2C_UNK, M2C_UNK, M2C_UNK *, s32, s32, s32, s32, s32, s32, s32, s32); /* extern */
M2C_UNK func_87F0455C();                            /* extern */
extern M2C_UNK D_8610AA10;
extern M2C_UNK D_8610AA1C;
extern M2C_UNK D_8610AA28;
extern M2C_UNK D_8610AA34;
extern M2C_UNK D_8610AA40;
extern M2C_UNK D_8610AA4C;
extern M2C_UNK D_8610AA58;
extern M2C_UNK D_8610AA64;
extern M2C_UNK D_8610AA70;
extern M2C_UNK D_8610AA78;

void func_861075DC(void) {
    func_87F0455C();
    func_87F04314(0, 0, 0, &D_8610AA10, 0xC, 0, 0xA, 3, 3, D_8610AD20 + 0x9774, D_8610AD20 + 0x9778, D_8610AD20 + 0x977C);
    func_87F04314(0, 0, 1, &D_8610AA1C, 0xC, 1, 3, 1, 0, D_8610AD20 + 0x9780, D_8610AD20 + 0x9781, D_8610AD20 + 0x9782);
    func_87F04314(0, 0, 2, &D_8610AA28, 0xC, 2, 0xA, 3, 3, D_8610AD20 + 0x9784, D_8610AD20 + 0x9788, D_8610AD20 + 0x978C);
    func_87F04314(0, 0, 3, &D_8610AA34, 0xC, 3, 0xA, 1, 5, D_8610AD20 + 0x9790, D_8610AD20 + 0x9794, D_8610AD20 + 0x9798);
    func_87F04314(0, 0, 4, &D_8610AA40, 0xC, 4, 0xA, 2, 3, D_8610AD20 + 0x97A8, D_8610AD20 + 0x97AC, D_8610AD20 + 0x97B0);
    func_87F04314(0, 0, 5, &D_8610AA4C, 0xC, 5, 0xA, 2, 3, D_8610AD20 + 0x979C, D_8610AD20 + 0x97A0, D_8610AD20 + 0x97A4);
    func_87F04314(0, 0, 6, &D_8610AA58, 0xC, 6, 0xA, 4, 5, D_8610AD20 + 0x97CC, D_8610AD20 + 0x97D0, D_8610AD20 + 0x97D4);
    func_87F04314(0, 0, 7, &D_8610AA64, 0xC, 7, 0xA, 1, 5, D_8610AD20 + 0x97C0, D_8610AD20 + 0x97C4, D_8610AD20 + 0x97C8);
    func_87F04314(0, 0, 8, &D_8610AA70, 0xC, 8, 6, 7, 0, D_8610AD20 + 0x97B4, D_8610AD20 + 0x97B8, D_8610AD20 + 0x97BC);
    func_87F04314(0, 0, 9, &D_8610AA78, 0xC, 9, 0xA, 3, 3, D_8610AD20 + 0x9768, D_8610AD20 + 0x976C, D_8610AD20 + 0x9770);
}

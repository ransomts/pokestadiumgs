extern u16 D_8FC0C7A0;
extern u16 D_8FC0C79E;
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

void func_8FC02074(void) {
    u8 *temp_s0;

    temp_s0 = (M2C_FIELD(&D_8FC02830, u8 *, 2) * 0x10) + &D_8FC0244C;
    if (D_8FC0C7A0 & 0x800) {
        M2C_FIELD(&D_8FC02830, u8 *, 2) = (u8) M2C_FIELD(temp_s0, u8 *, 8);
        func_800226C0(1);
    } else if (D_8FC0C7A0 & 0x400) {
        M2C_FIELD(&D_8FC02830, u8 *, 2) = (u8) M2C_FIELD(temp_s0, u8 *, 9);
        func_800226C0(1);
    } else if (D_8FC0C7A0 & 0x200) {
        M2C_FIELD(&D_8FC02830, u8 *, 2) = (u8) M2C_FIELD(temp_s0, u8 *, 0xA);
        func_800226C0(1);
    } else if (D_8FC0C7A0 & 0x100) {
        M2C_FIELD(&D_8FC02830, u8 *, 2) = (u8) M2C_FIELD(temp_s0, u8 *, 0xB);
        func_800226C0(1);
    }
    if (D_8FC0C79E & 0x8000) {
        func_8FC01FC4(temp_s0);
        return;
    }
    if (D_8FC0C79E & 0x4000) {
        func_8FC01FBC();
    }
}

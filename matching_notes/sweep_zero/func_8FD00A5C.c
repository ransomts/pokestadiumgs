extern u8 D_8FD02188;
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

M2C_UNK Ui_DrawAnimatedTextureMarker(s16, s16);     /* extern */

void func_8FD00A5C(void) {
    switch (M2C_FIELD(&D_8FD02188, u8 *, 0)) {      /* irregular */
    case 0:
        Ui_DrawAnimatedTextureMarker(0x19, (s16) ((M2C_FIELD(&D_8FD02188, s16 *, 4) * 0xE) + 0x32));
        return;
    case 1:
        Ui_DrawAnimatedTextureMarker(0x4B, 0x46);
        return;
    case 2:
        if (M2C_FIELD(&D_8FD02188, s16 *, 2) == 0) {
            Ui_DrawAnimatedTextureMarker((s16) (M2C_FIELD(&D_8FD02188, u16 *, 0xC) - 0x19), 0x46);
            return;
        }
        Ui_DrawAnimatedTextureMarker((s16) (M2C_FIELD(&D_8FD02188, u16 *, 0xE) - 0x19), 0x46);
        return;
    }
}

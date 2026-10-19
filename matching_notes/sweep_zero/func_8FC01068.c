void _bcopy(s32 *, s32, s32);
void func_800226C0(s32);
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

M2C_UNK Deck_WriteEntries(u32 *, M2C_UNK, s32);     /* extern */
M2C_UNK Dma_CopyChunks(u32 *, M2C_UNK, M2C_UNK);    /* extern */
M2C_UNK func_80054E48(M2C_UNK);                     /* extern */
M2C_UNK func_80055948(M2C_UNK);                     /* extern */
s32 func_8006218C(M2C_UNK, M2C_UNK, M2C_UNK, M2C_UNK); /* extern */
M2C_UNK func_80062304(s32);                         /* extern */
M2C_UNK func_8FC00FF8(M2C_UNK *, u8);               /* extern */
extern s32 D_8FC02833;
extern u8 D_8FC02858;
extern s32 D_8FC02865;
extern u8 D_8FC07598;
extern s32 D_8FC075A5;
extern M2C_UNK D_8FC0C2E5;
extern M2C_UNK D_8FC0C468;
extern M2C_UNK D_8FC0C4C1;
extern M2C_UNK D_8FC0C644;
extern M2C_UNK D_8FC0C740;

void func_8FC01068(void) {
    s32 sp1C;
    s32 temp_v0;

    if (D_8FC02831 == 0) {
        _bcopy(&D_8FC02865, (s32) &D_8FC0C2E5, 0x16);
        _bcopy(&D_8FC075A5, (s32) &D_8FC0C4C1, 0x16);
        _bcopy(&D_8FC02833, (s32) &D_8FC0C740, 0x20);
        func_8FC00FF8(&D_8FC0C468, D_8FC02858);
        func_8FC00FF8(&D_8FC0C644, D_8FC07598);
        func_8FC00F88();
        Dma_CopyChunks(&D_8FC0C2D8, 0x03FEF000, 0x03FEF490);
        func_80055948(3);
        temp_v0 = func_8006218C(0x19, 0, 0, 1);
        sp1C = temp_v0;
        Deck_WriteEntries(&D_8FC0C2D8, 1, temp_v0);
        func_80062304(sp1C);
        func_80054E48(3);
        func_800226C0(2);
        return;
    }
    func_800226C0(5);
}

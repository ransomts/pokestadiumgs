#include "global.h"


#ifdef VERSION_US
extern void Input_SetRepeatController(s32);
extern s32 D_80087200;
extern s32 D_880068B8;

void func_88228A20(void) {
    Input_SetRepeatController(D_80087200);
    D_880068B8 = 0;
}

typedef struct {
    u8 unused[0x5C];
    u8 selected;
    u8 padding[3];
    void (*callback)(void);
} Cleanup_88228A48;
extern u32 D_88234890;
extern s32 D_880068B4;
extern void func_88001900(void);
extern void Util_Free(s32);
void func_88228A48(void) {
    Cleanup_88228A48 *state = (Cleanup_88228A48 *)D_88234890;

    if (state->selected != 0) {
        state->callback();
    } else {
        Input_SetRepeatController(D_80087200);
        func_88001900();
        D_880068B4 = 1;
    }
    Util_Free((s32)D_88234890);
}

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/31/fragment31_19BCA0/func_88228AB4.s")

extern u32 D_88234890;
extern void func_8821D930(s32);
void func_88228BA4(void) {
    func_8821D930((D_88234890 + 4));
}

/* mkdraft:func_88228BCC begin */
#ifndef M2C_FIELD /* mkdraft: m2c --valid-syntax helpers */
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

s32 func_8004C874(M2C_UNK, M2C_UNK);                /* extern */
M2C_UNK func_88002AA8(void *, M2C_UNK, void *, M2C_UNK, s32, s32, s32, s32, s32, s32, s32, s32, s32, M2C_UNK *); /* extern */
s32 func_88004804(void *, M2C_UNK, s16, s16, s32, s32, s32, s32, s32, M2C_UNK *, M2C_UNK *, M2C_UNK *, M2C_UNK *, s32, s32); /* extern */
extern M2C_UNK D_88006020;
extern s32 D_880068B4;
extern M2C_UNK D_8800ED50;
extern u32 D_88234890;
void func_88228A20(void);
void func_88228A48(void);
void func_88228AB4(void);
void func_88228BA4(void);

void func_88228BCC(s16 arg0, s16 arg1, s32 arg2) {
    D_88234890 = Util_Malloc(0x64);
    M2C_FIELD(D_88234890, s32 *, 0x54) = func_8004C874(0x27, 7);
    M2C_FIELD(D_88234890, s32 *, 0x58) = func_8004C874(0x27, 8);
    func_88002AA8(D_88234890 + 0x20, 0, D_88234890 + 0x54, 2, 8, 1, 6, 0, 0, 0, 0, 0, 0, &D_88006020);
    M2C_FIELD(D_88234890, s32 *, 0xC) = func_8004C874(0x27, 0);
    M2C_FIELD(D_88234890, s32 *, 8) = 0;
    M2C_FIELD(D_88234890, s32 *, 0x10) = 4;
    M2C_FIELD(D_88234890, s16 *, 0x14) = 1;
    M2C_FIELD(D_88234890, s16 *, 0x16) = 4;
    M2C_FIELD(D_88234890, void **, 0) = (void *) ((func_88004804(D_88234890 + 4, 2, arg0, arg1, 4, 1, 0xDC, 0xDC, 0xB4, &func_88228AB4, &func_88228BA4, &func_88228A20, &func_88228A48, 0, 0) * 0x4C) + &D_8800ED50);
    D_880068B4 = 0;
    M2C_FIELD(D_88234890, s32 *, 0x60) = arg2;
}
/* mkdraft:func_88228BCC end */
#endif

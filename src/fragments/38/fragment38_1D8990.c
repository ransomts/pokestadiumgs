#include "global.h"


#ifdef VERSION_US
extern void func_80049064(s16, s16, s32, s32);
extern void func_800496A4(s32, s16);
extern void func_8004989C(s32);
extern void func_800498C4();
extern void func_800499EC();
void func_889033A0(void *arg0) {
    func_800498C4();
    func_800496A4((*(s32 *)((u8 *)(arg0) + (0x10))), (*(s16 *)((u8 *)(arg0) + (0x14))));
    func_8004989C(0x1A);
    func_80049064((*(s16 *)((u8 *)(arg0) + (0))), (*(s16 *)((u8 *)(arg0) + (2))), (*(s32 *)((u8 *)(arg0) + (4))), *(*(s32 **)((u8 *)(arg0) + (8))));
    func_800499EC();
}

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/38/fragment38_1D8990/func_889033FC.s")

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

s32 func_8004C874(M2C_UNK, s32);                    /* extern */
M2C_UNK func_88002AA8(u8 *, M2C_UNK, u8 *, M2C_UNK, s32, s32, s32, s32, s32, s32, s32, s32, s32, M2C_UNK *); /* extern */
extern M2C_UNK D_88006020;

void func_889034DC(u8 *arg0) {
    s32 temp_v0;
    s32 var_s0;
    u8 *var_s1;

    var_s0 = 0;
    var_s1 = arg0;
    do {
        temp_v0 = func_8004C874(0x45, var_s0);
        var_s0 += 1;
        var_s1 += 4;
        M2C_FIELD(var_s1, s32 *, 0x34) = temp_v0;
    } while (var_s0 != 2);
    func_88002AA8(arg0 + 4, 0, arg0 + 0x38, 2, 8, 1, 6, 0xF, 0x10, 0xD, 0x10, 0, 0, &D_88006020);
    M2C_FIELD(arg0, s32 *, 0x40) = 0;
}
void func_889035A0(void *arg0, u8 *arg1, s16 arg2, s16 arg3) {
    (*(s16 *)((u8 *)(arg0) + (4))) = arg2;
    (*(s16 *)((u8 *)(arg0) + (6))) = arg3;
    (*(u8 **)((u8 *)(arg0) + (8))) = arg1;
    (*(s16 *)((u8 *)(arg0) + (0xC))) = 0;
    (*(s8 *)((u8 *)(arg0) + (0xE))) = func_88902B70(arg1);
    (*(s32 *)((u8 *)(arg0) + (0x10))) = 0;
}

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/38/fragment38_1D8990/func_889035FC.s")

extern u8 *D_889041B0;
extern s32 D_880068B8;
void func_88903B00(void) {
    s32 *temp_v0;

    temp_v0 = (*(s32 **)((u8 *)(D_889041B0) + (0x240)));
    if (temp_v0 == NULL) {
        D_880068B8 = 0;
        return;
    }
    *temp_v0 = 0;
}

s32 Input_SetRepeatController(s32);
s32 Util_Free(void *);
s32 func_88001900();
extern void *D_80087200;
extern s32 D_889041B4;
extern s8 D_889041B8;

void func_88903B2C(void)
{
  s32 (*temp_t9)();
  s32 *temp_v0;
  Input_SetRepeatController(D_80087200);
  func_88001900();
  temp_v0 = *((s32 **) (((u8 *) D_889041B0) + 0x23C));
  if (temp_v0 != NULL)
  {
    *temp_v0 = 1;
  }
  if ((*((s32 *) (((u8 *) D_889041B0) + 0x240))) == 0)
  {
    D_889041B8 = 2;
    D_889041B4 = 0;
  }
  temp_t9 = *((s32 (**)()) (((u8 *) D_889041B0) + 0x244));
  temp_t9 = temp_t9;
  Util_Free(D_889041B0);
  temp_t9();
}

extern void func_88004990(u8, s32);
extern void *D_80087200;
void func_88903BB4(void) {
    s32 *temp_v0;

    if ((*(u16 *)((u8 *)(D_80087200) + (8))) & 0xC000) {
        func_88004990(*(*(u8 **)((u8 *)(D_889041B0) + (0))), 0);
        temp_v0 = (*(s32 **)((u8 *)(D_889041B0) + (0x240)));
        if (temp_v0 != NULL) {
            *temp_v0 = 1;
            return;
        }
        D_880068B8 = 1;
    }
}

extern void func_889033A0(void *arg0);
void func_88903C28(void) {
    func_889033A0(D_889041B0 + 4);
}

#pragma GLOBAL_ASM("asm/us/nonmatchings/fragments/38/fragment38_1D8990/func_88903C50.s")
#endif

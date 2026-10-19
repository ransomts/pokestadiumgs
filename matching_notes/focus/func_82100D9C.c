extern s32 StageContext_GetFadeMode();
extern void StageContext_SetClearColor(u16);
extern s32 StageFade_StartFromTransparent(s32);
extern void func_800225C4(s32);
extern void func_80025CBC(s32);
extern void func_80064D28();
extern f32 D_821040BC;
extern f32 D_821040C0;

s32 func_82100D9C(void *arg0) {
    s32 sp24;
    f32 var_fv0;

    sp24 = *(s32 *)((u8 *)arg0 + 0x24);
    func_80064D28();
    switch (sp24) {
    case 0:
        if (StageContext_GetFadeMode() == 0) {
            sp24 = 1;
        }
        break;
    case 1:
        func_82100C50(arg0, 1);
        if (func_82100CD8(arg0) != 0) {
            s32 buttons = *(u16 *)((u8 *)D_80087200 + 8);
            if (buttons & 0x8000) {
                sp24 = 2;
                func_800226C0(0x3D);
                if ((*(s32 *)((u8 *)arg0 + 4) = *(s32 *)((u8 *)(*(void **)((u8 *)(*(void **)((u8 *)(*(void **)((u8 *)arg0 + 0x1C)) + 4)) + 8)) + 8)) != 8) {
                    func_800225C4(0x10);
                }
                StageContext_SetClearColor(0xFFFF);
                StageFade_StartFromTransparent(8);
            PERM_RANDOMIZE(
            } else if (((short) buttons) & 0x4000) {
            )
                sp24 = 2;
                func_800226C0(3);
                *(s32 *)((u8 *)arg0 + 4) = 0;
                StageContext_SetClearColor(0xFFFF);
                StageFade_StartFromTransparent(8);
            }
        }
        break;
    case 2:
        func_82100C50(arg0, 0);
        if (*(s32 *)((u8 *)arg0 + 4) != 0) {
            var_fv0 = D_821040BC;
        } else {
            var_fv0 = D_821040C0;
        }
        *(f32 *)((u8 *)arg0 + 8) = (f32)(*(f32 *)((u8 *)arg0 + 8) * var_fv0);
        if (StageContext_GetFadeMode() == 1) {
            sp24 = 3;
            if ((*(s32 *)((u8 *)arg0 + 4) != 8) && (*(s32 *)((u8 *)arg0 + 4) != 0)) {
                func_80025CBC(8);
            }
        }
        break;
    }
    if (func_82100CD8(arg0) != 0) {
        func_821006AC(*(s32 *)((u8 *)arg0 + 0x14), 1);
    } else {
        if (*(s32 *)((u8 *)arg0 + 0x38) != 0) {
            func_82100D20(arg0);
        }
        func_821006AC(*(s32 *)((u8 *)arg0 + 0x14), 0);
    }
    *(s32 *)((u8 *)arg0 + 0x24) = sp24;
    return sp24;
}

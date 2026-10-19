extern s32 func_87E0FDB4(s32, u8 *, void *, u32, u32);
extern s32 D_87E1A870[];
extern s32 D_87E1A988[];
extern s32 D_87E1AA10[];
extern u32 D_87E1EBB8;

void func_87E1162C(s32 *arg0, s32 *arg1, s32 *arg2)
{
  s32 var_s0;
  u8 *var_v0;
  s32 var_v1;
  var_s0 = 1;
  if (func_87E11534(2, *((s32 *) (((u8 *) ((u32) D_87E1EBB8)) + 8)), ((u8 *) ((u32) D_87E1EBB8)) + 0x1C, 0x20, 0x20) != 0)
  {
    *arg0 = *((s32 *) (((u8 *) ((u32) D_87E1EBB8)) + 0xC));
    *arg1 = *((s32 *) (((u8 *) ((u32) D_87E1EBB8)) + 0x10));
    *arg2 = *((s32 *) (((u8 *) ((u32) D_87E1EBB8)) + 0x14));
  }
  else
  {
    *arg0 = -1;
    *arg1 = -1;
    *arg2 = -1;
  }
  switch (*arg0)
  {
    case 6:
      var_s0 = 0;
      break;

    case 48:
      var_s0 = 0;
      break;

    default:
      for (var_v0 = ((u8 *) ((u32) D_87E1EBB8)) + 0x1C, var_v1 = 0; var_v1 != 2; var_v1 += 1)
    {
      if ((((s32) var_v0[4]) < 0xFF) && (((s32) var_v0[4]) > 0))
      {
        var_s0 = 0;
      }
      var_v0 = var_v0 + 8;
    }

      break;

  }

  func_87E0FBB4(var_s0, ((u8 *) ((u32) D_87E1EBB8)) + 0x1FC, 7, 3);
  var_v1 = 2;
  func_87E0FC90(var_s0, ((u8 *) ((u32) D_87E1EBB8)) + 0x1FC, D_87E1A988, 3, 3);
  func_87E0FBB4(var_s0, ((u8 *) ((u32) D_87E1EBB8)) + 0x1E4, 7, var_v1);

  func_87E0FDB4(((*((s32 *) (((u8 *) ((u32) D_87E1EBB8)) + 8))) == 0) && (var_s0 != 0), ((u8 *) ((u32) D_87E1EBB8)) + 0x1E4, D_87E1A870, 6, var_v1);
  func_87E0FBB4(var_s0, ((u8 *) ((u32) D_87E1EBB8)) + 0x214, 7, var_v1);
  func_87E0FDB4(((*((s32 *) (((u8 *) ((u32) D_87E1EBB8)) + 8))) == 1) && (var_s0 != 0), ((u8 *) ((u32) D_87E1EBB8)) + 0x214, D_87E1AA10, 6, var_v1);
  PERM_RANDOMIZE(
  if ((var_s0 != 0) && (*arg0 == 0x24 || *arg0 == 0x29))
  {
    *((s32 *) (((u8 *) ((u32) D_87E1EBB8)) + 0x1EC)) = 2;
  }
  )
}

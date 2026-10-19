s32 func_87E07A2C(u8 *arg0)
{
  s32 sp1C[2];
  s32 var_a1;
  u32 temp_a0;
  s32 var_v1;
  void *temp_a1;
  sp1C[1] = 0;
  temp_a0 = func_8003570C() % 145U;
  temp_a1 = *((void **) (((u8 *) arg0) + 0x170));
  var_v1 = sp1C[1];
  if ((*((u16 *) (((u8 *) temp_a1) + 0x21F4))) == 0xFFF)
  {
    *((u16 *) (((u8 *) temp_a1) + 0x21F4)) = 0U;
  }
  var_a1 = 0;
  if (((s32) temp_a0) > ((var_a1 != temp_a0) * 0))
  {
    do
    {
      loop_4:
      var_v1 += 1;

      if (var_v1 >= 0xC)
      {
        var_v1 = 0;
        if (temp_a0 && temp_a0)
        {
        }
      }
      PERM_RANDOMIZE(
      if ((*((u16 *) (((u8 *) (*((void **) (((u8 *) arg0) + 0x170)))) + 0x21F4))) & (1 << var_v1))
      )
      {
        goto loop_4;
      }
      var_a1 += 1;
    }
    while (var_a1 != temp_a0);
  }
  return var_v1;
}

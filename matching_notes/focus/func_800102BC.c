extern u8 D_8011BE90[];

void func_800102BC(s32 arg0) {
    s32 index;
    u8 *entry;
    u8 *field;

    index = 0;
    if (*((s32 *) (D_8011BE90 + 0x2C28)) > 0) {
        do {
            entry = (u8 *) (index * 0x100 + *(s32 *) (D_8011BE90 + 0x3468));
            field = entry + 0x30;
            if ((arg0 == entry[0x33]) && (field[0] != 0)) {
                field[0] = 1;
                *((f32 *) (field + 0x3C)) = *((f32 *) (D_8011BE90 + 0x2BF8));
                field[0x30] = field[0x30] | 0x10;
            }
            index++;
        } while (index < *((s32 *) (D_8011BE90 + 0x2C28)));
    }
}

s16 *func_82606E90(s16 *arg0) {
    s16 *new_var;
    s16 *current;
    s16 *result;
    s32 index;
    s32 end;

    result = 0;
    PERM_RANDOMIZE(
    end = 0x1E0;
    )
    index = 0;
    current = (new_var = arg0);
    do {
        index += 0xC;
        if ((*current) == 0) {
            result = current;
            break;
        }
        current += 6;
    } while (index != end);
    return result;
}

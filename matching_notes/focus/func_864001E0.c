s32 func_864001E0(f32 *arg0, f32 arg1, f32 *arg2, f32 *arg3, f32 *arg4, f32 *arg5) {
    f32 temp_fa0;
    f32 temp_fa0_2;
    f32 temp_fv0;
    f32 temp_fv1;
    f32 temp_fv1_2;
    s32 var_v1;

    var_v1 = 0;
    arg4[0] = arg0[0] - arg2[0];
    temp_fv1 = arg4[0];
    arg4[1] = arg0[1] - arg2[1];
    temp_fa0 = arg4[1];
    temp_fv0 = sqrtf((temp_fv1 * temp_fv1) + (temp_fa0 * temp_fa0));
    if (temp_fv0 < arg1) {
        var_v1 = 1;
        if (temp_fv0 == 0.0f) {
            arg4[0] = arg3[0];
            arg4[1] = arg3[1];
        } else {
            arg4[0] = temp_fv1 / temp_fv0;
            arg4[1] = temp_fa0 / temp_fv0;
        }
        temp_fv1_2 = arg4[0];
        temp_fa0_2 = arg4[1];
        if (((temp_fa0_2 * arg3[1]) + (temp_fv1_2 * arg3[0])) >= 0.0f) {
            *arg5 = arg1 - temp_fv0;
        } else {
            arg4[0] = temp_fv1_2;
            arg4[1] = temp_fa0_2;
            *arg5 = arg1 + temp_fv0;
        }
    }
    return var_v1;
}

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

void func_8412142C(u8 *arg0) {
    f32 *temp_a0;

    M2C_FIELD(arg0, s16 *, 0x5FE) = 0;
    M2C_FIELD(arg0, s16 *, 0x5FC) = 0;
    M2C_FIELD(arg0, s8 *, 0x623) = 0;
    M2C_FIELD(arg0, s8 *, 0x624) = 0;
    M2C_FIELD(arg0, s16 *, 0x604) = (s16) M2C_FIELD(arg0, s16 *, 0x20);
    temp_a0 = arg0 + 0x5E4;
    M2C_FIELD(temp_a0, f32 *, 0x28) = (f32) (M2C_FIELD(arg0, f32 *, 0x34) * D_84189C70);
    Vec3f_SetComponentsDuplicate(temp_a0, 0.0f, 0.0f, 0.0f);
    Vec3f_SetComponentsDuplicate(arg0 + 0x5F0, 0.0f, 0.0f, 0.0f);
    func_84120464((s32) arg0, 0x3F800000, 0x4000);
}

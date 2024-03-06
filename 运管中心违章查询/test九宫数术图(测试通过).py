import itertools

# 生成数字1到9的所有排列组合
perms = itertools.permutations(range(1, 10))

# 检查每种排列是否符合条件
for perm in perms:
    if perm[0] + perm[1] + perm[2] == 15 and perm[3] + perm[4] + perm[5] == 15 and perm[6] + perm[7] + perm[8] == 15 \
    and perm[0] + perm[3] + perm[6] == 15 and perm[1] + perm[4] + perm[7] == 15 and perm[2] + perm[5] + perm[8] == 15 \
    and perm[0] + perm[4] + perm[8] == 15 and perm[2] + perm[4] + perm[6] == 15:
        break

# 输出符合条件的九宫格
print("-------------")
for i in range(3):
    print("|", perm[i*3], "|", perm[i*3+1], "|", perm[i*3+2], "|")
    print("-------------")

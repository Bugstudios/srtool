#include <stdio.h>
#include <string.h>
#include <windows.h>

int my_atoi(const char *str) {
    int result = 0;
    int sign = 1;
    int i = 0;

    // 跳过空白字符
    while (str[i] == ' ') i++;

    // 检查符号
    if (str[i] == '-') {
        sign = -1;
        i++;
    } else if (str[i] == '+') {
        i++;
    }

    // 转换字符串到整数
    while (str[i] >= '0' && str[i] <= '9') {
        result = result * 10 + (str[i] - '0');
        i++;
    }

    return result * sign;
}


// LCG 伪随机数生成器参数
#define LCG_A 1664525
#define LCG_C 1013904223
#define LCG_M 4294967296
static unsigned int lcg_seed = 1;

// LCG 生成随机数
unsigned int lcg_rand() {
    lcg_seed = (LCG_A * lcg_seed + LCG_C) % LCG_M;
    return lcg_seed;
}

// 使用 Windows API 获取当前时间并设置种子
void lcg_srand_from_system_time() {
    SYSTEMTIME time;
    GetSystemTime(&time);
    lcg_seed = (unsigned int)(time.wSecond + time.wMilliseconds);
}

double simulateAverageSingleThread(int numSimulations, int roleCount, int weaponCount) {
    lcg_srand_from_system_time(); // 初始化随机种子

    double baseRate = 0.006;
    const int pityStartRole = 73;
    const int hardPityRole = 90;
    const int pityStartWeapon = 63;
    const int hardPityWeapon = 80;
    double rateIncrease = 0.062;

    int totalPulls = 0;

    for (int i = 0; i < numSimulations; ++i) {
        int pulls = 0;
        int guaranteedRole = 0, guaranteedWeapon = 0;
        int roleObtained = 0, weaponObtained = 0;
        int rolePullCount = 0, weaponPullCount = 0;

        // 先抽角色池
        while (roleObtained < roleCount) {
            double pullRate = baseRate;
            if (rolePullCount >= pityStartRole) {
                pullRate += (rolePullCount - pityStartRole) * rateIncrease;
            }

            int gotGold = (rolePullCount >= hardPityRole - 1) || ((double)lcg_rand() / LCG_M < pullRate);
            if (gotGold) {
                rolePullCount = 0;
                double guaranteedRate = 0.5;

                if (guaranteedRole || ((double)lcg_rand() / LCG_M < guaranteedRate)) {
                    guaranteedRole = 0;
                    roleObtained++;
                } else {
                    guaranteedRole = 1;
                }
            } else {
                rolePullCount++;
            }
            pulls++;
        }

        // 再抽武器池
        while (weaponObtained < weaponCount) {
            double pullRate = baseRate;
            if (weaponPullCount >= pityStartWeapon) {
                pullRate += (weaponPullCount - pityStartWeapon) * rateIncrease;
            }

            int gotGold = (weaponPullCount >= hardPityWeapon - 1) || ((double)lcg_rand() / LCG_M < pullRate);
            if (gotGold) {
                weaponPullCount = 0;
                double guaranteedRate = 0.75;

                if (guaranteedWeapon || ((double)lcg_rand() / LCG_M < guaranteedRate)) {
                    guaranteedWeapon = 0;
                    weaponObtained++;
                } else {
                    guaranteedWeapon = 1;
                }
            } else {
                weaponPullCount++;
            }
            pulls++;
        }

        totalPulls += pulls;
    }

    return (double)totalPulls / numSimulations;
}

double simulateWithItemsSingleThread(int numSimulations, int roleCount, int weaponCount, int items, int initialRolePulls, int initialWeaponPulls, 
                                     int majorPityRole, int majorPityWeapon) {
    lcg_srand_from_system_time(); // 初始化随机种子

    double baseRate = 0.006;
    const int pityStartRole = 73;
    const int hardPityRole = 90;
    const int pityStartWeapon = 63;
    const int hardPityWeapon = 80;
    double rateIncrease = 0.062;

    int successfulSimulations = 0;

    for (int i = 0; i < numSimulations; ++i) {
        int pulls = 0;
        int guaranteedRole = 0, guaranteedWeapon = 0;
        int currentMajorPityRole = majorPityRole;
        int currentMajorPityWeapon = majorPityWeapon;
        int roleObtained = 0, weaponObtained = 0;
        int rolePullCount = initialRolePulls, weaponPullCount = initialWeaponPulls;

        // 先抽角色池
        while (roleObtained < roleCount && pulls < items) {
            double pullRate = baseRate;
            if (rolePullCount >= pityStartRole) {
                pullRate += (rolePullCount - pityStartRole) * rateIncrease;
            }

            int gotGold = (rolePullCount >= hardPityRole - 1) || ((double)lcg_rand() / LCG_M < pullRate);
            if (gotGold) {
                rolePullCount = 0;
                double guaranteedRate = 0.5;

                if (guaranteedRole || currentMajorPityRole || ((double)lcg_rand() / LCG_M < guaranteedRate)) {
                    guaranteedRole = 0;
                    currentMajorPityRole = 0;
                    roleObtained++;
                } else {
                    guaranteedRole = 1;
                }
            } else {
                rolePullCount++;
            }
            pulls++;
        }

        // 再抽武器池
        while (weaponObtained < weaponCount && pulls < items) {
            double pullRate = baseRate;
            if (weaponPullCount >= pityStartWeapon) {
                pullRate += (weaponPullCount - pityStartWeapon) * rateIncrease;
            }

            int gotGold = (weaponPullCount >= hardPityWeapon - 1) || ((double)lcg_rand() / LCG_M < pullRate);
            if (gotGold) {
                weaponPullCount = 0;
                double guaranteedRate = 0.75;

                if (guaranteedWeapon || currentMajorPityWeapon || ((double)lcg_rand() / LCG_M < guaranteedRate)) {
                    guaranteedWeapon = 0;
                    currentMajorPityWeapon = 0;
                    weaponObtained++;
                } else {
                    guaranteedWeapon = 1;
                }
            } else {
                weaponPullCount++;
            }
            pulls++;
        }

        if (roleObtained >= roleCount && weaponObtained >= weaponCount) {
            successfulSimulations++;
        }
    }

    return (double)successfulSimulations / numSimulations * 100.0;
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <function> <parameters>...\n", argv[0]);
        return 1;
    }

    if (strcmp(argv[1], "-average") == 0) {
        if (argc < 4) {
            fprintf(stderr, "Usage: %s -average <roleCount> <weaponCount>\n", argv[0]);
            return 1;
        }
        int roleCount = my_atoi(argv[2]);
        int weaponCount = my_atoi(argv[3]);
        
        double averagePulls = simulateAverageSingleThread(50000, roleCount, weaponCount);
        double starJades = averagePulls * 160.0;

        printf("%.1f\n约合星琼数 %.1f\n", averagePulls, starJades);
    } else if (strcmp(argv[1], "-simulate") == 0) {
        if (argc < 9) {
            fprintf(stderr, "Usage: %s -simulate <roleCount> <weaponCount> <items> <initialRolePulls> <initialWeaponPulls> <majorPityRole> <majorPityWeapon>\n", argv[0]);
            return 1;
        }
        int roleCount = my_atoi(argv[2]);
        int weaponCount = my_atoi(argv[3]);
        int items = my_atoi(argv[4]);
        int initialRolePulls = my_atoi(argv[5]);
        int initialWeaponPulls = my_atoi(argv[6]);
        int majorPityRole = my_atoi(argv[7]);
        int majorPityWeapon = my_atoi(argv[8]);
        
        double successRate = simulateWithItemsSingleThread(50000, roleCount, weaponCount, items, initialRolePulls, initialWeaponPulls, majorPityRole, majorPityWeapon);
        printf("成功率 %.3f%%\n", successRate);
    } else {
        fprintf(stderr, "Invalid function specified.\n");
        return 1;
    }

    return 0;
}

#include <iostream>
#include <random>
#include <chrono>
#include <thread>
#include <vector>
#include <numeric>
#include <string>

// 初始化全局随机数引擎
std::random_device rd;

// 单线程模拟角色池和武器池抽卡的平均次数
void simulateAverageTask(int numSimulations, int roleCount, int weaponCount, std::vector<int>& results, int threadIndex) {
    std::mt19937 gen(rd());
    double baseRate = 0.006;
    const int pityStartRole = 73;
    const int hardPityRole = 90;
    const int pityStartWeapon = 63;
    const int hardPityWeapon = 80;
    double rateIncrease = 0.062;
    std::uniform_real_distribution<> dis(0.0, 1.0);

    for (int i = 0; i < numSimulations; ++i) {
        int pulls = 0;
        bool guaranteedRole = false, guaranteedWeapon = false;
        int roleObtained = 0, weaponObtained = 0;
        int rolePullCount = 0, weaponPullCount = 0;
        bool falseMajorPity = false;

        // 先抽角色池
        while (roleObtained < roleCount) {
            double pullRate = baseRate;
            if (rolePullCount >= pityStartRole) {
                pullRate += (rolePullCount - pityStartRole) * rateIncrease;
            }

            bool gotGold = (rolePullCount >= hardPityRole - 1) || (dis(gen) < pullRate);
            if (gotGold) {
                rolePullCount = 0;
                double guaranteedRate = 0.5;

                if (guaranteedRole || (dis(gen) < guaranteedRate)) {
                    guaranteedRole = false;
                    roleObtained++;
                } else {
                    guaranteedRole = true;
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

            bool gotGold = (weaponPullCount >= hardPityWeapon - 1) || (dis(gen) < pullRate);
            if (gotGold) {
                weaponPullCount = 0;
                double guaranteedRate = 0.75;

                if (guaranteedWeapon || (dis(gen) < guaranteedRate)) {
                    guaranteedWeapon = false;
                    weaponObtained++;
                } else {
                    guaranteedWeapon = true;
                }
            } else {
                weaponPullCount++;
            }
            pulls++;
        }

        results[threadIndex] += pulls;
    }
}

double calculateAveragePullsMultiThreaded(int roleCount, int weaponCount, int totalSimulations) {
    int numThreads = std::thread::hardware_concurrency();
    if (numThreads == 0) numThreads = 1;
    int simulationsPerThread = totalSimulations / numThreads;

    std::vector<int> results(numThreads, 0);
    std::vector<std::thread> threads;

    for (int i = 0; i < numThreads; ++i) {
        threads.push_back(std::thread(simulateAverageTask, simulationsPerThread, roleCount, weaponCount, std::ref(results), i));
    }

    for (auto& th : threads) {
        th.join();
    }

    int totalPulls = std::accumulate(results.begin(), results.end(), 0);
    return static_cast<double>(totalPulls) / totalSimulations;
}

void simulateWithItemsTask(int numSimulations, int roleCount, int weaponCount, int items, int initialRolePulls, int initialWeaponPulls, 
                           bool majorPityRole, bool majorPityWeapon, std::vector<int>& results, int threadIndex) {
    std::mt19937 gen(rd());
    double baseRate = 0.006;
    const int pityStartRole = 73;
    const int hardPityRole = 90;
    const int pityStartWeapon = 63;
    const int hardPityWeapon = 80;
    double rateIncrease = 0.062;
    std::uniform_real_distribution<> dis(0.0, 1.0);

    for (int i = 0; i < numSimulations; ++i) {
        int pulls = 0;
        bool guaranteedRole = false, guaranteedWeapon = false;
        bool currentMajorPityRole = majorPityRole;
        bool currentMajorPityWeapon = majorPityWeapon;
        int roleObtained = 0, weaponObtained = 0;
        int rolePullCount = initialRolePulls, weaponPullCount = initialWeaponPulls;

        // 先抽角色池
        while (roleObtained < roleCount && pulls < items) {
            double pullRate = baseRate;
            if (rolePullCount >= pityStartRole) {
                pullRate += (rolePullCount - pityStartRole) * rateIncrease;
            }

            bool gotGold = (rolePullCount >= hardPityRole - 1) || (dis(gen) < pullRate);
            if (gotGold) {
                rolePullCount = 0;
                double guaranteedRate = 0.5;

                if (guaranteedRole || currentMajorPityRole || (dis(gen) < guaranteedRate)) {
                    guaranteedRole = false;
                    currentMajorPityRole = false;
                    roleObtained++;
                } else {
                    guaranteedRole = true;
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

            bool gotGold = (weaponPullCount >= hardPityWeapon - 1) || (dis(gen) < pullRate);
            if (gotGold) {
                weaponPullCount = 0;
                double guaranteedRate = 0.75;

                if (guaranteedWeapon || currentMajorPityWeapon || (dis(gen) < guaranteedRate)) {
                    guaranteedWeapon = false;
                    currentMajorPityWeapon = false;
                    weaponObtained++;
                } else {
                    guaranteedWeapon = true;
                }
            } else {
                weaponPullCount++;
            }
            pulls++;
        }

        if (roleObtained >= roleCount && weaponObtained >= weaponCount) {
            results[threadIndex]++;
        }
    }
}

double simulateWithItemsMultiThreaded(int roleCount, int weaponCount, int items, int initialRolePulls, int initialWeaponPulls, 
                                      bool majorPityRole, bool majorPityWeapon, int totalSimulations) {
    int numThreads = std::thread::hardware_concurrency();
    if (numThreads == 0) numThreads = 1;
    int simulationsPerThread = totalSimulations / numThreads;

    std::vector<int> results(numThreads, 0);
    std::vector<std::thread> threads;

    for (int i = 0; i < numThreads; ++i) {
        threads.push_back(std::thread(simulateWithItemsTask, simulationsPerThread, roleCount, weaponCount, items, initialRolePulls, initialWeaponPulls,
                                      majorPityRole, majorPityWeapon, std::ref(results), i));
    }

    for (auto& th : threads) {
        th.join();
    }

    int successfulSimulations = std::accumulate(results.begin(), results.end(), 0);
    return static_cast<double>(successfulSimulations) / totalSimulations * 100.0;
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <function> <parameters>..." << std::endl;
        return 1;
    }

    std::string function = argv[1];
    if (function == "-average") {
        if (argc < 4) {
            std::cerr << "Usage: " << argv[0] << " -average <roleCount> <weaponCount>" << std::endl;
            return 1;
        }
        int roleCount = std::stoi(argv[2]);
        int weaponCount = std::stoi(argv[3]);
        double averagePulls = calculateAveragePullsMultiThreaded(roleCount, weaponCount, 50000);
        int starJades = static_cast<int>(std::ceil(averagePulls)) * 160;
        std::cout << averagePulls << " " << starJades << std::endl;
    } else if (function == "-simulate") {
        if (argc < 9) {
            std::cerr << "Usage: " << argv[0] << " -simulate <roleCount> <weaponCount> <items> <initialRolePulls> <initialWeaponPulls> <majorPityRole> <majorPityWeapon>" << std::endl;
            return 1;
        }
        int roleCount = std::stoi(argv[2]);
        int weaponCount = std::stoi(argv[3]);
        int items = std::stoi(argv[4]);
        int initialRolePulls = std::stoi(argv[5]);
        int initialWeaponPulls = std::stoi(argv[6]);
        bool majorPityRole = std::stoi(argv[7]);
        bool majorPityWeapon = std::stoi(argv[8]);
        double successRate = simulateWithItemsMultiThreaded(roleCount, weaponCount, items, initialRolePulls, initialWeaponPulls, majorPityRole, 
                                                            majorPityWeapon, 50000);
        std::cout << successRate << "%" << std::endl;
    } else {
        std::cerr << "Invalid function specified." << std::endl;
        return 1;
    }

    return 0;
}

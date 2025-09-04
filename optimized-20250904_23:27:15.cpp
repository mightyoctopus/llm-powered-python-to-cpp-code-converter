
#include <iostream>
#include <iomanip>
#include <chrono>

double calculate(long long iterations, long long p1, long long p2) {
    double result = 1.0;
    for (long long i = 1; i <= iterations; ++i) {
        long double j = (long double)i * p1 - p2;
        result -= (1.0L / j);
        j = (long double)i * p1 + p2;
        result += (1.0L / j);
    }
    return result;
}

int main() {
    auto start_time = std::chrono::high_resolution_clock::now();
    double final_result = calculate(100000000, 4, 1) * 4;
    auto end_time = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end_time - start_time);

    std::cout << std::fixed << std::setprecision(12) << "Result: " << final_result << std::endl;
    std::cout << "Execution Time: " << (double)duration.count() / 1000000.0 << " seconds" << std::endl;
    return 0;
}


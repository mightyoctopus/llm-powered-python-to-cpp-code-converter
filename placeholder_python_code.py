
pi_1 = """
import time

def calculate(iterations, p1, p2):
    result = 1.0 
    for i in range(1, iterations+1):
        j = i * p1 - p2
        result -= (1/j)
        j = i * p1 + p2
        result += (1/j)
    return result

### USE Or MODIFY THIS CODE BELOW IF YOU NEED CODE EXECUTION CHECK -- EXAMPLE BELOW: 
start_time = time.time()
final_result = calculate(100_000_000, 4, 1) * 4
end_time = time.time()

print(f"Result: {final_result:.12f}")
print(f"Execution Time: {(end_time - start_time):.6f} seconds")
"""

pi_2 = """
import time
def lcg(seed, a=1664525, c=1013904223, m=2**32):
    value = seed
    while True:
        value = (a * value + c) % m
        yield value

def max_subarray_sum(n, seed, min_val, max_val):
    '''Generate n pseudo-random numbers using LCG and find max subarray sum.'''
    lcg_gen = lcg(seed)
    random_numbers = [next(lcg_gen) % (max_val - min_val + 1) + min_val for _ in range(n)]

    # Kadane’s Algorithm
    max_sum = float('-inf')
    current_sum = 0
    for x in random_numbers:
        current_sum = max(x, current_sum + x)
        max_sum = max(max_sum, current_sum)

    return max_sum, random_numbers

def total_max_subarray_sum(n, initial_seed, min_val, max_val):
    total_sum = 0
    lcg_gen = lcg(initial_seed)
    for _ in range(20):
        seed = next(lcg_gen)
        max_sum, _ = max_subarray_sum(n, seed, min_val, max_val)  # unpack tuple
        total_sum += max_sum
    return total_sum

# Parameters
n = 10000
initial_seed = 42
min_val = -10
max_val = 10

# Timing
start_time = time.time()
result = total_max_subarray_sum(n, initial_seed, min_val, max_val)
end_time = time.time()

print("Total Maximum Subarray Sum (20 runs):", result)
print("Execution Time: {:.6f} seconds".format(end_time - start_time))

"""
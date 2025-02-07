import functools
import itertools
import time

# CACHING
@functools.lru_cache(maxsize=3)
def factorial(n):
    if n<=1:
        return 1
    else:
        return n*factorial(n-1)

start_time = time.time()
print(factorial(10))
end_time = time.time()
print("Elapsed Time", end_time - start_time)
start_time = time.time()
print(factorial(10))
end_time = time.time()
print("Elapsed Time", end_time - start_time)


# PARTIAL
def power(number, exponent):
    return number**exponent

square_2=power(2,2)
square_4=power(4,2)
square_4=power(5,2)
square = functools.partial(power, exponent=2)
square_4 = square(4)
square_5=square(5)
cube = functools.partial(power,exponent=3)
cube_5=cube(5)


# COMBINATIONS, PERMUTATIONS, CARTESIAN PRODUCT
# Generate all combinations of a list
combinations = itertools.combinations([1, 2, 3], 2)
print("Combinations:", list(combinations))
permutations = itertools.permutations([1, 2, 3],2)
print("Permutations:", list(permutations))

# Generate an infinite sequence of numbers
counter = itertools.count(start=1, step=2)

for _ in range(5):
    print(next(counter))
  
products = itertools.product(['A', 'B'], [1, 2])
print("Cartesian Product:", list(products))

# Define an iterable
colors = ['red', 'green', 'blue']

# Create an infinite iterator that cycles through the colors
color_cycle = itertools.cycle(colors)

# Print the first 10 elements of the color cycle
for _ in range(10):
    print(next(color_cycle))
  
# Repeat the number 5 three times
repeated_numbers = itertools.repeat(5, times=3)

# Print the repeated numbers
print(list(repeated_numbers))

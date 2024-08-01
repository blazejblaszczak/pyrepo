import random
import timeit


# INSERTION SORT
def insertion_sort(arr):
    # Traverse through all elements in the list, starting from the second element (index 1)
    for i in range(1, len(arr)):
        # Store the current element to be compared and inserted into the sorted part of the list
        current_element = arr[i]
        # Move elements of the sorted part of the list that are greater than the current element
        # to one position ahead of their current position
        j = i - 1
      
        while j >= 0 and current_element < arr[j]:
            arr[j + 1] = arr[j]
            j -= 1
          
        # Insert the current element into its correct position in the sorted part of the list
        arr[j + 1] = current_element
    return arr


# RECURSION
# At its core, recursion involves solving a problem 
# by breaking it down into smaller, more manageable instances of the same problem. 

# BASIC RECURSION EXAMPLE
def sum_of_natural_numbers(n):
    if n == 1:
        return 1 # Base case
    else:
        return n + sum_of_natural_numbers(n - 1) # Recursive case


result = sum_of_natural_numbers(5)  # Calculates 1 + 2 + 3 + 4 + 5
print(f"The sum of the first 5 natural numbers is {result}")


# RECURSIVELY CALCULATING FIBONACCI SEQUENCE
# f(n) = f(n - 1) + f(n - 2)
def fibonacci(n):
    if n <= 0:
        return 0 # Base case
    elif n == 1:
        return 1 # Base case 
    else:
        return fibonacci(n - 1) + fibonacci(n - 2) # Recursive case
    

result = fibonacci(7)  # Calculates the 7th Fibonacci number (1, 1, 2, 3, 5, 8, 13, ...)
print(f"The 7th Fibonacci number is {result}")

# RECURSIVELY CALCULATING FACTORIAL
def factorial(n):
    """
    Recursive function to calculate the factorial of a non-negative integer.
    Args:
    n (int): Non-negative integer for which factorial is calculated.
    Returns:
    int: Factorial of the input integer.
    """
    if n == 0:
        return 1  # Base case: factorial of 0 is 1
    else:
        return n * factorial(n - 1)  # Recursive case: n! = n * (n-1)!


num = 5
result = factorial(num)
print(f"The factorial of {num} is {result}")


# MERGE SORT
# Merge sort is a sorting algorithm which is
# efficient enough to be commonly used in practice.
# The idea of merge sort is to split a list up
# into smaller and smaller pieces until all that
# remains are single element lists. Since single
# element lists are necessarily sorted, this is
# our 'base case', and we can then start to
# reassemble the list in sorted order.
def merge_sort(array):
    if len(array) <= 1:
        return array
    else:
        left_split = array[:len(array)//2] # Integer division
        right_split = array[len(array)//2:]
        left = merge_sort(left_split)
        right = merge_sort(right_split)        
        return merge(left, right)


def merge(left, right):
    merged = []
    left_pointer = 0
    right_pointer = 0
    merging = True
    while merging:
        left_element = left[left_pointer]
        right_element = right[right_pointer]
        if left_element < right_element:
            merged.append(left_element)
            left_pointer += 1
        elif right_element < left_element:
            merged.append(right_element)
            right_pointer += 1
        elif right_element == left_element: # Equal items
            merged.append(right_element)
            merged.append(left_element)
            left_pointer += 1
            right_pointer += 1
        if left_pointer >= len(left): # Reached end of left list
            merged.extend(right[right_pointer:])
            merging = False
        elif right_pointer >= len(right): # Reached end of right list
            merged.extend(left[left_pointer:])
            merging = False
    return merged
  
# Generate a large random list
large_random_list = [random.randint(1, 1000) for _ in range(100)]

# Compare times
insertion_time = timeit.timeit(lambda: insertion_sort(large_random_list[:]), number=10)
merge_time = timeit.timeit(lambda: merge_sort(large_random_list[:]), number=10)

print(f"Insertion Sort took: {insertion_time:.6f} seconds")
print(f"Merge Sort took: {merge_time:.6f} seconds")

# Merge sort test cases
l = [2, 6, 9, 5, 3, 4, 5, 6, 6, 7] # [random.randint(1, 10) for _ in range(10)]
print(l)

sorted = merge_sort(l)
print(sorted)

l = [1]
sorted = merge_sort(l)
print(sorted)

l = [random.randint(1, 1000) for n in range(10000)]
sorted = merge_sort(l)
print(sorted[:50])

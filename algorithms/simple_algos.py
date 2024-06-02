# SEARCHING ALGORITHMS

# LINEAR SEARCH
# To review, linear search involves sequentially checking every element
# in a collection until the desired value is found.


def linear_search(array, target):
    for i in range(len(array)):
        if array[i] == target:
            return i
        
    return -1


test = range(1000000)
print(linear_search(test, 99999))
print(linear_search(test, -999))


# BINARY SEARCH
# An alternative to linear search is binary search. Binary search can be more efficient than
# linear search, but with a few caveats.
# First, the algorithm is more complex (this tradeoff always exists), and second,
# it requires data to be sorted. If binary search is run on unsorted data, it
# can perform just as poorly as linear search and it may produce erroneous results.


def binary_search(array, target):
    # Initialize 'pointers'
    left = 0
    right = len(array) - 1 # Account for indexing to get the right most element index
    mid = int((left + right)/2)
    while left <= right:
        if array[mid] == target: # If target is found 
            return mid
        elif target > array[mid]:
            left = mid + 1 # We already checked the mid element, so we shift the index by 1 for the next search.
        elif target < array[mid]:
            right = mid - 1
        mid = int((left + right)/2) # Recalculate mid
    return -1


test = [1, 1, 1, 2, 3, 6, 9, 19, 555]
print(binary_search(test, 1))
print(binary_search(test, 555))


# Comparing linear and binary search efficiency
# Generate a sorted list of integers for testing
sorted_list = list(range(1000000))

# Test cases
target = random.randint(0, 999999)  # Random target value
linear_time = timeit.timeit(lambda: linear_search(sorted_list, target), number=100)
binary_time = timeit.timeit(lambda: binary_search(sorted_list, target), number=100)
print(f"Linear search execution time: {linear_time:.6f} seconds")
print(f"Binary search execution time: {binary_time:.6f} seconds")


# SORTING ALGORITHMS

# BUBBLE SORT


def bubble_sort(arr):
    """
    Bubble Sort: A simple sorting algorithm that repeatedly steps through the list,
    compares adjacent elements, and swaps them if they are in the wrong order.
    Args:
    arr (list): The input list to be sorted.
    Returns:
    list: The sorted list in ascending order.
    """
    # Get the length of the input list
    n = len(arr)
    # Traverse through all elements in the list
    for i in range(n):
        # Flag to optimize the algorithm
        # If no swaps are performed in an iteration, the list is already sorted, and we can stop early
        swapped = False
        # Last i elements are already in place, so we don't need to compare them again
        for j in range(0, n - i - 1):
            # Compare adjacent elements
            if arr[j] > arr[j + 1]:
                # Swap if the element found is greater than the next element
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                # Set the swapped flag to True to indicate that a swap occurred in this iteration
                swapped = True
        # If no two elements were swapped in the inner loop, the list is sorted, and we can exit early
        if not swapped:
            break
    return arr


# Example usage:
unsorted_list = [64, 25, 12, 22, 11]
sorted_list = bubble_sort(unsorted_list)
print("Sorted array:", sorted_list)


# INSERTION SORT


def insertion_sort(arr):
    """
    Insertion Sort: A simple sorting algorithm that builds the final sorted
    array one item at a time. It takes each element from the input list and
    inserts it into its correct position in the sorted part of the array.
    Args:
    arr (list): The input list to be sorted.
    Returns:
    list: The sorted list in ascending order.
    """
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


# Example usage:
unsorted_list = [64, 1, 12, 22, 11]
sorted_list = insertion_sort(unsorted_list)
print("Sorted array:", sorted_list)


# Comparing bubble sort and insertion sort
# Generate a random unsorted list of 1000 integers
unsorted_list = [random.randint(1, 1000) for _ in range(10000)]

# Measure and compare the runtimes of Bubble Sort and Insertion Sort
bubble_sort_time = timeit.timeit(lambda: bubble_sort(unsorted_list.copy()), number=1)
insertion_sort_time = timeit.timeit(lambda: insertion_sort(unsorted_list.copy()), number=1)
print(f"Bubble Sort Execution Time: {bubble_sort_time:.6f} seconds")
print(f"Insertion Sort Execution Time: {insertion_sort_time:.6f} seconds")

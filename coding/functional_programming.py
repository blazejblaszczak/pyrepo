from functools import reduce

# FILTER
# Use range() to generate numbers from 1 to 10 and convert it to a list
numbers = list(range(1, 11))
# Use filter() with a lambda function to get only the even numbers
filtered_numbers = filter(lambda x: x % 2 == 0, numbers)
# Convert the result to a list and print it
print(list(filtered_numbers))

# MAP
# List of numbers
numbers = list(range(1,6))

# Using map() with a lambda function to double each number
squared_numbers = map(lambda x: x ** 2, numbers)
print(list(squared_numbers))  # Output: [2, 4, 6, 8, 10]

# REDUCE
letters = ["p","y","t","h","o","n"]
string = reduce(lambda x,y: x+y, letters)
print(string)

numbers = [5,4,3,2,1]
factorial = reduce(lambda x,y:x*y, numbers)
print(f"Factorial : {factorial}")

# List of prices for items in the shopping cart
prices =   [10.99, 24.50, 8.75, 15.25]

# Use reduce() to calculate the total cost including tax
total_cost_with_tax = reduce(lambda total, price: total+price+price*0.15, prices,0)
print("Total cost:", round(total_cost_with_tax, 2))

# GENERATORS

def fibonacci_generator():
    # Initialize the first two Fibonacci numbers
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b  # Update Fibonacci numbers
      
# Create a generator object for Fibonacci numbers
fib_gen = fibonacci_generator()
print(next(fib_gen))
print(next(fib_gen))
print(next(fib_gen))

# Function to generate random numbers using a generator
def generate_random_numbers_generator(n):
    for _ in range(n):
        yield random.randint(1, 100)

# LIST COMPREHENSION

# Using list comprehension
squares = [i * i for i in num_list]
odd_numbers = [i for i in num_list if i % 2 != 0]

# Using list comprehension to filter scores above the passing threshold
exam_scores = [85, 72, 90, 60, 45, 78, 82]
passing_threshold = 70
passing_scores = [score for score in exam_scores if score >= passing_threshold]

list1 = [1, 2, 3]
list2 = [5, 6, 7]
products = [x*y for x in list1 for y in list2]

# RECURSION
def factorial(n):
    if n<=1:
        return 1
    else:
        return n*factorial(n-1)
      
def fibonacci(n):
    if n <= 1:
        return n
    else:
        return fibonacci(n - 1) + fibonacci(n - 2)
      
# Generate the first 10 Fibonacci numbers
fibonacci_sequence = [fibonacci(i) for i in range(10)]
print("Fibonacci Sequence:", fibonacci_sequence)
print("Factorial of 6 is ", factorial(6))

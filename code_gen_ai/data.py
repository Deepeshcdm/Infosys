"""Data definitions for concepts, writing tasks, and buggy code snippets."""

# Random Concept Explainer Data
CONCEPTS_BY_DIFFICULTY = {
    "Beginner": [
        {"category": "Data Structures", "topic": "Arrays vs Linked Lists"},
        {"category": "Algorithms", "topic": "Linear Search"},
        {"category": "Web Dev", "topic": "What is HTTP?"},
        {"category": "CS Basics", "topic": "What is a Variable?"},
        {"category": "AI", "topic": "What is Machine Learning?"},
        {"category": "Data Structures", "topic": "Stack and Queue basics"},
        {"category": "Algorithms", "topic": "Bubble Sort"},
        {"category": "Web Dev", "topic": "HTML vs CSS vs JavaScript"},
        {"category": "CS Basics", "topic": "What is an Operating System?"},
        {"category": "AI", "topic": "Supervised vs Unsupervised Learning"},
    ],
    "Intermediate": [
        {"category": "Data Structures", "topic": "Hashmap collision resolution"},
        {"category": "Algorithms", "topic": "Two Pointers technique"},
        {"category": "Web Dev", "topic": "REST vs GraphQL"},
        {"category": "CS Basics", "topic": "Process vs Thread"},
        {"category": "AI", "topic": "Gradient Descent optimization"},
        {"category": "Data Structures", "topic": "Binary Search Trees"},
        {"category": "Algorithms", "topic": "Merge Sort vs Quick Sort"},
        {"category": "Web Dev", "topic": "CORS and how it works"},
        {"category": "CS Basics", "topic": "Virtual Memory"},
        {"category": "AI", "topic": "Overfitting and Regularization"},
    ],
    "Advanced": [
        {"category": "Data Structures", "topic": "Red-Black Trees balancing"},
        {"category": "Algorithms", "topic": "Dynamic Programming - State compression"},
        {"category": "Web Dev", "topic": "Microservices architecture patterns"},
        {"category": "CS Basics", "topic": "Deadlock prevention algorithms"},
        {"category": "AI", "topic": "Self-attention in Transformers"},
        {"category": "Data Structures", "topic": "B+ Trees for databases"},
        {"category": "Algorithms", "topic": "A* pathfinding algorithm"},
        {"category": "Web Dev", "topic": "Event-driven architecture"},
        {"category": "CS Basics", "topic": "Memory management and Garbage Collection"},
        {"category": "AI", "topic": "Reinforcement Learning - Q-Learning"},
    ]
}

# Random Writing Tasks Data
WRITING_TASKS_BY_TONE = {
    "Formal": [
        {"type": "Email", "prompt": "Write a professional apology email for missing a meeting"},
        {"type": "Email", "prompt": "Write a formal request for a deadline extension"},
        {"type": "Documentation", "prompt": "Write API documentation for a user authentication endpoint"},
        {"type": "Resume", "prompt": "Write a resume bullet point for leading a software migration project"},
        {"type": "Email", "prompt": "Write a professional introduction email to a new client"},
        {"type": "Report", "prompt": "Write an executive summary for a quarterly performance report"},
        {"type": "Proposal", "prompt": "Write a project proposal introduction for a new mobile app"},
    ],
    "Friendly": [
        {"type": "Email", "prompt": "Write a friendly follow-up email after a job interview"},
        {"type": "Social Media", "prompt": "Write an engaging LinkedIn post about starting a new job"},
        {"type": "Message", "prompt": "Write a warm welcome message for new team members"},
        {"type": "Blog", "prompt": "Write a casual blog intro about learning to code"},
        {"type": "Social Media", "prompt": "Write an Instagram caption for a team building event"},
        {"type": "Email", "prompt": "Write a friendly reminder email for an upcoming team lunch"},
        {"type": "Newsletter", "prompt": "Write a friendly company newsletter opening paragraph"},
    ],
    "Humorous": [
        {"type": "Social Media", "prompt": "Write a funny tweet about debugging code at 3 AM"},
        {"type": "Product", "prompt": "Write a humorous product description for a rubber duck debugger"},
        {"type": "Email", "prompt": "Write a playfully sarcastic out-of-office auto-reply"},
        {"type": "Story", "prompt": "Write a short funny story about a programmer's first day at work"},
        {"type": "Social Media", "prompt": "Write a witty LinkedIn post about surviving Monday meetings"},
        {"type": "Caption", "prompt": "Write a humorous error message for a 404 page"},
        {"type": "Bio", "prompt": "Write a funny developer bio for a GitHub profile"},
    ]
}

# Random Bug Generator Data
BUGGY_CODE_SNIPPETS = [
    {
        "language": "python",
        "title": "Off-by-one error in loop",
        "buggy_code": '''def sum_first_n(arr, n):
    """Sum the first n elements of arr"""
    total = 0
    for i in range(1, n + 1):  # Bug here!
        total += arr[i]
    return total

# Example: sum_first_n([1, 2, 3, 4, 5], 3) should return 6''',
        "fixed_code": '''def sum_first_n(arr, n):
    """Sum the first n elements of arr"""
    total = 0
    for i in range(n):  # Fixed: start from 0
        total += arr[i]
    return total''',
        "explanation": "The loop started at index 1 instead of 0, causing it to skip the first element and potentially access an out-of-bounds index.",
        "prevention": "Always remember Python uses 0-based indexing. Use range(n) for first n elements."
    },
    {
        "language": "python",
        "title": "Mutable default argument",
        "buggy_code": '''def add_item(item, items=[]):  # Bug here!
    items.append(item)
    return items

# Try calling:
# print(add_item("a"))  # ['a']
# print(add_item("b"))  # Expect ['b'], but get ['a', 'b']!''',
        "fixed_code": '''def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items''',
        "explanation": "Mutable default arguments (like lists) are created once at function definition, not each call. All calls share the same list!",
        "prevention": "Never use mutable objects (lists, dicts) as default arguments. Use None and create inside the function."
    },
    {
        "language": "javascript",
        "title": "Async/Await missing",
        "buggy_code": '''async function fetchUserData(userId) {
    const response = fetch(`/api/users/${userId}`);  // Bug here!
    const data = response.json();
    return data;
}

// Returns a Promise, not the actual data!''',
        "fixed_code": '''async function fetchUserData(userId) {
    const response = await fetch(`/api/users/${userId}`);
    const data = await response.json();
    return data;
}''',
        "explanation": "Missing 'await' keywords cause the function to return Promises instead of waiting for the actual values.",
        "prevention": "Always use 'await' when calling async functions or Promise-returning methods like fetch()."
    },
    {
        "language": "javascript",
        "title": "Variable hoisting issue",
        "buggy_code": '''function printNumbers() {
    for (var i = 0; i < 3; i++) {
        setTimeout(function() {
            console.log(i);  // Bug: prints 3, 3, 3
        }, 100);
    }
}
// Expected: 0, 1, 2  Actual: 3, 3, 3''',
        "fixed_code": '''function printNumbers() {
    for (let i = 0; i < 3; i++) {
        setTimeout(function() {
            console.log(i);  // Fixed: prints 0, 1, 2
        }, 100);
    }
}''',
        "explanation": "'var' is function-scoped, so all callbacks share the same 'i'. By the time they run, the loop has finished and i=3.",
        "prevention": "Use 'let' instead of 'var' for block-scoped variables, especially in loops with closures."
    },
    {
        "language": "python",
        "title": "Infinite loop",
        "buggy_code": '''def find_target(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid  # Bug here!
        else:
            right = mid  # Bug here!
    return -1''',
        "fixed_code": '''def find_target(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1  # Fixed
        else:
            right = mid - 1  # Fixed
    return -1''',
        "explanation": "Without +1/-1, the search space never shrinks when mid equals left or right, causing an infinite loop.",
        "prevention": "In binary search, always shrink the search space by excluding mid: left = mid + 1 or right = mid - 1."
    },
    {
        "language": "java",
        "title": "Null pointer exception",
        "buggy_code": '''public String getUserName(User user) {
    return user.getName().toUpperCase();  // Bug: no null check!
}

// Crashes if user is null or user.getName() returns null''',
        "fixed_code": '''public String getUserName(User user) {
    if (user == null || user.getName() == null) {
        return "Unknown";
    }
    return user.getName().toUpperCase();
}''',
        "explanation": "Calling methods on null references throws NullPointerException. Both the user object and getName() result could be null.",
        "prevention": "Always validate inputs and check for null before calling methods. Consider using Optional in Java 8+."
    },
    {
        "language": "python",
        "title": "String comparison bug",
        "buggy_code": '''def check_password(input_pwd, stored_pwd):
    if input_pwd is stored_pwd:  # Bug here!
        return True
    return False

# May fail even with matching passwords!''',
        "fixed_code": '''def check_password(input_pwd, stored_pwd):
    if input_pwd == stored_pwd:  # Fixed: use == for value comparison
        return True
    return False''',
        "explanation": "'is' checks object identity (same memory location), '==' checks value equality. Different string objects with same content fail 'is' check.",
        "prevention": "Use '==' for comparing values, 'is' only for None checks or intentional identity comparison."
    },
    {
        "language": "javascript",
        "title": "Type coercion bug",
        "buggy_code": '''function isAdult(age) {
    if (age == "18") {  // Bug: loose equality!
        return true;
    }
    return age > 18;
}

// isAdult("18") returns true (correct by accident)
// isAdult("19") returns false! (string > number comparison)''',
        "fixed_code": '''function isAdult(age) {
    const numAge = Number(age);
    if (numAge >= 18) {
        return true;
    }
    return false;
}''',
        "explanation": "Using == allows type coercion which can cause unexpected behavior. String/number comparisons with > are unpredictable.",
        "prevention": "Always use === for comparisons and explicitly convert types. Consider TypeScript for type safety."
    },
    {
        "language": "python",
        "title": "Wrong variable scope",
        "buggy_code": '''total = 0

def add_to_total(value):
    total = total + value  # Bug: UnboundLocalError!
    return total

add_to_total(5)''',
        "fixed_code": '''total = 0

def add_to_total(value):
    global total  # Fixed: declare global
    total = total + value
    return total

# Or better - avoid global state:
def add_to_total(current_total, value):
    return current_total + value''',
        "explanation": "Assignment inside a function creates a local variable. Python sees 'total = ...' and treats 'total' as local, but it's read before assignment.",
        "prevention": "Avoid modifying global variables. Pass values as parameters and return results. Use 'global' keyword only when necessary."
    },
    {
        "language": "java",
        "title": "Array index out of bounds",
        "buggy_code": '''public int getLastElement(int[] arr) {
    return arr[arr.length];  // Bug: off by one!
}

// Array of length 5 has indices 0-4, not 0-5''',
        "fixed_code": '''public int getLastElement(int[] arr) {
    if (arr == null || arr.length == 0) {
        throw new IllegalArgumentException("Array is empty");
    }
    return arr[arr.length - 1];  // Fixed: length - 1
}''',
        "explanation": "Array indices go from 0 to length-1. Accessing arr[length] is always out of bounds.",
        "prevention": "Remember: last valid index = length - 1. Add bounds checking and handle empty arrays."
    }
]

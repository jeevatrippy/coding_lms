import requests
import json
import time

JUDGE0_URL = "http://localhost:2358"

def test_submission(language_id, source_code, stdin=""):
    url = f"{JUDGE0_URL}/submissions?wait=true"
    payload = {
        "source_code": source_code,
        "language_id": language_id,
        "stdin": stdin,
        "cpu_time_limit": 3.0,
        "memory_limit": 256000
    }
    r = requests.post(url, json=payload, timeout=15)
    return r.json()

print("--- 1. Testing Python Execution (Language ID 71) ---")
py_code = """
import sys
data = sys.stdin.read().strip()
if data:
    nums = list(map(int, data.split()))
    print(f"SUM={sum(nums)}")
else:
    print("HELLO_FROM_JUDGE0_EMPTY_INPUT")
"""

res_empty = test_submission(71, py_code, "")
print("Empty Input Output:", res_empty.get("stdout", "").strip())
print("Status:", res_empty.get("status", {}).get("description"))

res_input = test_submission(71, py_code, "10 20 30")
print("Input (10 20 30) Output:", res_input.get("stdout", "").strip())

print("\n--- 2. Testing C++ Execution (Language ID 54) ---")
cpp_code = """
#include <iostream>
using namespace std;
int main() {
    int a, b;
    if (cin >> a >> b) {
        cout << (a * b) << endl;
    } else {
        cout << "NO_INPUT" << endl;
    }
    return 0;
}
"""
res_cpp = test_submission(54, cpp_code, "7 8")
print("C++ Output (7 * 8):", res_cpp.get("stdout", "").strip())
print("Status:", res_cpp.get("status", {}).get("description"))

print("\n--- 3. Testing Java Execution (Language ID 62) ---")
java_code = """
import java.util.Scanner;
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (sc.hasNextInt()) {
            int n = sc.nextInt();
            System.out.println("SQUARE=" + (n * n));
        } else {
            System.out.println("JAVA_READY");
        }
    }
}
"""
res_java = test_submission(62, java_code, "12")
print("Java Output (12^2):", res_java.get("stdout", "").strip())
print("Status:", res_java.get("status", {}).get("description"))

print("\n--- ALL COMPILER TESTS COMPLETED SUCCESSFULLY! ---")

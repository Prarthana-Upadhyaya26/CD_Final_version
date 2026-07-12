#!/bin/bash
# Test runner script for Constant Fold Strength Reduction Pass
# Runs all test cases and generates comparison report

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Constant Fold Strength Reduction Pass - Test Suite ==="
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASSED=0
TOTAL=0

run_test() {
    local test_file=$1
    local expected_contains=$2
    local description=$3

    TOTAL=$((TOTAL + 1))

    echo -n "Running $test_file: $description... "

    if [ ! -f "$BASE_DIR/testcases/$test_file" ]; then
        echo -e "${RED}FAILED${NC} - Test file not found"
        return 1
    fi

    # Run our pass
    if [ -x "$BASE_DIR/build/cf_runner" ]; then
        "$BASE_DIR/build/cf_runner" "$BASE_DIR/testcases/$test_file" "$BASE_DIR/output_$test_file" 2>/dev/null
    else
        "$BASE_DIR/run.sh" "$BASE_DIR/testcases/$test_file" "$BASE_DIR/output_$test_file" 2>/dev/null
    fi

    if [ $? -ne 0 ]; then
        echo -e "${RED}FAILED${NC} - Pass execution failed"
        return 1
    fi

    # Check if output contains expected result
    if grep -q "$expected_contains" "$BASE_DIR/output_$test_file"; then
        echo -e "${GREEN}PASSED${NC}"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}FAILED${NC} - Expected '$expected_contains' not found"
        echo "  Actual output:"
        cat "$BASE_DIR/output_$test_file" | head -10
        return 1
    fi
}

# Test cases
run_test "test1_constant_fold.ll" "ret i32 9" "Constant folding (4+5=9)"
run_test "test2_strength_reduce.ll" "shl i32" "Strength reduction (x*16 → x<<4)"
run_test "test3_mixed.ll" "shl i32" "Mixed operations with strength reduction"
run_test "test4_non_power_of_two.ll" "mul i32" "Non-power-of-2 multiplication (unchanged)"
run_test "test5_negative_power.ll" "mul i32" "Negative power multiplication (unchanged)"
run_test "test6_fold_with_expr.ll" "add i32" "Global load case is unchanged by this pass"
run_test "test7_bitwise_fold.ll" "ret i32 3" "Constant folding of bitwise AND"
run_test "test8_constleft_strength.ll" "shl i32" "Strength reduction with left-hand constant operand"
run_test "test9_constant_expr_div.ll" "ret i32 5" "Constant folding of integer division constant expression"
run_test "test10_nested_fold.ll" "shl i32" "Nested fold then strength reduction in one pass"

echo
echo "=== Results ==="
echo "Passed: $PASSED/$TOTAL tests"

if [ $PASSED -eq $TOTAL ]; then
    echo -e "${GREEN}All tests passed! ✓${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed ✗${NC}"
    exit 1
fi
#!/bin/bash
# Test script to compile C source with macros to LLVM IR and apply the optimization pass

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$BASE_DIR"

echo "=== Macro Expansion + Optimization Pass Demo ==="
echo

SOURCE_FILE="testcases/test_macro_source.c"
IR_FILE="testcases/test_macro_source.ll"
OUTPUT_FILE="output_macro_source.ll"

if [ ! -f "$SOURCE_FILE" ]; then
    echo "Error: Source file $SOURCE_FILE not found"
    exit 1
fi

echo "Step 1: Compiling C source with macro to LLVM IR..."
echo "Command: clang -emit-llvm -S -O0 $SOURCE_FILE -o $IR_FILE"
clang -emit-llvm -S -O0 "$SOURCE_FILE" -o "$IR_FILE"

if [ $? -ne 0 ]; then
    echo "Error: Failed to compile C source to LLVM IR"
    exit 1
fi

echo "✓ Generated: $IR_FILE"
echo

echo "Step 2: Generated IR (showing macro-expanded code):"
echo "---"
grep -A 5 "scaled_value" "$IR_FILE" | head -15
echo "---"
echo

echo "Step 3: Running Constant Fold + Strength Reduction Pass..."
if [ -x "build/cf_runner" ]; then
    "build/cf_runner" "$IR_FILE" "$OUTPUT_FILE" 2>/dev/null
else
    echo "Error: cf_runner not found at build/cf_runner"
    echo "Run ./build.sh first"
    exit 1
fi

if [ $? -ne 0 ]; then
    echo "Error: Pass execution failed"
    exit 1
fi

echo "✓ Generated: $OUTPUT_FILE"
echo

echo "Step 4: Optimized IR (showing strength reduction):"
echo "---"
grep -A 5 "scaled_value" "$OUTPUT_FILE" | head -15
echo "---"
echo

echo "Step 5: Verification - checking for optimizations:"
if grep -q "shl i32" "$OUTPUT_FILE"; then
    echo "✓ Found shift operation (x * 16 → x << 4)"
else
    echo "✗ Shift operation not found"
fi

if grep -q "ret i32 3" "$OUTPUT_FILE"; then
    echo "✓ Found folded constant (15 & 3 → 3)"
else
    echo "✗ Constant folding not found"
fi

echo
echo "=== Demo Complete ==="
echo "Original source: $SOURCE_FILE"
echo "Preprocessor-expanded IR: $IR_FILE"
echo "After optimization pass: $OUTPUT_FILE"

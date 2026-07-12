# Demo: Constant Fold Strength Reduction Pass

## Working Example

### Build and Run Demo
```bash
# Build the pass and direct runner
./build.sh

# Run constant folding example with the in-process runner
./build/cf_runner testcases/test1_constant_fold.ll demo_output.ll
cat demo_output.ll

# Alternatively use the wrapper script with fallback to opt
./run.sh testcases/test1_constant_fold.ll demo_output.ll
```

**Expected Output:**
```llvm
define i32 @fold_add() {
  ret i32 9  ; 4 + 5 folded at compile time
}
```

### Strength Reduction Demo
```bash
./run.sh testcases/test2_strength_reduce.ll demo_output2.ll
cat demo_output2.ll
```

**Expected Output:**
```llvm
define i32 @reduce_mul(i32 %x) {
  %1 = shl i32 %x, 4  ; x * 16 → x << 4 (much faster!)
  ret i32 %1
}
```

## Failure Case Demo

### Non-Optimizable Operation
```bash
./run.sh testcases/test4_non_power_of_two.ll demo_output3.ll
cat demo_output3.ll
```

**Expected Output (Unchanged):**
```llvm
define i32 @no_reduce(i32 %x) {
  %m = mul i32 %x, 5  ; Cannot optimize - 5 is not a power of 2
  ret i32 %m
}
```

## Performance Comparison

### Before Optimization (Original IR)
```llvm
define i32 @example(i32 %x) {
  %mul = mul i32 %x, 8      ; Expensive multiplication
  %add = add i32 %mul, 10   ; Addition with constant
  ret i32 %add
}
```

### After Our Pass
```llvm
define i32 @example(i32 %x) {
  %shl = shl i32 %x, 3      ; Cheap shift operation
  ret i32 18                ; Constant folded: 8 + 10 = 18
}
```

## Automated Testing
```bash
./test_all.sh  # Runs all 10 test cases automatically using cf_runner when available
```

## Screenshots

### 1. Build Process
![Build Output](screenshots/build_demo.png)
*Shows successful compilation with LLVM 18*

### 2. Test Execution
![Test Results](screenshots/test_demo.png)
*Shows all 10 tests passing*

### 3. Optimization Results
![Before/After](screenshots/optimization_demo.png)
*Shows IR transformation from mul to shl*

## Video Demo (Alternative)

For a video demonstration:
1. Show project structure
2. Demonstrate build process
3. Run individual test cases
4. Show automated test suite
5. Explain optimization results
6. Demonstrate failure cases (correctly unchanged code)
# Constant Fold Strength Reduction Pass

An LLVM optimization pass that performs constant folding and strength reduction on arithmetic operations.

## What It Does

This pass implements two key optimizations:
1. **Constant Folding**: Evaluates arithmetic operations with constant operands at compile time
2. **Strength Reduction**: Converts multiplication by powers of 2 into efficient shift operations

## How to Run

### Prerequisites
- Ubuntu 22.04 (or WSL) or macOS with Homebrew
- LLVM 18 toolchain
- CMake 3.13+
- Clang 18

### Setup
```bash
# Install dependencies (Ubuntu/WSL)
sudo apt update
sudo apt install -y lsb-release wget software-properties-common gnupg
wget -O - https://apt.llvm.org/llvm-snapshot.gpg.key | sudo apt-key add -
sudo add-apt-repository "deb http://apt.llvm.org/jammy/ llvm-toolchain-jammy-18 main"
sudo apt update
sudo apt install -y llvm-18 llvm-18-dev clang-18 lld-18 cmake build-essential
```

### Build and Run
```bash
# Make scripts executable
chmod +x build.sh run.sh test_all.sh

# Build the pass and the in-process runner
./build.sh

# Run on a test case with the recommended in-process runner
./build/cf_runner testcases/test1_constant_fold.ll output.ll

# Alternatively, use the wrapper script to fall back to the opt plugin
./run.sh testcases/test1_constant_fold.ll output.ll

# View results
cat output.ll
```

### Test Cases
The `testcases/` directory contains 10 test files demonstrating different scenarios:
- `test1_constant_fold.ll`: Basic constant folding (4 + 5 = 9)
- `test2_strength_reduce.ll`: Strength reduction (x * 16 → x << 4)
- `test3_mixed.ll`: Mixed operations
- `test4_non_power_of_two.ll`: Non-optimizable multiplication
- `test5_negative_power.ll`: Negative power (unchanged)
- `test6_fold_with_expr.ll`: Complex expressions

## Project Structure
```
.
├── src/
│   ├── ConstantFoldStrength.cpp    # Pass implementation
│   └── CMakeLists.txt              # Build configuration
├── testcases/                      # LLVM IR test files
├── build.sh                        # Build script
├── run.sh                          # Run script
├── README.md                       # This file
├── DESIGN.md                       # Design document
├── IMPLEMENTATION.md              # Implementation details
└── EVALUATION.md                  # Performance evaluation
```
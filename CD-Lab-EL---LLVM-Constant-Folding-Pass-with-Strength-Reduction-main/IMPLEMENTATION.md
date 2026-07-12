# Implementation Details: Constant Fold Strength Reduction Pass

## LLVM Architecture Integration

### Pass Manager Integration
The pass inherits from `PassInfoMixin<ConstantFoldStrengthPass>` to integrate with LLVM's new pass manager (NPM). This provides:
- Automatic registration with the pass pipeline
- Standard analysis preservation tracking
- Compatibility with modern LLVM optimization pipelines

### Plugin Architecture
Implemented as a loadable pass plugin using the `PassPluginLibraryInfo` interface:
- Allows dynamic loading via `opt --load-pass-plugin`
- Follows LLVM's plugin API version requirements
- Enables easy integration with existing toolchains

### In-Process Runner
The project also includes an in-process runner implementation in `Runner.cpp`:
- Builds as `cf_runner` alongside the pass plugin
- Executes the pass directly through LLVM C++ APIs
- Avoids requiring external `opt` for local verification and macOS/Homebrew workflows

## Core Implementation

### Header Usage
```cpp
#include "llvm/ADT/ArrayRef.h"           // For pipeline element arrays
#include "llvm/ADT/SmallVector.h"        // Efficient worklist storage
#include "llvm/ADT/StringRef.h"          // String handling
#include "llvm/IR/Constants.h"           // ConstantInt operations
#include "llvm/IR/Function.h"            // Function/BB iteration
#include "llvm/IR/IRBuilder.h"           // Instruction creation
#include "llvm/IR/Instructions.h"        // BinaryOperator access
#include "llvm/IR/PassManager.h"         // NPM base classes
#include "llvm/Passes/PassBuilder.h"     // Pipeline registration
#include "llvm/Passes/PassPlugin.h"      // Plugin infrastructure
```

### Key Functions

#### `isPositivePowerOfTwo(const APInt &V)`
```cpp
static bool isPositivePowerOfTwo(const APInt &V) {
  return V.isPowerOf2() && V.isNonNegative();
}
```
- Uses LLVM's `APInt` arbitrary-precision integer class
- Checks both power-of-2 property and non-negativity
- Essential for correct strength reduction

#### Main `run()` Method
- **Worklist Creation**: Collects all `BinaryOperator` instances
- **Constant Folding**: Direct evaluation of constant expressions
- **Strength Reduction**: Algebraic transformation to shifts
- **IR Updates**: Uses `IRBuilder` for correct instruction placement

### Build System

#### CMake Configuration
```cmake
find_package(LLVM REQUIRED CONFIG)        # Locate LLVM installation
list(APPEND CMAKE_MODULE_PATH ${LLVM_CMAKE_DIR})
include(AddLLVM)                          # LLVM-specific build helpers

add_definitions(${LLVM_DEFINITIONS})      # Compiler flags
include_directories(SYSTEM ${LLVM_INCLUDE_DIRS})  # Header paths

add_llvm_pass_plugin(ConstantFoldStrength # Plugin target
    ConstantFoldStrength.cpp
)
```

#### Compiler Requirements
- **Clang 18**: Matches LLVM version for compatibility
- **C++ Standard**: Uses C++ features supported by LLVM 18
- **Optimization**: Release build with `-O3` for performance

## Technical Details

### Memory Management
- Uses `SmallVector` for efficient small collections
- Leverages LLVM's arena-based memory allocation
- No manual memory management required

### Instruction Replacement
```cpp
BO->replaceAllUsesWith(Folded);
BO->eraseFromParent();
```
- Atomic replacement ensures IR consistency
- `eraseFromParent()` safely removes dead instructions
- Preserves use-def chains correctly

### Analysis Preservation
Returns `PreservedAnalyses::none()` when modifications occur, indicating that all analyses may be invalidated. Returns `PreservedAnalyses::all()` when no changes are made.

## Testing Infrastructure

### Test Case Format
Uses LLVM IR (.ll files) for input/output verification:
- Human-readable intermediate representation
- Easy to verify transformations
- Compatible with both direct runner and `opt`

### Automation Scripts
- `build.sh`: Handles CMake configuration and compilation
- `run.sh`: Provides consistent testing interface and falls back to `opt` if needed
- `cf_runner`: In-process execution target used by `test_all.sh` when available
- Cross-platform compatibility via macOS/Homebrew and WSL

## Performance Characteristics

### Time Complexity
- O(n) where n is the number of instructions
- Single pass over function instructions
- Efficient constant-time checks per operation

### Space Complexity
- O(n) for worklist storage in worst case
- Minimal additional memory usage
- Reuses LLVM's existing data structures
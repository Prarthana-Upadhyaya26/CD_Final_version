# Design Document: Constant Fold Strength Reduction Pass

## Approach

### Core Strategy
The pass implements a function-level optimization that combines two complementary techniques:
1. **Constant Folding**: Compile-time evaluation of arithmetic with known constants
2. **Strength Reduction**: Algebraic transformation of expensive operations to cheaper equivalents

### Algorithm Overview
1. **Collection Phase**: Gather all binary operations in the function
2. **Analysis Phase**: Check each operation for optimization opportunities
3. **Transformation Phase**: Apply folding/reduction and update the IR
4. **Cleanup Phase**: Remove dead instructions and return analysis results

### Key Design Decisions

#### Worklist-Based Processing
- Uses a forward iteration over basic blocks to collect binary operations
- Processes operations in a worklist to handle dependencies safely
- Avoids modifying instructions while iterating over them

#### Conservative Constant Folding
- Only folds operations where both operands are compile-time constants
- Does not perform interprocedural constant propagation
- Avoids complex expression evaluation to maintain simplicity

#### Positive Power-of-2 Only
- Strength reduction limited to positive powers of 2
- Ensures correctness for unsigned/signed arithmetic
- Matches common optimization patterns in real code

#### Runner and Validation
- Implementation is separated into a reusable pass header and plugin registration
- A separate `cf_runner` target executes the pass directly through LLVM APIs
- This enables local validation without requiring external `opt` invocation

## Alternatives Considered

### Broader Constant Folding
**Alternative**: Implement full constant propagation with dataflow analysis
- **Pros**: Could handle more cases (e.g., test6 with global loads)
- **Cons**: Significantly more complex, increases compilation time
- **Decision**: Keep simple - focus on local, obvious optimizations

### All Strength Reductions
**Alternative**: Reduce division/modulo operations, not just multiplication
- **Pros**: More comprehensive optimization coverage
- **Cons**: Division strength reduction is more complex and error-prone
- **Decision**: Start with multiplication only - most common and safe case

### Module-Level Pass
**Alternative**: Implement as module pass instead of function pass
- **Pros**: Could optimize across function boundaries
- **Cons**: More complex analysis, potential for larger compile-time impact
- **Decision**: Function-level is appropriate for this optimization scope

### Integration with LLVM Pipeline
**Alternative**: Use existing LLVM passes (InstCombine, etc.)
- **Pros**: Leverage battle-tested implementations
- **Cons**: Learning exercise requires custom implementation
- **Decision**: Custom implementation for educational purposes

## Trade-offs

### Simplicity vs. Completeness
- **Chosen**: Simple, focused optimizations that are obviously correct
- **Alternative**: Complex analysis for marginal additional optimizations

### Compile-time vs. Runtime Performance
- **Chosen**: Fast compilation with good runtime improvements
- **Alternative**: Slower compilation for potentially better runtime code

### Correctness vs. Aggressiveness
- **Chosen**: Conservative approach that never breaks programs
- **Alternative**: Aggressive optimizations that might have edge cases
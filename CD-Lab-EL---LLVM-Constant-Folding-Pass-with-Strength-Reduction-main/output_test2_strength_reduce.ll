; ModuleID = '/Users/shriram/Downloads/CD-Lab-EL---LLVM-Constant-Folding-Pass-with-Strength-Reduction-main/testcases/test2_strength_reduce.ll'
source_filename = "/Users/shriram/Downloads/CD-Lab-EL---LLVM-Constant-Folding-Pass-with-Strength-Reduction-main/testcases/test2_strength_reduce.ll"

define i32 @reduce_mul(i32 %x) {
  %1 = shl i32 %x, 4
  ret i32 %1
}

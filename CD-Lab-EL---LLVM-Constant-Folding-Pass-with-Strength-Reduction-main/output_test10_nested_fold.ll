; ModuleID = '/Users/shriram/Downloads/CD-Lab-EL---LLVM-Constant-Folding-Pass-with-Strength-Reduction-main/testcases/test10_nested_fold.ll'
source_filename = "/Users/shriram/Downloads/CD-Lab-EL---LLVM-Constant-Folding-Pass-with-Strength-Reduction-main/testcases/test10_nested_fold.ll"

define i32 @nested(i32 %x) {
  %1 = shl i32 %x, 3
  %res = add i32 2, %1
  ret i32 %res
}

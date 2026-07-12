; ModuleID = '/Users/shriram/Downloads/CD-Lab-EL---LLVM-Constant-Folding-Pass-with-Strength-Reduction-main/testcases/test3_mixed.ll'
source_filename = "/Users/shriram/Downloads/CD-Lab-EL---LLVM-Constant-Folding-Pass-with-Strength-Reduction-main/testcases/test3_mixed.ll"

define i32 @mixed(i32 %a) {
  %1 = shl i32 %a, 3
  %res = add i32 5, %1
  ret i32 %res
}

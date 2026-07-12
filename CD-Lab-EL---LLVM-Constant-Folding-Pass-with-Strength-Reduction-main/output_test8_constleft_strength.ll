; ModuleID = '/Users/shriram/Downloads/CD-Lab-EL---LLVM-Constant-Folding-Pass-with-Strength-Reduction-main/testcases/test8_constleft_strength.ll'
source_filename = "/Users/shriram/Downloads/CD-Lab-EL---LLVM-Constant-Folding-Pass-with-Strength-Reduction-main/testcases/test8_constleft_strength.ll"

define i32 @reduce_left_const(i32 %x) {
  %1 = shl i32 %x, 5
  ret i32 %1
}

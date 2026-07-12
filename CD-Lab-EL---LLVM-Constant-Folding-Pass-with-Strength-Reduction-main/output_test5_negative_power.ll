; ModuleID = '/Users/shriram/Downloads/CD-Lab-EL---LLVM-Constant-Folding-Pass-with-Strength-Reduction-main/testcases/test5_negative_power.ll'
source_filename = "/Users/shriram/Downloads/CD-Lab-EL---LLVM-Constant-Folding-Pass-with-Strength-Reduction-main/testcases/test5_negative_power.ll"

define i32 @mul_neg4(i32 %x) {
  %m = mul i32 %x, -4
  ret i32 %m
}

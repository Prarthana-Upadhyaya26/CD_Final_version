; ModuleID = '/Users/shriram/Downloads/CD-Lab-EL---LLVM-Constant-Folding-Pass-with-Strength-Reduction-main/testcases/test4_non_power_of_two.ll'
source_filename = "/Users/shriram/Downloads/CD-Lab-EL---LLVM-Constant-Folding-Pass-with-Strength-Reduction-main/testcases/test4_non_power_of_two.ll"

define i32 @no_reduce(i32 %x) {
  %m = mul i32 %x, 5
  ret i32 %m
}

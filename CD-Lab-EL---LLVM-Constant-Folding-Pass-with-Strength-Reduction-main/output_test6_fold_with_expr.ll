; ModuleID = '/Users/shriram/Downloads/CD-Lab-EL---LLVM-Constant-Folding-Pass-with-Strength-Reduction-main/testcases/test6_fold_with_expr.ll'
source_filename = "/Users/shriram/Downloads/CD-Lab-EL---LLVM-Constant-Folding-Pass-with-Strength-Reduction-main/testcases/test6_fold_with_expr.ll"

@glob = constant i32 10

define i32 @fold_expr() {
  %load = load i32, ptr @glob, align 4
  %add = add i32 %load, 20
  ret i32 %add
}

@glob = constant i32 10

define i32 @fold_expr() {
  %load = load i32, ptr @glob
  %add = add i32 %load, 20
  ret i32 %add
}

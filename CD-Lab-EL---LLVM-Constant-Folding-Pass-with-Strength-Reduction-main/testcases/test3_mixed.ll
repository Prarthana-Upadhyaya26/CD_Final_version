define i32 @mixed(i32 %a) {
  %cst = add i32 2, 3
  %mul = mul i32 %a, 8
  %res = add i32 %cst, %mul
  ret i32 %res
}

define i32 @nested(i32 %x) {
  %cst = add i32 1, 1
  %mul = mul i32 %x, 8
  %res = add i32 %cst, %mul
  ret i32 %res
}

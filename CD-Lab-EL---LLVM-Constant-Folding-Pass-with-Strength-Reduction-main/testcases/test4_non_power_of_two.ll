define i32 @no_reduce(i32 %x) {
  %m = mul i32 %x, 5
  ret i32 %m
}

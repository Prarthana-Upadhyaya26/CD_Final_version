// C source file with a preprocessor macro that gets expanded and optimized
#define SCALE 3+5

int scaled_value(int x) {
  return x * SCALE;
}

int bitwise_constant(void) {
  return 15 & 3;
}

int combined_operation(int a, int b) {
  int step1 = a * SCALE;
  int step2 = step1 + b;
  return step2;
}

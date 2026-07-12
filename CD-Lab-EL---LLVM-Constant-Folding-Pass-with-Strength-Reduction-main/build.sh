#!/bin/bash
rm -rf build
mkdir build && cd build
chmod 755 .

if [ -z "$CXX" ]; then
  if [ -x "/opt/homebrew/opt/llvm@18/bin/clang++" ]; then
    export CXX="/opt/homebrew/opt/llvm@18/bin/clang++"
  elif command -v clang++-18 >/dev/null 2>&1; then
    export CXX="$(command -v clang++-18)"
  elif command -v clang++ >/dev/null 2>&1; then
    export CXX="$(command -v clang++)"
  fi
fi

if [ -z "$CXX" ]; then
  echo "C++ compiler not found. Install LLVM or set CXX to clang++." >&2
  exit 1
fi

CMAKE_ARGS="-DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_COMPILER=$CXX"
if [ -d "/opt/homebrew/opt/llvm@18/lib/cmake/llvm" ]; then
  CMAKE_ARGS="$CMAKE_ARGS -DLLVM_DIR=/opt/homebrew/opt/llvm@18/lib/cmake/llvm"
fi

cmake $CMAKE_ARGS ../src

if command -v sysctl >/dev/null 2>&1; then
  JOBS=$(sysctl -n hw.ncpu)
else
  JOBS=$(nproc 2>/dev/null || getconf _NPROCESSORS_ONLN 2>/dev/null || echo 1)
fi
make -j"$JOBS"
if [ -f "ConstantFoldStrength.dylib" ] && [ ! -f "ConstantFoldStrength.so" ]; then
  ln -sf "ConstantFoldStrength.dylib" "ConstantFoldStrength.so"
fi
cd ..
echo "Plugin built: build/ConstantFoldStrength.so"
echo "Runner built: build/cf_runner"
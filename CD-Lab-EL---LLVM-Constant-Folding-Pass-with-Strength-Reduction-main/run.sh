#!/bin/bash
# Run the pass on a test file using cf_runner when available, otherwise use opt/opt-18.
if [ -x "./build/cf_runner" ]; then
  ./build/cf_runner "$1" "$2"
  exit $?
fi

if [ -n "$OPT" ]; then
  OPT_BIN="$OPT"
elif [ -x "/opt/homebrew/opt/llvm@18/bin/opt" ]; then
  OPT_BIN="/opt/homebrew/opt/llvm@18/bin/opt"
elif command -v opt-18 >/dev/null 2>&1; then
  OPT_BIN="$(command -v opt-18)"
elif command -v opt >/dev/null 2>&1; then
  OPT_BIN="$(command -v opt)"
else
  echo "opt not found. Install LLVM or set OPT to the opt binary, or build with ./build.sh." >&2
  exit 1
fi

PLUGIN="./build/ConstantFoldStrength.so"
if [ ! -f "$PLUGIN" ] && [ -f "./build/ConstantFoldStrength.dylib" ]; then
  PLUGIN="./build/ConstantFoldStrength.dylib"
fi

"$OPT_BIN" -load-pass-plugin "$PLUGIN" \
    -passes="constfold-strength" -S "$1" -o "$2"
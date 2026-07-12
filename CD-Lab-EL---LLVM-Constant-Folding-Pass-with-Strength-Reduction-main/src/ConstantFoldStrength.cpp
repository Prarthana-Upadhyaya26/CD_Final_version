#include "ConstantFoldStrength.h"
#include "llvm/ADT/ArrayRef.h"
#include "llvm/ADT/StringRef.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"

using namespace llvm;

// Registration for the new pass manager.
llvm::PassPluginLibraryInfo getConstantFoldStrengthPluginInfo() {
  return {LLVM_PLUGIN_API_VERSION, "ConstantFoldStrength", LLVM_VERSION_STRING,
          [](PassBuilder &PB) {
            PB.registerPipelineParsingCallback(
                [](StringRef Name, FunctionPassManager &FPM,
                   ArrayRef<PassBuilder::PipelineElement>) {
                  if (Name == "constfold-strength") {
                    FPM.addPass(ConstantFoldStrengthPass());
                    return true;
                  }
                  return false;
                });
          }};
}

// This is the core interface for pass plugins.
extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo
llvmGetPassPluginInfo() {
  return getConstantFoldStrengthPluginInfo();
}

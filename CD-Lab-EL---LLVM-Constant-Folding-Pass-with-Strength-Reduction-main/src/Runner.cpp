#include "ConstantFoldStrength.h"
#include "llvm/Bitcode/BitcodeReader.h"
#include "llvm/Bitcode/BitcodeWriter.h"
#include "llvm/IR/AssemblyAnnotationWriter.h"
#include "llvm/IR/LLVMContext.h"
#include "llvm/IR/LegacyPassManager.h"
#include "llvm/IR/Module.h"
#include "llvm/IRReader/IRReader.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Support/CommandLine.h"
#include "llvm/Support/FileSystem.h"
#include "llvm/Support/SourceMgr.h"
#include "llvm/Support/ToolOutputFile.h"
#include "llvm/Support/raw_ostream.h"

using namespace llvm;

static cl::opt<std::string> InputFilename(cl::Positional,
                                          cl::desc("<input LLVM IR file>"),
                                          cl::Required);
static cl::opt<std::string> OutputFilename(cl::Positional,
                                           cl::desc("<output LLVM IR file>"),
                                           cl::Required);

int main(int argc, char **argv) {
  cl::ParseCommandLineOptions(argc, argv, "cf_runner: run constant folding + strength reduction\n");

  LLVMContext Context;
  SMDiagnostic Err;
  std::unique_ptr<Module> M = parseIRFile(InputFilename, Err, Context);
  if (!M) {
    Err.print(argv[0], errs());
    return 1;
  }

  PassBuilder PB;
  FunctionAnalysisManager FAM;
  PB.registerFunctionAnalyses(FAM);

  ConstantFoldStrengthPass Pass;
  for (Function &F : *M) {
    if (!F.isDeclaration())
      Pass.run(F, FAM);
  }

  std::error_code EC;
  raw_fd_ostream Out(OutputFilename, EC, sys::fs::OF_None);
  if (EC) {
    errs() << "Unable to open output file: " << EC.message() << "\n";
    return 1;
  }

  M->print(Out, nullptr);
  return 0;
}

#ifndef CONSTANT_FOLD_STRENGTH_H
#define CONSTANT_FOLD_STRENGTH_H

#include "llvm/ADT/ArrayRef.h"
#include "llvm/ADT/SmallVector.h"
#include "llvm/ADT/StringRef.h"
#include "llvm/IR/Constants.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/IR/Instructions.h"
#include "llvm/IR/PassManager.h"
#include "llvm/Support/raw_ostream.h"

struct ConstantFoldStrengthPass
    : public llvm::PassInfoMixin<ConstantFoldStrengthPass> {
  static bool isPositivePowerOfTwo(const llvm::APInt &V) {
    return V.isPowerOf2() && V.isNonNegative();
  }

  llvm::PreservedAnalyses
  run(llvm::Function &F, llvm::FunctionAnalysisManager &) {
    bool Changed = false;

    llvm::IRBuilder<> Builder(F.getContext());
    llvm::SmallVector<llvm::BinaryOperator *, 16> Worklist;
    for (llvm::BasicBlock &BB : F)
      for (llvm::Instruction &I : BB)
        if (auto *BinOp = llvm::dyn_cast<llvm::BinaryOperator>(&I))
          Worklist.push_back(BinOp);

    for (llvm::BinaryOperator *BO : Worklist) {
      if (!BO->getParent() || BO->use_empty())
        continue;

      llvm::Value *Op0 = BO->getOperand(0);
      llvm::Value *Op1 = BO->getOperand(1);

      auto *C0 = llvm::dyn_cast<llvm::ConstantInt>(Op0);
      auto *C1 = llvm::dyn_cast<llvm::ConstantInt>(Op1);
      if (C0 && C1) {
        llvm::Constant *Folded =
            llvm::ConstantExpr::get(BO->getOpcode(), C0, C1);
        BO->replaceAllUsesWith(Folded);
        BO->eraseFromParent();
        Changed = true;
        continue;
      }

      if (BO->getOpcode() == llvm::Instruction::Mul) {
        if (auto *CI = llvm::dyn_cast<llvm::ConstantInt>(Op1)) {
          const llvm::APInt &Val = CI->getValue();
          if (isPositivePowerOfTwo(Val)) {
            unsigned ShiftAmt = Val.exactLogBase2();
            Builder.SetInsertPoint(BO);
            llvm::Value *Shift = Builder.CreateShl(
                Op0, llvm::ConstantInt::get(CI->getType(), ShiftAmt));
            BO->replaceAllUsesWith(Shift);
            BO->eraseFromParent();
            Changed = true;
            continue;
          }
        }
        if (auto *CI = llvm::dyn_cast<llvm::ConstantInt>(Op0)) {
          const llvm::APInt &Val = CI->getValue();
          if (isPositivePowerOfTwo(Val)) {
            unsigned ShiftAmt = Val.exactLogBase2();
            Builder.SetInsertPoint(BO);
            llvm::Value *Shift = Builder.CreateShl(
                Op1, llvm::ConstantInt::get(CI->getType(), ShiftAmt));
            BO->replaceAllUsesWith(Shift);
            BO->eraseFromParent();
            Changed = true;
            continue;
          }
        }
      }
    }

    return Changed ? llvm::PreservedAnalyses::none()
                   : llvm::PreservedAnalyses::all();
  }
};

#endif // CONSTANT_FOLD_STRENGTH_H

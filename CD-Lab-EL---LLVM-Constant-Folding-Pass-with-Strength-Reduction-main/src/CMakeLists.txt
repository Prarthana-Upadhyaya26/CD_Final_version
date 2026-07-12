cmake_minimum_required(VERSION 3.13)
project(ConstantFoldStrength)

find_package(LLVM REQUIRED CONFIG)
list(APPEND CMAKE_MODULE_PATH ${LLVM_CMAKE_DIR})
include(AddLLVM)

add_definitions(${LLVM_DEFINITIONS})
include_directories(SYSTEM ${LLVM_INCLUDE_DIRS})

add_llvm_pass_plugin(ConstantFoldStrength
    ConstantFoldStrength.cpp
    PARTIAL_SOURCES_INTENDED
)

llvm_map_components_to_libnames(LLVM_LIBS
    core
    support
    irreader
    asmparser
    analysis
    transformutils
    passes
)

add_executable(cf_runner Runner.cpp)
llvm_update_compile_flags(cf_runner)
target_link_libraries(cf_runner PRIVATE ${LLVM_LIBS})

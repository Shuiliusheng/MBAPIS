1. riscv-pk
    - Modify the original size of the mmap record region in mmap.c to enable riscv-pk to support multiple executions of the mmap function calls.
    - Modify the code in mmap.c to set a larger memory size, to support more memory.
2. rocket-chip
    - Modify the code in subsystem/Configs.scala to initialize the memory size, in order to support sufficiently large memory when using the rocket/boom simulator and riscv-pk.
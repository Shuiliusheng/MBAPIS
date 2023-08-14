#### create checkpoint with gem5
1. Introduction
    - Before running Gem5, the user sets the starting position (in terms of instruction count) and length information for the program segment to create a checkpoint file. Gem5 then collects information about the execution of instructions within that segment during the execution process. Finally, Gem5 generates the checkpoint file based on the collected information.
    - Before running Gem5, the memory space for the test program is configured as follows: (A portion of the space is reserved for checkpoint loader usage)
      - The brk point is set to the default BrkPoint_For_Ckpt (0x1400000), and the checkpoint loader will be linked at the position 0x1000000 (i.e., the available space from 0x1000000 to 0x1400000).
      - The starting position for mmap is set.
      - The initial position for the stack is set.
    - Execution example: ckptsettings is an additional parameter added.
      - The example directory contains an example running script for 403.gcc.
      ```shell
        ./build/RISCV/gem5.fast ./configs/example/se.py --cpu-type=NonCachingSimpleCPU --mem-type=SimpleMemory --mem-size=8GB --ckptsetting=settingsfile -c bench/test.riscv --options=""
      ```

2. Additional parameter: --ckptsettings=settingsfile
  - The parameters used to specify the generation of a checkpoint include:
      - stacktop: Specify the runtime stack base address
      - mmapend: Specify the mmap base address
      - brkpoint: Specify the starting position of the runtime brk point, with the default value of BrkPoint_For_Ckpt (0x1400000).
      - ckptprefix: Specify the directory and checkpoint file name prefix for the output checkpoint file. The directory needs to be created in advance.
      - strictLength: This option causes Gem5 to not search for the interval exit instruction but instead terminates the information gathering for checkpoint generation and creates the checkpoint file after reaching the specified instruction count.
      - ckptctrl: (startplace length warmupnum times), specify the information of each program interval that will be created checkpoints
          - startplace: the begining instruction count for starting recording information and create checkpoints.
          - length: the length of each program interval
          - warmupnum: the number of instructions used to warmup for each program interval
          - times: the number of consecutive identical program intervals.

  - An example of settingsfile
    - A setting file is configured for the target execution environment as riscv-pk: riscv-pk supports a maximum of 2GB memory and a maximum address space of 0x80000000 (riscv-pk needs to be modified separately to support this space).
      ```c
          //Starting from 60,000 instructions, create four consecutive intervals of 20,000 instructions each to generate checkpoint files. Each interval includes an additional 1,000 instructions for warm-up.
          //Each interval does not search for an interval exit instruction.
          stacktop: 0x74000000
          mmapend: 0x30000000
          brkpoint: 0x1400000
          ckptprefix: ./dir/test
          strictLength: 
          ckptctrl: 60000 20000 1000 4
      ```
    - A setting file configured for the target execution environment as Linux: the maximum address space is set to 0x3fc0000000.
      ```c
          stacktop: 0x3e00000000
          mmapend: 0x0e00000000
          ckptprefix: ./dir/test
          ckptctrl: 60000 20000 1000 4
      ```

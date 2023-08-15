### Read the ckpt file, restore the initial running environment of the target program interval, and take over the syscalls in the interval
1. ckptinfo.h: Used to define some struct, assembly code, function, extern variables

2. readckpt.cpp: contains the main function，responsible for initially allocating certain fixed memory regions
    - main(int argc, char **argv)
      - argv[1]: the file name of the checkpoint; argv[2]: the corresponding executable file
  
3. elf_load.cpp: loads the code segment used by the target program interval into memory
    - uint64_t loadelf(char * progname, char *ckptinfo)
      - Parse the ELF file to obtain the information of the code segment
      - Read the checkpoint file, get the code area information used, and load this information into memory from the elf file

4. user_jmp.cpp: finds a sequence of jump instructions that satisfies the jump requirement for each syscall 

5. ckpt_load.cpp: reads the information in the checkpoint and restore the environment required for the execution of the target program interval
    - void read_ckptsyscall(FILE *fp): reads all syscall information from the ckpt file and put it in memory
    - void alloc_memrange(FILE *p): 
      - reads all memory region information from the ckpt file
      - allocates all memory regions using the mmap function
    - void setFistLoad(FILE *p)
      - reads all first load information from the ckpt file and restore their data to memory
    - void read_ckptinfo(char ckptinfo[])
      - Main tasks: read ckpt file, restore all execution environments, complete jump conversion for syscalls, start interval relaying
      - reads the ckpt file, get the starting instruction number of the program interval, the interval length, the number of warmup instructions, the pc of the interval exit instruction, the pc of the first instruction of this interval
      - gets all integer and floating point register data from the ckpt file
      - calls the alloc_memrange function to allocate all used memory regions
      - calls the setFirstload function to restore all first load data
      - calls the read_ckptsyscall function to read all syscall information
      - calls the getRangeInfo and produceJmp function to complete the conversion of all jump requirements for all syscall
      - determines whether the interval contains a syscall. If not, we need to replace the exit instruction with the jal instruction at this time; otherwise, the takeOverSyscall function will replace it after the last syscall is processed.
      - saves the current logical register data to memory, and restore all register states of the start point of this interval
      - uses jump instructions to redirect the processor to the first instruction of this interval


6. takeover_syscall.cpp: takes over the syscall to complete the memory change and return value setting
    - 工作流程：
      - step1: Save the state of the current register to the program_intregs[32] array (currently only integer registers are saved, floating point has not been used yet)
      - step2: Restore the state of some registers of the checkpoint loader. If it is not restored, functions such as printf cannot be used, and global variables cannot be obtained at the same time
      - step4: Determine whether the number of current syscalls has exceeded the number of syscalls contained in this interval. If it exceeds, end the execution
      - step4: Read the runninginfo structure and find the information corresponding to the current syscall

      - step5: Determine whether the current syscall number is the same as the syscall number recorded in the checkpoint file. If it is not the same, there are some wrongs happened during the relaying. 
      - step6: Determine whether the current syscall needs to modify the memory data
          - Write data directly to memory according to bufaddr and recorded data size
      - step7: If the syscall has a return value, write it back to the a0 register (program_intregs[10] = infos->ret)
        - If there is no return value, write the old a0 value back to the a0 register
      - step9: Determine whether the current syscall is the last syscall. If yes, replace the address where the exit instruction is with the jump instruction
        - Complete the processing of the syscall and restore the register status 
        - Jump back to the return address of the syscall


7. Usage:
  - Build: ./riscv.sh
    - Set the your own riscv-toolchain in riscv.sh
    - The readckpt_gen.riscv will be linked to 0x1000000
  - Execute in riscv execution environments: ./readckpt_gen.riscv bench_ckpt.info bench.riscv 
1. The createCkpt.sh script sets the directory and input parameters for the GCC executable, as well as the parameters and directory for Gem5.
2. The createCkpt.sh script selects the setting file used as settings_pk.
   ```c
    //mmapend and stacktop setting, the default value of brkpoint is 0x1400000
    mmapend: 0x30000000
    stacktop: 0x74000000
    //The directory for generating checkpoint files is "ckpt" folder, with the prefix "gcc".
    ckptprefix: ./ckpt/gcc
    //从100000000指令开始，间隔1亿条生成一个checkpoint文件，共生成2个
    //Generate checkpoint files starting from instruction 100,000,000 with an interval of 100 million instructions. A total of 2 checkpoint files will be generated.
    //checkpoint1: Recording starts from 80 million instructions, with 20 million instructions reserved as warm-up. Information is recorded for 100 million instructions starting from 100 million.
    //checkpoint2: Recording starts from 180 million instructions, with 20 million instructions reserved as warm-up. Information is recorded for 100 million instructions starting from 200 million.
    ckptctrl: 100000000 100000000 20000000 2
   ```
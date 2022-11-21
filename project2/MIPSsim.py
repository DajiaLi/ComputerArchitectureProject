import os
import argparse

BinaryCodePath = "./sample.txt"


class MIPSsimulator:

    def __init__(self, BinaryCode=BinaryCodePath):
        self.R_function5 = {}
        self.R_function6 = {}
        self.I_opcode = {}
        self.J_opcode = {}
        self.BinaryCodePath = BinaryCode
        self.DisassembleOutput = "./disassembly.txt"
        self.SimulationOutput = "./simulation.txt"
        self.instructions = []
        self.instructions_print = []
        self.outputSimulation = None
        self.Registers = []
        self.Data = []
        self.instructionBeginIndex = 64
        self.DataBeginIndex = None
        self.IF_Unit = {}
        self.Pre_Issue_Buffer = []
        self.Pre_ALU_Queue = {}
        self.Post_ALU_Buffer = None  # [pc, cycle]
        self.Pre_ALUB_Queue = {}
        self.Post_ALUB_Buffer = None  # [pc, cycle]
        self.Pre_MEM_Queue = {}
        self.Post_MEM_Buffer = None  # [pc, cycle]
        self.ALUB_OP = ("SLL", "SRL", "SRA", "MUL")
        self.MEM_OP = ("LW", "SW")
        self.Register_status = []
        self.WaitWriteBack = []
        self.pc = 0  # 用于模拟
        self.Waiting_Instruction = None
        self.Executed_Instruction = None

    def inital(self):
        self.readAllOpcode()

        if os.path.exists(self.SimulationOutput):
            os.remove(self.SimulationOutput)
        self.outputSimulation = open(self.SimulationOutput, "a")

        if os.path.exists(self.DisassembleOutput):
            os.remove(self.DisassembleOutput)

        for i in range(0, 32):
            self.Registers.append(0)
            self.Register_status.append([])
        self.IF_Unit["Waiting Instruction"] = []
        self.IF_Unit["Executed Instruction"] = []
        self.Pre_ALU_Queue["Entry 0"] = None
        self.Pre_ALU_Queue["Entry 1"] = None
        self.Pre_ALUB_Queue["Entry 0"] = None
        self.Pre_ALUB_Queue["Entry 1"] = None
        self.Pre_MEM_Queue["Entry 0"] = None
        self.Pre_MEM_Queue["Entry 1"] = None

    def print(self):
        print(self.R_function5)
        print(self.R_function6)
        print(self.I_opcode)
        print(self.J_opcode)
        print(self.instructions)

    def readAllOpcode(self, ):
        file1 = open(r'./dependencies/R-function5.txt', 'r')
        lines = file1.read().split('\n')  # store the lines in a list
        lines = [x for x in lines if len(x) > 0]  # get read of the empty lines
        lines = [x for x in lines if x[0] != '#']  # get rid of comments
        lines = [x.rstrip().lstrip() for x in lines]  # get rid of fringe whitespaces

        for line in lines:
            op, code = line.split(' ')
            self.R_function5[op] = code

        file2 = open(r'./dependencies/R-function6.txt', 'r')
        lines = file2.read().split('\n')  # store the lines in a list
        lines = [x for x in lines if len(x) > 0]  # get read of the empty lines
        lines = [x for x in lines if x[0] != '#']  # get rid of comments
        lines = [x.rstrip().lstrip() for x in lines]  # get rid of fringe whitespaces

        for line in lines:
            op, code = line.split(' ')
            self.R_function6[op] = code

        file3 = open(r'./dependencies/I-opcode.txt', 'r')
        lines = file3.read().split('\n')  # store the lines in a list
        lines = [x for x in lines if len(x) > 0]  # get read of the empty lines
        lines = [x for x in lines if x[0] != '#']  # get rid of comments
        lines = [x.rstrip().lstrip() for x in lines]  # get rid of fringe whitespaces

        for line in lines:
            op, code = line.split(' ')
            self.I_opcode[op] = code

        file4 = open(r'./dependencies/J-opcode.txt', 'r')
        lines = file4.read().split('\n')  # store the lines in a list
        lines = [x for x in lines if len(x) > 0]  # get read of the empty lines
        lines = [x for x in lines if x[0] != '#']  # get rid of comments
        lines = [x.rstrip().lstrip() for x in lines]  # get rid of fringe whitespaces

        for line in lines:
            op, code = line.split(' ')
            self.J_opcode[op] = code

    def complement2source(self, comlement):
        res = list(comlement)
        first1 = False
        for i in range(len(comlement) - 1, -1, -1):
            if first1:
                if res[i] == '1':
                    res[i] = '0'
                else:
                    res[i] = '1'
            else:
                if res[i] == '1':
                    first1 = True
        return "".join(res)

    def disassemble(self):
        file = open(self.BinaryCodePath)
        lines = file.read().split('\n')
        lines = [x for x in lines if len(x) > 0]
        lines = [x for x in lines if x[0] != '#']  # get rid of comments
        lines = [x.rstrip().lstrip() for x in lines]

        pc = self.instructionBeginIndex
        mode = "instruction"

        output = open(self.DisassembleOutput, "a")

        for line in lines:
            # disassemble instructions
            if mode == "instruction":

                instruction = []
                instruction_print = []
                op = line[0:6]
                rs = line[6:11]
                rt = line[11:16]
                rd = line[16:21]
                shamt = line[21:26]
                funct = line[26:32]

                output.write(op[0] + " " + op[1:] + " ")
                output.write(rs + " ")
                output.write(rt + " ")
                output.write(rd + " ")
                output.write(shamt + " ")
                output.write(funct + "\t")
                output.write(str(pc) + "\t")
                pc = pc + 4

                if op in self.I_opcode.keys():
                    if self.I_opcode[op] == "BEQ":
                        output.write(
                            "%s R%d, R%d, #%d" % (self.I_opcode[op], int(rs, 2), int(rt, 2), int(line[16:32], 2) * 4))
                        instruction.append("BEQ")
                        instruction.append(int(rs, 2))
                        instruction.append(int(rt, 2))
                        instruction.append(int(line[16:32], 2) * 4)
                        instruction_print.append("BEQ")
                        instruction_print.append("R%d, R%d, #%d" % (int(rs, 2), int(rt, 2), int(line[16:32], 2) * 4))

                    elif self.I_opcode[op][0] == 'B' and self.I_opcode[op][-1] == 'Z':
                        output.write(
                            "%s R%d, #%d" % (self.I_opcode[op], int(rs, 2), int(line[16:32], 2) * 4))
                        instruction.append(self.I_opcode[op])
                        instruction.append(int(rs, 2))
                        instruction.append(int(line[16:32], 2) * 4)
                        instruction_print.append(self.I_opcode[op])
                        instruction_print.append("R%d, #%d" % (int(rs, 2), int(line[16:32], 2) * 4))

                    elif self.I_opcode[op][-1] == 'W':
                        output.write(
                            "%s R%d, %d(R%d)" % (self.I_opcode[op], int(rt, 2), int(line[16:32], 2), int(rs, 2)))
                        instruction.append(self.I_opcode[op])
                        instruction.append(int(rt, 2))
                        instruction.append(int(line[16:32], 2))
                        instruction.append(int(rs, 2))
                        instruction_print.append(self.I_opcode[op])
                        instruction_print.append("R%d, %d(R%d)" % (int(rt, 2), int(line[16:32], 2), int(rs, 2)))

                elif op in self.J_opcode.keys():
                    output.write("%s #%d" % (self.J_opcode[op], int(line[6:32], 2) * 4))
                    instruction.append(self.J_opcode[op])
                    instruction.append(int(line[6:32], 2) * 4)
                    instruction_print.append(self.J_opcode[op])
                    instruction_print.append("#%d" % (int(line[6:32], 2) * 4))

                elif op[0] == '0' and funct in self.R_function6.keys():
                    if funct == "001101":
                        output.write("BREAK")
                        mode = "operand"
                        instruction.append("BREAK")
                        instruction_print.append("BREAK")
                        self.DataBeginIndex = pc
                    elif shamt == "00000":  # 不是位移指令
                        output.write("%s R%d, R%d, R%d"
                                     % (self.R_function6[funct], int(rd, 2), int(rs, 2), int(rt, 2)))
                        instruction.append(self.R_function6[funct])
                        instruction.append("R")
                        instruction.append(int(rd, 2))
                        instruction.append(int(rs, 2))
                        instruction.append(int(rt, 2))
                        instruction_print.append(self.R_function6[funct])
                        instruction_print.append("R%d, R%d, R%d" % (int(rd, 2), int(rs, 2), int(rt, 2)))
                    else:  # 是位移指令
                        output.write("%s R%d, R%d, #%d"
                                     % (self.R_function6[funct], int(rd, 2), int(rt, 2), int(shamt, 2)))
                        instruction.append(self.R_function6[funct])
                        instruction.append(int(rd, 2))
                        instruction.append(int(rt, 2))
                        instruction.append(int(shamt, 2))
                        instruction_print.append(self.R_function6[funct])
                        instruction_print.append("R%d, R%d, #%d" % (int(rd, 2), int(rt, 2), int(shamt, 2)))

                elif op[0] == '1' and op[1:] in self.R_function5.keys():
                    output.write("%s R%d, R%d, #%d" %
                                 (self.R_function5[op[1:]], int(rt, 2), int(rs, 2), int(line[16:32], 2)))
                    instruction.append(self.R_function5[op[1:]])
                    instruction.append("I")
                    instruction.append(int(rt, 2))
                    instruction.append(int(rs, 2))
                    instruction.append(int(line[16:32], 2))
                    instruction_print.append(self.R_function5[op[1:]])
                    instruction_print.append("R%d, R%d, #%d" % (int(rt, 2), int(rs, 2), int(line[16:32], 2)))

                output.write("\n")
                self.instructions.append(instruction)
                self.instructions_print.append(instruction_print)

            elif mode == "operand":
                output.write(line + "\t")
                output.write(str(pc) + "\t")
                pc = pc + 4
                if line[0] == '1':
                    output.write("-")
                    output.write("%d\n" % (int(self.complement2source(line[1:]), base=2)))
                    self.Data.append(int(self.complement2source(line[1:]), base=2) * (-1))
                else:
                    output.write("%d\n" % int(line[1:], 2))
                    self.Data.append(int(line[1:], 2))

    def writeSimulationOutput(self, cycle):
        self.outputSimulation.write("-" * 20)
        self.outputSimulation.write("\nCycle:%d\n\n" % (cycle))
        self.outputSimulation.write("IF Unit:\n")
        self.outputSimulation.write("\tWaiting Instruction: ")
        if self.Waiting_Instruction is not None:
            self.outputSimulation.write(self.instructions_print[self.Waiting_Instruction[0]][0] + "\t" +
                                        self.instructions_print[self.Waiting_Instruction[0]][1])
        self.outputSimulation.write("\n")
        self.outputSimulation.write("\tExecuted Instruction: ")
        if self.Executed_Instruction is not None:
            if self.instructions[self.Executed_Instruction[0]][0] == "BREAK":
                self.outputSimulation.write("BREAK")
            else:
                self.outputSimulation.write(self.instructions_print[self.Executed_Instruction[0]][0] + "\t" +
                                            self.instructions_print[self.Executed_Instruction[0]][1])
        self.outputSimulation.write("\n")
        self.outputSimulation.write("Pre-Issue Buffer:\n")
        self.outputSimulation.write("\tEntry 0:")
        if len(self.Pre_Issue_Buffer) > 0:
            self.outputSimulation.write("[" + self.instructions_print[self.Pre_Issue_Buffer[0][0]][0] + "\t" +
                                        self.instructions_print[self.Pre_Issue_Buffer[0][0]][1] + "]")
        self.outputSimulation.write("\n")
        self.outputSimulation.write("\tEntry 1:")
        if len(self.Pre_Issue_Buffer) > 1:
            self.outputSimulation.write("[" + self.instructions_print[self.Pre_Issue_Buffer[1][0]][0] + "\t" +
                                        self.instructions_print[self.Pre_Issue_Buffer[1][0]][1] + "]")
        self.outputSimulation.write("\n")
        self.outputSimulation.write("\tEntry 2:")
        if len(self.Pre_Issue_Buffer) > 2:
            self.outputSimulation.write("[" + self.instructions_print[self.Pre_Issue_Buffer[2][0]][0] + "\t" +
                                        self.instructions_print[self.Pre_Issue_Buffer[2][0]][1] + "]")
        self.outputSimulation.write("\n")
        self.outputSimulation.write("\tEntry 3:")
        if len(self.Pre_Issue_Buffer) > 3:
            self.outputSimulation.write("[" + self.instructions_print[self.Pre_Issue_Buffer[3][0]][0] + "\t" +
                                        self.instructions_print[self.Pre_Issue_Buffer[3][0]][1] + "]")
        self.outputSimulation.write("\n")
        self.outputSimulation.write("Pre-ALU Queue:\n")
        self.outputSimulation.write("\tEntry 0:")
        if self.Pre_ALU_Queue["Entry 0"] is not None:
            self.outputSimulation.write("[" + self.instructions_print[self.Pre_ALU_Queue["Entry 0"][0]][0] + "\t" +
                                        self.instructions_print[self.Pre_ALU_Queue["Entry 0"][0]][1] + "]")
        self.outputSimulation.write("\n")
        self.outputSimulation.write("\tEntry 1:")
        if self.Pre_ALU_Queue["Entry 1"] is not None:
            self.outputSimulation.write("[" + self.instructions_print[self.Pre_ALU_Queue["Entry 1"][0]][0] + "\t" +
                                        self.instructions_print[self.Pre_ALU_Queue["Entry 1"][0]][1] + "]")
        self.outputSimulation.write("\n")
        self.outputSimulation.write("Post-ALU Buffer:")
        if self.Post_ALU_Buffer is not None:
            self.outputSimulation.write("[" + self.instructions_print[self.Post_ALU_Buffer[0]][0] + "\t" +
                                        self.instructions_print[self.Post_ALU_Buffer[0]][1] + "]")
        self.outputSimulation.write("\n")
        self.outputSimulation.write("Pre-ALUB Queue:\n")
        self.outputSimulation.write("\tEntry 0:")
        if self.Pre_ALUB_Queue["Entry 0"] is not None:
            self.outputSimulation.write("[" + self.instructions_print[self.Pre_ALUB_Queue["Entry 0"][0]][0] + "\t" +
                                        self.instructions_print[self.Pre_ALUB_Queue["Entry 0"][0]][1] + "]")
        self.outputSimulation.write("\n")
        self.outputSimulation.write("\tEntry 1:")
        if self.Pre_ALUB_Queue["Entry 1"] is not None:
            self.outputSimulation.write("[" + self.instructions_print[self.Pre_ALUB_Queue["Entry 1"][0]][0] + "\t" +
                                        self.instructions_print[self.Pre_ALUB_Queue["Entry 1"][0]][1] + "]")
        self.outputSimulation.write("\n")
        self.outputSimulation.write("Post-ALUB Buffer:")
        if self.Post_ALUB_Buffer is not None:
            self.outputSimulation.write("[" + self.instructions_print[self.Post_ALUB_Buffer[0]][0] + "\t" +
                                        self.instructions_print[self.Post_ALUB_Buffer[0]][1] + "]")
        self.outputSimulation.write("\n")
        self.outputSimulation.write("Pre-MEM Queue:")
        self.outputSimulation.write("\n")
        self.outputSimulation.write("\tEntry 0:")
        if self.Pre_MEM_Queue["Entry 0"] is not None:
            self.outputSimulation.write("[" + self.instructions_print[self.Pre_MEM_Queue["Entry 0"][0]][0] + "\t" +
                                        self.instructions_print[self.Pre_MEM_Queue["Entry 0"][0]][1] + "]")
        self.outputSimulation.write("\n")
        self.outputSimulation.write("\tEntry 1:")
        if self.Pre_MEM_Queue["Entry 1"] is not None:
            self.outputSimulation.write("[" + self.instructions_print[self.Pre_MEM_Queue["Entry 1"][0]][0] + "\t" +
                                        self.instructions_print[self.Pre_MEM_Queue["Entry 1"][0]][1] + "]")
        self.outputSimulation.write("\n")
        self.outputSimulation.write("Post-MEM Buffer:")
        if self.Post_MEM_Buffer is not None:
            self.outputSimulation.write("[" + self.instructions_print[self.Post_MEM_Buffer[0]][0] + "\t" +
                                        self.instructions_print[self.Post_MEM_Buffer[0]][1] + "]")
        self.outputSimulation.write("\n")

        self.outputSimulation.write("\nRegisters")

        self.outputSimulation.write("\nR00:")
        for i in range(0, 8):
            self.outputSimulation.write("\t%d" % (self.Registers[i]))
        self.outputSimulation.write("\nR08:")
        for i in range(8, 16):
            self.outputSimulation.write("\t%d" % (self.Registers[i]))
        self.outputSimulation.write("\nR16:")
        for i in range(16, 24):
            self.outputSimulation.write("\t%d" % (self.Registers[i]))
        self.outputSimulation.write("\nR24:")
        for i in range(24, 32):
            self.outputSimulation.write("\t%d" % (self.Registers[i]))

        self.outputSimulation.write("\n\nData")

        for i in range(0, len(self.Data)):
            if i % 8 == 0:
                self.outputSimulation.write("\n%d:" % (self.DataBeginIndex + 4 * i))
            self.outputSimulation.write("\t%d" % (self.Data[i]))
        self.outputSimulation.write("\n")

    def TomasuloIssueCheck(self, pc):
        """
        根据Tomsaulo算法判断index为pc的instruction能否issue
        :return: Ture or False
        """
        if self.instructions[pc][0] in ('ADD', 'SUB'):
            if self.instructions[pc][1] == 'R':
                # 前1个if用于用于排除[ADD	R1, R1, R5]，如果没有其他干扰，R1的status不为None，但实际上没有hazard
                if len(self.Register_status[self.instructions[pc][4]]) == 0 \
                        and len(self.Register_status[self.instructions[pc][3]]) == 1 \
                        and self.Register_status[self.instructions[pc][3]][0] == pc:
                    return True
                elif len(self.Register_status[self.instructions[pc][3]]) > 0 or self.Register_status[self.instructions[pc][4]]:
                    return False
                else:
                    return True
            elif self.instructions[pc][1] == 'I':
                if len(self.Register_status[self.instructions[pc][3]]) > 0:
                    return False
                else:
                    return True
        elif self.instructions[pc][0] == "LW":
            if len(self.Register_status[self.instructions[pc][3]]) > 0:
                return False
            return True
        elif self.instructions[pc][0] == "SW":
            if len(self.Register_status[self.instructions[pc][1]]) > 0 or len(self.Register_status[self.instructions[pc][3]]) > 0:
                # 如果原寄存器在状态表中被另一条LW指令占用，依然可以issue，因为SW指令执行始终在LW指令前
                preSW_All_LW = True
                if len(self.Register_status[self.instructions[pc][1]]) > 0:
                    for i in self.Register_status[self.instructions[pc][1]]:
                        if self.instructions[i][0] != "LW":
                            preSW_All_LW = False
                if len(self.Register_status[self.instructions[pc][3]]) > 0:
                    for i in self.Register_status[self.instructions[pc][3]]:
                        if self.instructions[i][0] != "LW":
                            preSW_All_LW = False
                return preSW_All_LW
            return True
        elif self.instructions[pc][0] in ("SLL", "SRL", ):
            if len(self.Register_status[self.instructions[pc][2]]) > 0:
                return False
            else:
                return True
        elif self.instructions[pc][0] in ("BLTZ", "BGTZ",):
            if len(self.Register_status[self.instructions[pc][1]]) > 0:
                return False
            else:
                return True

    def TomasuloRegisterChange(self, pc, mode):
        if mode == "reserve":
            if self.instructions[pc][0] in ('ADD', 'SUB'):
                self.Register_status[self.instructions[pc][2]].append(pc)
            elif self.instructions[pc][0] in ('SLL', 'SRL', "LW"):
                self.Register_status[self.instructions[pc][1]].append(pc)
        elif mode == "writeback":
            if self.instructions[pc][0] in ('ADD', 'SUB'):
                self.Register_status[self.instructions[pc][2]].remove(pc)
            elif self.instructions[pc][0] in ('SLL', 'SRL', "LW"):
                self.Register_status[self.instructions[pc][1]].remove(pc)

    def HandleBranchInstruction(self,cycle):
        if self.Waiting_Instruction is not None and self.TomasuloIssueCheck(self.Waiting_Instruction[0]):
            # 处理等待指令
            if self.Waiting_Instruction is not None and self.Waiting_Instruction[1] < cycle:
                self.Executed_Instruction = self.Waiting_Instruction
                self.Executed_Instruction[1] = cycle
                self.Waiting_Instruction = None

        # 处理跳转指令，改变PC值
        if self.Executed_Instruction is not None and self.Executed_Instruction[1] < cycle:
            if self.instructions[self.Executed_Instruction[0]][0] == "BLTZ":
                if self.Registers[self.instructions[self.Executed_Instruction[0]][1]] < 0:
                    self.pc += int(self.instructions[self.Executed_Instruction[0]][2] / 4)
            elif self.instructions[self.Executed_Instruction[0]][0] == "BGTZ":
                if self.Registers[self.instructions[self.Executed_Instruction[0]][1]] > 0:
                    self.pc += int(self.instructions[self.Executed_Instruction[0]][2] / 4)
            elif self.instructions[self.Executed_Instruction[0]][0] == "J":
                self.pc = int((self.instructions[self.Executed_Instruction[0]][1] - self.instructionBeginIndex) / 4)
            elif self.instructions[self.Executed_Instruction[0]][0] == "BREAK":
                exit()
            self.Executed_Instruction = None

    def Fetch2Pre_Issue_Buffer(self, cycle):
        fetchNum = 0  # 一次最多取两条, 最多容纳4条
        while (fetchNum < 2 and len(self.Pre_Issue_Buffer) < 4
               and self.Waiting_Instruction is None
               and self.Executed_Instruction is None):
            if self.instructions[self.pc][0] in ("BLTZ", "BGTZ", ):
                self.Waiting_Instruction = [self.pc, cycle]
                # 遇到跳转指令时后面所有的语句都要抛弃
                self.pc = self.pc + 1
                break
            elif self.instructions[self.pc][0] in ("J", "BREAK", ):
                self.Executed_Instruction = [self.pc, cycle]
                self.pc = self.pc + 1
                break
            else:
                self.Pre_Issue_Buffer.append([self.pc, cycle])
            # updata Tomsulo Register statue table
            self.TomasuloRegisterChange(self.pc, mode="reserve")
            fetchNum = fetchNum + 1
            self.pc = self.pc + 1

    def Issue2Pre_Queue(self, cycle):
        # Issue
        issueNum = 0  # 最多issue发射两条，可以不按顺序发射
        cur = 0  # 当前要探查的指令index
        while issueNum < 2 and len(self.Pre_Issue_Buffer) > 0 and cur < len(self.Pre_Issue_Buffer):
            # 本轮fetch的指令不能issue, 在Tomasulo Register Status表中目标寄存器被reserve的指令也不能issue
            if self.Pre_Issue_Buffer[cur][1] < cycle and self.TomasuloIssueCheck(self.Pre_Issue_Buffer[cur][0]):
                # Pre_Issue_Buffer[cur]中为ALU指令
                if (self.instructions[self.Pre_Issue_Buffer[cur][0]][0] not in self.ALUB_OP
                        and self.instructions[self.Pre_Issue_Buffer[cur][0]][0] not in self.MEM_OP):
                    # issue to pre_ALU entry0 if entry0 is empty
                    if self.Pre_ALU_Queue["Entry 0"] is None:
                        self.Pre_ALU_Queue["Entry 0"] = self.Pre_Issue_Buffer[cur]
                        self.Pre_ALU_Queue["Entry 0"][1] = cycle  # 更新cycle，同一个cycle到ALU unit的不能处理
                        del (self.Pre_Issue_Buffer[cur])
                        issueNum = issueNum + 1
                    # issue to pre_ALU entry0 if entry1 is empty
                    elif self.Pre_ALU_Queue["Entry 1"] is None:
                        self.Pre_ALU_Queue["Entry 1"] = self.Pre_Issue_Buffer[cur]
                        self.Pre_ALU_Queue["Entry 1"][1] = cycle
                        del (self.Pre_Issue_Buffer[cur])
                        issueNum = issueNum + 1
                    else:
                        # ALU 单元内容已满，向后探查
                        cur = cur + 1
                # Pre_Issue_Buffer[cur]中为MEM指令
                elif (self.instructions[self.Pre_Issue_Buffer[cur][0]][0] in self.MEM_OP):
                    # SW必须顺序执行，即SW指令必须为第一条时才能执行，cur=0
                    if self.instructions[self.Pre_Issue_Buffer[cur][0]][0] == "SW" and cur > 0:
                        cur = cur + 1
                        continue
                    # LW之前不能有SW指令
                    if self.instructions[self.Pre_Issue_Buffer[cur][0]][0] == "LW" and cur > 0:
                        pre_SW = False
                        t = cur - 1
                        while t >= 0:
                            if self.instructions[self.Pre_Issue_Buffer[t][0]][0] == "SW":
                                pre_SW = True
                                break
                            t = t - 1
                        if pre_SW:
                            cur = cur + 1
                            continue
                    # issue to pre_MEM entry0 if entry0 is empty
                    if self.Pre_MEM_Queue["Entry 0"] is None:
                        self.Pre_MEM_Queue["Entry 0"] = self.Pre_Issue_Buffer[cur]
                        self.Pre_MEM_Queue["Entry 0"][1] = cycle  # 更新cycle，同一个cycle到ALU unit的不能处理
                        del (self.Pre_Issue_Buffer[cur])
                        issueNum = issueNum + 1
                    # issue to pre_ALU entry0 if entry1 is empty
                    elif self.Pre_MEM_Queue["Entry 1"] is None:
                        self.Pre_MEM_Queue["Entry 1"] = self.Pre_Issue_Buffer[cur]
                        self.Pre_MEM_Queue["Entry 1"][1] = cycle
                        del (self.Pre_Issue_Buffer[cur])
                        issueNum = issueNum + 1
                    else:
                        # MEM 单元内容已满，向后探查
                        cur = cur + 1
                # Pre_Issue_Buffer[cur]中为ALUB指令
                elif (self.instructions[self.Pre_Issue_Buffer[cur][0]][0] in self.ALUB_OP):
                    # issue to pre_ALUB entry0 if entry0 is empty
                    if self.Pre_ALUB_Queue["Entry 0"] is None:
                        self.Pre_ALUB_Queue["Entry 0"] = self.Pre_Issue_Buffer[cur]
                        self.Pre_ALUB_Queue["Entry 0"][1] = cycle  # 更新cycle，同一个cycle到ALU unit的不能处理
                        del (self.Pre_Issue_Buffer[cur])
                        issueNum = issueNum + 1
                    # issue to pre_ALUB entry0 if entry1 is empty
                    elif self.Pre_ALUB_Queue["Entry 1"] is None:
                        self.Pre_ALUB_Queue["Entry 1"] = self.Pre_Issue_Buffer[cur]
                        self.Pre_ALUB_Queue["Entry 1"][1] = cycle
                        del (self.Pre_Issue_Buffer[cur])
                        issueNum = issueNum + 1
                    else:
                        # MEM 单元内容已满，向后探查
                        cur = cur + 1
            else:
                cur = cur + 1

    def Pre_Queue2Post_Buffer(self, cycle):
        # ALU, ALUB, MEM work memory parallelly
        # ALU
        if self.Post_ALU_Buffer is None:
            if self.Pre_ALU_Queue["Entry 0"] is not None and self.Pre_ALU_Queue["Entry 0"][1] < cycle:
                self.Post_ALU_Buffer = self.Pre_ALU_Queue["Entry 0"]
                self.Post_ALU_Buffer[1] = cycle
                self.Pre_ALU_Queue["Entry 0"] = self.Pre_ALU_Queue["Entry 1"]
                self.Pre_ALU_Queue["Entry 1"] = None

        # MEM
        if self.Post_MEM_Buffer is None:
            if self.Pre_MEM_Queue["Entry 0"] is not None and self.Pre_MEM_Queue["Entry 0"][1] < cycle:
                # SW不需要送到buffer,就地处理
                if self.instructions[self.Pre_MEM_Queue["Entry 0"][0]][0] == "SW":
                    self.Data[int((self.instructions[self.Pre_MEM_Queue["Entry 0"][0]][2] + self.Registers[self.instructions[self.Pre_MEM_Queue["Entry 0"][0]][3]] - self.DataBeginIndex) / 4)] \
                        = self.Registers[self.instructions[self.Pre_MEM_Queue["Entry 0"][0]][1]]
                else:
                    self.Post_MEM_Buffer = self.Pre_MEM_Queue["Entry 0"]
                    self.Post_MEM_Buffer[1] = cycle
                # 后继指令上去
                self.Pre_MEM_Queue["Entry 0"] = self.Pre_MEM_Queue["Entry 1"]
                self.Pre_MEM_Queue["Entry 1"] = None

        # ALUB
        if self.Post_ALUB_Buffer is None:
            if self.Pre_ALUB_Queue["Entry 0"] is not None and self.Pre_ALUB_Queue["Entry 0"][1] < cycle - 1:
                self.Post_ALUB_Buffer = self.Pre_ALUB_Queue["Entry 0"]
                self.Post_ALUB_Buffer[1] = cycle
                self.Pre_ALUB_Queue["Entry 0"] = self.Pre_ALUB_Queue["Entry 1"]
                self.Pre_ALUB_Queue["Entry 1"] = None

    def HandlePost_Buffer(self, cycle):
        # Post ALU Buffer
        if self.Post_ALU_Buffer is not None and self.Post_ALU_Buffer[1] < cycle:
            if self.instructions[self.Post_ALU_Buffer[0]][0] == 'ADD':
                if self.instructions[self.Post_ALU_Buffer[0]][1] == 'R':
                    self.Registers[self.instructions[self.Post_ALU_Buffer[0]][2]] = \
                        self.Registers[self.instructions[self.Post_ALU_Buffer[0]][3]] + self.Registers[
                            self.instructions[self.Post_ALU_Buffer[0]][4]]
                elif self.instructions[self.Post_ALU_Buffer[0]][1] == 'I':
                    self.Registers[self.instructions[self.Post_ALU_Buffer[0]][2]] = \
                        self.Registers[self.instructions[self.Post_ALU_Buffer[0]][3]] + \
                        self.instructions[self.Post_ALU_Buffer[0]][4]
            elif self.instructions[self.Post_ALU_Buffer[0]][0] == 'SUB':
                if self.instructions[self.Post_ALU_Buffer[0]][1] == 'R':
                    self.Registers[self.instructions[self.Post_ALU_Buffer[0]][2]] = \
                        self.Registers[self.instructions[self.Post_ALU_Buffer[0]][3]] - self.Registers[
                            self.instructions[self.Post_ALU_Buffer[0]][4]]
                elif self.instructions[self.Post_ALU_Buffer[0]][1] == 'I':
                    self.Registers[self.instructions[self.Post_ALU_Buffer[0]][2]] = \
                        self.Registers[self.instructions[self.Post_ALU_Buffer[0]][3]] - \
                        self.instructions[self.Post_ALU_Buffer[0]][4]
            # send to writeback
            self.Post_ALU_Buffer[1] = cycle
            self.WaitWriteBack.append(self.Post_ALU_Buffer)
            # 写回之后清空buffer
            self.Post_ALU_Buffer = None

        # Post MEM Buffer
        if self.Post_MEM_Buffer is not None and self.Post_MEM_Buffer[1] < cycle:
            if self.instructions[self.Post_MEM_Buffer[0]][0] == 'LW':
                self.Registers[self.instructions[self.Post_MEM_Buffer[0]][1]] = \
                    self.Data[int((self.instructions[self.Post_MEM_Buffer[0]][2] + self.Registers[self.instructions[self.Post_MEM_Buffer[0]][3]] - self.DataBeginIndex) / 4)]
            # send to writeback
            self.Post_MEM_Buffer[1] = cycle
            self.WaitWriteBack.append(self.Post_MEM_Buffer)
            # 写回之后清空buffer
            self.Post_MEM_Buffer = None

        # Post ALUB Buffer
        if self.Post_ALUB_Buffer is not None and self.Post_ALUB_Buffer[1] < cycle:
            if self.instructions[self.Post_ALUB_Buffer[0]][0] == 'SLL':
                self.Registers[self.instructions[self.Post_ALUB_Buffer[0]][1]] = self.Registers[self.instructions[self.Post_ALUB_Buffer[0]][2]] * pow(2,self.instructions[self.Post_ALUB_Buffer[0]][3])
            elif self.instructions[self.Post_ALUB_Buffer[0]][0] == 'SRL':
                self.Registers[self.instructions[self.Post_ALUB_Buffer[0]][1]] = int(self.Registers[self.instructions[self.Post_ALUB_Buffer[0]][2]] / pow(2,self.instructions[self.Post_ALUB_Buffer[0]][3]))
            # send to writeback
            self.Post_ALUB_Buffer[1] = cycle
            self.WaitWriteBack.append(self.Post_ALUB_Buffer)
            # 写回之后清空buffer
            self.Post_ALUB_Buffer = None

    def WriteBack(self, cycle):
        while len(self.WaitWriteBack) > 0:
            self.TomasuloRegisterChange(self.WaitWriteBack[0][0], mode="writeback")
            del(self.WaitWriteBack[0])

    def simulation(self):
        """
        instruction like:
        ['ADD', 'R', 1, 0, 0], ['ADD', 'I', 2, 0, 5]
        ['BEQ', 1, 2, 68], ['SLL', 16, 1, 2], ['LW', 3, 148, 16]
        ['J', 72], ['BREAK']
        """
        cycle = 0
        while True:
            cycle = cycle + 1


            # handle branch instruction
            self.HandleBranchInstruction(cycle=cycle)

            # fetch
            self.Fetch2Pre_Issue_Buffer(cycle=cycle)

            # Issue
            self.Issue2Pre_Queue(cycle=cycle)

            self.HandlePost_Buffer(cycle=cycle)

            self.Pre_Queue2Post_Buffer(cycle=cycle)

            self.WriteBack(cycle=cycle)

            # output
            self.writeSimulationOutput(cycle=cycle)
            #
            # if cycle == 230:
            #     print()
            # if cycle == 231:
            #     break


if __name__ == '__main__':
    # parser = argparse.ArgumentParser()
    # parser.add_argument("BinaryCodePath", help="the path of sample", type=str)
    # args = parser.parse_args()
    # mips = MIPSsimulator(args.BinaryCodePath)
    mips = MIPSsimulator()
    mips.inital()
    mips.disassemble()
    mips.print()
    # mips.writeSimulationOutput(1)
    mips.simulation()

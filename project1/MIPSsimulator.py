import os

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
        self.DataBeginIndex = None


    def inital(self):
        self.readAllOpcode()

        if os.path.exists(self.SimulationOutput):
            os.remove(self.SimulationOutput)
        self.outputSimulation = open(self.SimulationOutput, "a")

        for i in range(0, 33):
            self.Registers.append(0)

    def print(self):
        print(self.R_function5)
        print(self.R_function6)
        print(self.I_opcode)
        print(self.J_opcode)

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

        pc = 64
        mode = "instruction"
        if os.path.exists(self.DisassembleOutput):
            os.remove(self.DisassembleOutput)
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

                output.write(op + " ")
                output.write(rs + " ")
                output.write(rt + " ")
                output.write(rd + " ")
                output.write(shamt + " ")
                output.write(funct + "\t")
                output.write(str(pc) + "\t")
                pc = pc + 4

                if op in self.I_opcode.keys():
                    if self.I_opcode[op] == "BEQ":
                        output.write("%s R%d, R%d, #%d" % (self.I_opcode[op], int(rs, 2), int(rt, 2), int(line[16:32], 2) * 4))
                        instruction.append("BEQ")
                        instruction.append(int(rs, 2))
                        instruction.append(int(rt, 2))
                        instruction.append(int(line[16:32], 2) * 4)
                        instruction_print.append("BEQ")
                        instruction_print.append("R%d, R%d, #%d" % (int(rs, 2), int(rt, 2), int(line[16:32], 2) * 4))

                    elif self.I_opcode[op][0] =='B' and self.I_opcode[op][-1] == 'Z':
                        output.write(
                            "%s R%d, #%d" % (self.I_opcode[op], int(rs, 2), int(line[16:32], 2) * 4))
                        instruction.append(self.I_opcode[op])
                        instruction.append(int(rs, 2))
                        instruction.append(int(line[16:32], 2) * 4)
                        instruction_print.append(self.I_opcode[op])
                        instruction_print.append("R%d, #%d" % (int(rs, 2), int(line[16:32], 2) * 4))

                    elif self.I_opcode[op][-1] == 'W':
                        output.write(
                            "%s R%d, %d(R%d)" % (self.I_opcode[op], int(rt, 2), int(line[16:32], 2), int(rs, 2)) )
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

                elif op[0] == '1'and op[1:] in self.R_function5.keys():
                    output.write("%s R%d, R%d, #%d" %
                                 (self.R_function5[op[1:]], int(rt,2), int(rs, 2), int(line[16:32],2)))
                    instruction.append(self.R_function5[op[1:]])
                    instruction.append("I")
                    instruction.append(int(rt, 2))
                    instruction.append(int(rs, 2))
                    instruction.append(int(line[16:32], 2))
                    instruction_print.append(self.R_function5[op[1:]])
                    instruction_print.append("R%d, R%d, #%d" % (int(rt, 2), int(rs, 2), int(line[16:32],2)))


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

    def writeSimulationOutput(self, cycle, address, instructionIndex):
        self.outputSimulation.write("-" * 20)
        self.outputSimulation.write("\nCycle:%d\t%d\t%s\t%s\n\nRegisters\n"
                                    % (cycle, address, self.instructions_print[instructionIndex][0], self.instructions_print[instructionIndex][1]))
        self.outputSimulation.write("R00:")
        for i in range(0, 16):
            self.outputSimulation.write("\t%d" % (self.Registers[i]))
        self.outputSimulation.write("\nR16:")
        for i in range(16, 32):
            self.outputSimulation.write("\t%d" % (self.Registers[i]))
        self.outputSimulation.write("\n\nData")
        for i in range(0, len(self.Data)):
            if i % 8 == 0:
                self.outputSimulation.write("\n%d:" % (self.DataBeginIndex + 4 * i))
            self.outputSimulation.write("\t%d" % (self.Data[i]))
        self.outputSimulation.write("\n")

    def simulation(self):
        """
        instruction like:
        ['ADD', 'R', 1, 0, 0], ['ADD', 'I', 2, 0, 5]
        ['BEQ', 1, 2, 68], ['SLL', 16, 1, 2], ['LW', 3, 148, 16]
        ['J', 72], ['BREAK']
        """
        pass

if __name__ == '__main__':
    mips = MIPSsimulator()
    mips.inital()
    mips.disassemble()
    print(mips.instructions)
    print(mips.instructions_print)
    print(mips.Data)
    print(mips.DataBeginIndex)
    mips.writeSimulationOutput(1, 64, 0)
    # print(mips.complement2source("1111111111111111111111111111101"))

"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = self.reg[0]
        self.FL = 0b00000000
        self.commands = {
            0b00000001: self.hlt,
            0b10000010: self.ldi,
            0b01000111: self.prn,
            0b10100010: self.mul,
            0b01000101: self.push,
            0b01000110: self.pop,
            0b01010000: self.call,
            0b00010001: self.ret,
            #New for SC
            0b10100111: self.cmp1,
            0b01010100: self.jmp,
            0b01010101: self.jeq,
            0b01010110: self.jne,
            0b10100000: self.add,
            #Strech
            0b10101000: self.and1
            0b10101010: self.or1,
            0b10101011: self.xor,
            0b01101001: self.not1,
            0b10101100: self.shl,
            0b10101101: self.shr,
            0b10100100: self.mod
        }


    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, value, address):
        self.ram[address] = value

    def hlt(self, operand_a, operand_b):
        return (0, False)

    def ldi(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b
        return (3, True)

    def prn(self, operand_a, operand_b):
        print(self.reg[operand_a])
        return (2, True)

    def mul(self, operand_a, operand_b):
        self.alu("MUL", operand_a, operand_b)
        return (3, True)

    def push(self, operand_a, operand_b):
        self.reg[7] -= 1
        sp = self.reg[7]
        value = self.reg[operand_a]
        self.ram[sp] = value
        return (2, True)

    def pop(self, operand_a, operand_b):
        sp = self.reg[7]
        value = self.ram[sp]
        self.reg[operand_a] = value
        self.reg[7] += 1
        return (2, True)

    def call(self, operand_a, operand_b):
        self.reg[7] -= 1
        self.ram[self.reg[7]] = self.pc + 2
        update_reg = self.ram[self.pc + 1]
        self.pc = self.reg[update_reg]
        return (None, True)

    def ret(self, operand_a, operand_b):
        self.pc = self.ram[self.reg[7]]
        self.reg[7] += 1
        return (None, True)

    def cmp1(self, operand_a, operand_b):
        self.alu("CMP", operand_a, operand_b)
        return (3, True)

    def jmp(self, operand_a, operand_b):
        self.pc = self.reg[operand_a]
        return (None, True)

    def jeq(self, operand_a, operand_b):
        if self.FL & 0b00000001 == 1:
            self.pc = self.reg[operand_a]
        else:
            self.pc += 2
        return (None, True)

    def jne(self, operand_a, operand_b):
        if self.FL & 0b00000001 == 0:
            self.pc = self.reg[operand_a]
        else:
            self.pc += 2
        return (None, True)

    def add(self, operand_a, operand_b):
        self.alu("ADD", operand_a, operand_b)
        return (3, True)

    def and1(self, operand_a, operand_b):
        self.alu("AND", operand_a, operand_b)
        return (3, True)

    def or1(self, operand_a, operand_b):
        self.alu("OR", operand_a, operand_b)
        return (3, True)

    def xor(self, operand_a, operand_b):
        self.alu("XOR", operand_a, operand_b)
        return (3, True)

    def not1(self, operand_a, operand_b):
        self.alu("NOT", operand_a, operand_b)
        return (3, True)

    def shl(self, operand_a, operand_b):
        self.alu("SHL", operand_a, operand_b)
        return (3, True)

    def shr(self, operand_a, operand_b):
        self.alu("SHR", operand_a, operand_b)
        return (3, True)

    def mod(self, operand_a, operand_b):
        self.alu("MOD", operand_a, operand_b)
        return (3, True)


    def load(self, program=None):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:
        if program == None:
            program = [
                # From print8.ls8
                0b10000010, # LDI R0,8
                0b00000000,
                0b00001000,
                0b01000111, # PRN R0
                0b00000000,
                0b00000001, # HLT
            ]

            for instruction in program:
                self.ram[address] = instruction
                address += 1

        elif program == "test":
            program = [
                # From print8.ls8
                0b10000010, # LDI R0,10
                0b00000000,
                0b00001010,
                0b10000010, # LDI R1,20
                0b00000001,
                0b00010100,
                0b10000010, # LDI R2,TEST1
                0b00000010,
                0b00010011,
                0b10100111, # CMP R0,R1
                0b00000000,
                0b00000001,
                0b01010101, # JEQ R2
                0b00000010,
                0b10000010, # LDI R3,1
                0b00000011,
                0b00000001,
                0b01000111, # PRN R3
                0b00000011,
                # TEST1 (address 19):
                0b10000010, # LDI R2,TEST2
                0b00000010,
                0b00100000,
                0b10100111, # CMP R0,R1
                0b00000000,
                0b00000001,
                0b01010110, # JNE R2
                0b00000010,
                0b10000010, # LDI R3,2
                0b00000011,
                0b00000010,
                0b01000111, # PRN R3
                0b00000011,
                # TEST2 (address 32):
                0b10000010, # LDI R1,10
                0b00000001,
                0b00001010,
                0b10000010, # LDI R2,TEST3
                0b00000010,
                0b00110000,
                0b10100111, # CMP R0,R1
                0b00000000,
                0b00000001,
                0b01010101, # JEQ R2
                0b00000010,
                0b10000010, # LDI R3,3
                0b00000011,
                0b00000011,
                0b01000111, # PRN R3
                0b00000011,
                # TEST3 (address 48):
                0b10000010, # LDI R2,TEST4
                0b00000010,
                0b00111101,
                0b10100111, # CMP R0,R1
                0b00000000,
                0b00000001,
                0b01010110, # JNE R2
                0b00000010,
                0b10000010, # LDI R3,4
                0b00000011,
                0b00000100,
                0b01000111, # PRN R3
                0b00000011,
                # TEST4 (address 61):
                0b10000010, # LDI R3,5
                0b00000011,
                0b00000101,
                0b01000111, # PRN R3
                0b00000011,
                0b10000010, # LDI R2,TEST5
                0b00000010,
                0b01001001,
                0b01010100, # JMP R2
                0b00000010,
                0b01000111, # PRN R3
                0b00000011,
                # TEST5 (address 73):
                0b00000001, # HLT
            ]

            for instruction in program:
                self.ram[address] = instruction
                address += 1

        elif program != None:
            try:
                with open(program) as f:
                    for line in f:
                        #parse out comments
                        comment_split = line.strip().split("#")
                        # Cast number string to int
                        value = comment_split[0].strip()
                        #ignore blank lines
                        if value == "":
                            continue
                        #populate memory array
                        self.ram[address] = int(value, 2)
                        address += 1   
            except FileNotFoundError:
                print("File not found")
                sys.exit(2)


    def alu(self, op, reg_a=None, reg_b=None):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
                self.reg[reg_a] = (self.reg[reg_a] * self.reg[reg_b])
        elif op == "CMP":
            """Compare the values in two registers."""
            valueA = self.reg[reg_a]
            valueB = self.reg[reg_b]

            if valueA == valueB:
                self.FL = 0b00000001

            if valueA < valueB:
                self.FL = 0b00000100

            if valueA > valueB:
                self.FL = 0b00000010
        elif op == "AND":
            """Compare the values in two registers."""
            valueA = self.reg[reg_a]
            valueB = self.reg[reg_b]
            self.reg[operand_a] = valueA & valueB
        elif op == "OR":
            """Compare the values in two registers."""
            valueA = self.reg[reg_a]
            valueB = self.reg[reg_b]
            self.reg[operand_a] = valueA | valueB
        elif op == "XOR":
            """Compare the values in two registers."""
            valueA = self.reg[reg_a]
            valueB = self.reg[reg_b]
            self.reg[operand_a] = valueA ^ valueB
        elif op == "NOT":
            self.reg[reg_a] = ~reg_a
        elif op == "SHL":
            """Compare the values in two registers."""
            valueA = self.reg[reg_a]
            valueB = self.reg[reg_b]
            self.reg[self.operand_a] = (valueA << valueB) % 255
        elif op == "SHR":
            """Compare the values in two registers."""
            valueA = self.reg[reg_a]
            valueB = self.reg[reg_b]
            self.reg[self.operand_a] = (valueA >> valueB) % 255
        elif op == "MOD":
            """Compare the values in two registers."""
            valueA = self.reg[reg_a]
            valueB = self.reg[reg_b]
            self.reg[self.operand_a] = valueA % valueB
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        running = True

        while running:
            ir = self.ram[self.pc]
            # print(ir)

            operand_a = self.ram_read(self.pc + 1)
            # print(operand_a)
            operand_b = self.ram_read(self.pc + 2)
            # print(operand_b)
            # print("try")
            try: 
                operation_output = self.commands[ir](operand_a, operand_b)
                running = operation_output[1]
                if operation_output[0] == None:
                    # print("call or ret done")
                    continue
                else:
                    self.pc += operation_output[0]

            except:
                print(f"command: {ir}")
                sys.exit()

"""
Utility functions and helpers for LC-3 simulator tests.
"""


class LC3TestUtils:
    """Utility class for LC-3 testing operations."""
    
    @staticmethod
    def create_instruction(opcode, **kwargs):
        """
        Create an LC-3 instruction with specified opcode and fields.
        
        Args:
            opcode: The instruction opcode (e.g., 0x1000 for ADD)
            **kwargs: Instruction fields (dr, sr1, sr2, imm, etc.)
        
        Returns:
            16-bit instruction word
        """
        instruction = opcode
        
        # Add destination register
        if 'dr' in kwargs:
            instruction |= (kwargs['dr'] & 0x7) << 9
        
        # Add source register 1
        if 'sr1' in kwargs:
            instruction |= (kwargs['sr1'] & 0x7) << 6
        
        # Add source register 2 or immediate value
        if 'sr2' in kwargs:
            instruction |= kwargs['sr2'] & 0x7
        elif 'imm5' in kwargs:
            instruction |= 0x20  # Set immediate mode bit
            instruction |= kwargs['imm5'] & 0x1F
        elif 'imm6' in kwargs:
            instruction |= kwargs['imm6'] & 0x3F
        elif 'imm9' in kwargs:
            instruction |= kwargs['imm9'] & 0x1FF
        elif 'imm11' in kwargs:
            instruction |= kwargs['imm11'] & 0x7FF
        
        # Add base register for LDR/STR
        if 'base' in kwargs:
            instruction |= (kwargs['base'] & 0x7) << 6
        
        # Add condition codes for BR
        if 'n' in kwargs and kwargs['n']:
            instruction |= 0x800
        if 'z' in kwargs and kwargs['z']:
            instruction |= 0x400
        if 'p' in kwargs and kwargs['p']:
            instruction |= 0x200
        
        # Add JSR mode bit
        if 'jsr_mode' in kwargs and kwargs['jsr_mode']:
            instruction |= 0x800
        
        # Add trap vector
        if 'trap_vector' in kwargs:
            instruction |= kwargs['trap_vector'] & 0xFF
        
        return instruction
    
    @staticmethod
    def sign_extend(value, bit_count):
        """
        Sign extend a value to 16 bits.
        
        Args:
            value: The value to sign extend
            bit_count: Number of bits in the original value
        
        Returns:
            Sign-extended 16-bit value
        """
        if value & (1 << (bit_count - 1)):
            # Sign bit is set, extend with 1s
            return value | (0xFFFF << bit_count)
        return value & ((1 << bit_count) - 1)
    
    @staticmethod
    def create_test_program(instructions, start_addr=0x3000):
        """
        Create a test program from a list of instructions.
        
        Args:
            instructions: List of instruction dictionaries or raw values
            start_addr: Starting address for the program
        
        Returns:
            List of 16-bit instruction words
        """
        program = []
        
        for instr in instructions:
            if isinstance(instr, dict):
                # Convert instruction dictionary to instruction word
                opcode = instr.pop('opcode')
                word = LC3TestUtils.create_instruction(opcode, **instr)
                program.append(word)
            else:
                # Raw instruction word
                program.append(instr)
        
        return program
    
    @staticmethod
    def verify_condition_codes(simulator, expected_n=None, expected_z=None, expected_p=None):
        """
        Verify condition codes match expected values.
        
        Args:
            simulator: The LC-3 simulator instance
            expected_n: Expected N flag value (None to skip check)
            expected_z: Expected Z flag value (None to skip check)
            expected_p: Expected P flag value (None to skip check)
        
        Returns:
            True if all specified condition codes match
        """
        n, z, p = simulator.get_condition_codes()
        
        if expected_n is not None and n != expected_n:
            return False
        if expected_z is not None and z != expected_z:
            return False
        if expected_p is not None and p != expected_p:
            return False
        
        return True
    
    @staticmethod
    def setup_memory_block(simulator, start_addr, data):
        """
        Set up a block of memory with data.
        
        Args:
            simulator: The LC-3 simulator instance
            start_addr: Starting address
            data: List of values to store
        """
        for i, value in enumerate(data):
            simulator.set_memory(start_addr + i, value)
    
    @staticmethod
    def verify_memory_block(simulator, start_addr, expected_data):
        """
        Verify a block of memory matches expected data.
        
        Args:
            simulator: The LC-3 simulator instance
            start_addr: Starting address
            expected_data: List of expected values
        
        Returns:
            True if all memory locations match expected values
        """
        for i, expected in enumerate(expected_data):
            actual = simulator.get_memory(start_addr + i)
            if actual != expected:
                return False
        return True
    
    @staticmethod
    def run_until_halt_or_limit(simulator, max_cycles=1000):
        """
        Run simulator until halt or cycle limit.
        
        Args:
            simulator: The LC-3 simulator instance
            max_cycles: Maximum cycles to run
        
        Returns:
            Tuple of (halted, cycles_executed)
        """
        cycles = 0
        while not simulator.is_halted() and cycles < max_cycles:
            simulator.step()
            cycles += 1
        
        return simulator.is_halted(), cycles
    
    @staticmethod
    def create_string_in_memory(simulator, start_addr, string):
        """
        Store a null-terminated string in memory.
        
        Args:
            simulator: The LC-3 simulator instance
            start_addr: Starting address for the string
            string: The string to store
        
        Returns:
            Address immediately after the null terminator
        """
        for i, char in enumerate(string):
            simulator.set_memory(start_addr + i, ord(char))
        
        # Add null terminator
        simulator.set_memory(start_addr + len(string), 0)
        
        return start_addr + len(string) + 1


class LC3ProgramBuilder:
    """Helper class for building LC-3 programs programmatically."""
    
    def __init__(self, start_addr=0x3000):
        self.instructions = []
        self.labels = {}
        self.current_addr = start_addr
        self.start_addr = start_addr
    
    def add_instruction(self, opcode, **kwargs):
        """Add an instruction to the program."""
        instruction = LC3TestUtils.create_instruction(opcode, **kwargs)
        self.instructions.append(instruction)
        self.current_addr += 1
        return self
    
    def add_data(self, value):
        """Add a data word to the program."""
        self.instructions.append(value & 0xFFFF)
        self.current_addr += 1
        return self
    
    def add_string(self, string):
        """Add a null-terminated string to the program."""
        for char in string:
            self.add_data(ord(char))
        self.add_data(0)  # Null terminator
        return self
    
    def add_label(self, label):
        """Add a label at the current position."""
        self.labels[label] = self.current_addr
        return self
    
    def get_label_offset(self, label, from_addr=None):
        """Get the offset to a label from a given address."""
        if from_addr is None:
            from_addr = self.current_addr
        
        if label not in self.labels:
            raise ValueError(f"Label '{label}' not found")
        
        return self.labels[label] - from_addr
    
    def build(self):
        """Build and return the complete program."""
        return self.instructions.copy()
    
    # Convenience methods for common instructions
    def add_add(self, dr, sr1, sr2=None, imm=None):
        if imm is not None:
            return self.add_instruction(0x1000, dr=dr, sr1=sr1, imm5=imm)
        else:
            return self.add_instruction(0x1000, dr=dr, sr1=sr1, sr2=sr2)
    
    def add_and(self, dr, sr1, sr2=None, imm=None):
        if imm is not None:
            return self.add_instruction(0x5000, dr=dr, sr1=sr1, imm5=imm)
        else:
            return self.add_instruction(0x5000, dr=dr, sr1=sr1, sr2=sr2)
    
    def add_not(self, dr, sr):
        return self.add_instruction(0x9000, dr=dr, sr1=sr)
    
    def add_br(self, offset, n=False, z=False, p=False):
        if not (n or z or p):
            n = z = p = True  # Unconditional branch
        return self.add_instruction(0x0000, imm9=offset, n=n, z=z, p=p)
    
    def add_jmp(self, base_reg):
        return self.add_instruction(0xC000, base=base_reg)
    
    def add_jsr(self, offset):
        return self.add_instruction(0x4000, jsr_mode=True, imm11=offset)
    
    def add_jsrr(self, base_reg):
        return self.add_instruction(0x4000, base=base_reg)
    
    def add_ld(self, dr, offset):
        return self.add_instruction(0x2000, dr=dr, imm9=offset)
    
    def add_ldi(self, dr, offset):
        return self.add_instruction(0xA000, dr=dr, imm9=offset)
    
    def add_ldr(self, dr, base_reg, offset):
        return self.add_instruction(0x6000, dr=dr, base=base_reg, imm6=offset)
    
    def add_lea(self, dr, offset):
        return self.add_instruction(0xE000, dr=dr, imm9=offset)
    
    def add_st(self, sr, offset):
        return self.add_instruction(0x3000, dr=sr, imm9=offset)
    
    def add_sti(self, sr, offset):
        return self.add_instruction(0xB000, dr=sr, imm9=offset)
    
    def add_str(self, sr, base_reg, offset):
        return self.add_instruction(0x7000, dr=sr, base=base_reg, imm6=offset)
    
    def add_trap(self, vector):
        return self.add_instruction(0xF000, trap_vector=vector)
    
    def add_halt(self):
        return self.add_trap(0x25)
    
    def add_out(self):
        return self.add_trap(0x21)
    
    def add_getc(self):
        return self.add_trap(0x20)
    
    def add_puts(self):
        return self.add_trap(0x22)
    
    def add_in(self):
        return self.add_trap(0x23)


class LC3Assembler:
    """Simple assembler for LC-3 assembly language."""
    
    OPCODES = {
        'ADD': 0x1000,
        'AND': 0x5000,
        'BR': 0x0000,
        'BRN': 0x0800,
        'BRZ': 0x0400,
        'BRP': 0x0200,
        'BRNZ': 0x0C00,
        'BRNP': 0x0A00,
        'BRZP': 0x0600,
        'BRNZP': 0x0E00,
        'JMP': 0xC000,
        'JSR': 0x4800,
        'JSRR': 0x4000,
        'LD': 0x2000,
        'LDI': 0xA000,
        'LDR': 0x6000,
        'LEA': 0xE000,
        'NOT': 0x9000,
        'RET': 0xC1C0,  # JMP R7
        'ST': 0x3000,
        'STI': 0xB000,
        'STR': 0x7000,
        'TRAP': 0xF000,
        'HALT': 0xF025,
        'OUT': 0xF021,
        'GETC': 0xF020,
        'PUTS': 0xF022,
        'IN': 0xF023,
    }
    
    @staticmethod
    def assemble_line(line):
        """
        Assemble a single line of LC-3 assembly.
        
        Args:
            line: Assembly language line
        
        Returns:
            16-bit instruction word or None for directives/labels
        """
        line = line.strip().upper()
        if not line or line.startswith(';'):
            return None
        
        parts = line.replace(',', ' ').split()
        if not parts:
            return None
        
        mnemonic = parts[0]
        if mnemonic not in LC3Assembler.OPCODES:
            return None
        
        # This is a simplified assembler - real implementation would be much more complex
        return LC3Assembler.OPCODES[mnemonic]
    
    @staticmethod
    def assemble_program(assembly_lines):
        """
        Assemble a complete LC-3 program.
        
        Args:
            assembly_lines: List of assembly language lines
        
        Returns:
            List of 16-bit instruction words
        """
        program = []
        for line in assembly_lines:
            instruction = LC3Assembler.assemble_line(line)
            if instruction is not None:
                program.append(instruction)
        return program


def create_test_environment():
    """Create a standardized test environment with utilities."""
    return {
        'utils': LC3TestUtils,
        'builder': LC3ProgramBuilder,
        'assembler': LC3Assembler,
    }

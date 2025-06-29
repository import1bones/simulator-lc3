# LC-3 State Machine Architecture

## Overview

The LC-3 state machine implements a microcode-based processor control unit that executes LC-3 instructions through a series of well-defined states. This implementation prioritizes readability, maintainability, and correctness.

## Architecture

### File Organization

- **`state_machine.h/.cpp`**: Main state machine logic and control flow
- **`state_definitions.h`**: Named constants for all state numbers and types
- **`signals.h/.cpp`**: Processor control signals and condition codes
- **`states.h/.cpp`**: Individual state implementations (microinstructions)
- **`state_machine_utils.cpp`**: Debugging and utility functions
- **`ext.h`**: Extension and helper functions

### Design Principles

1. **Named Constants**: All magic numbers replaced with meaningful names
2. **Separation of Concerns**: State transition logic separated from state execution
3. **Clear Function Responsibilities**: Each function has a single, well-defined purpose
4. **Comprehensive Documentation**: Every function and important variable documented
5. **Error Handling**: Proper validation and error detection
6. **Debugging Support**: Built-in logging and state monitoring capabilities

## State Machine Flow

### Fetch-Decode-Execute Cycle

```
FETCH1 → FETCH2 → FETCH3 → DECODE → [Execution States] → FETCH1
```

### State Categories

#### 1. Fetch Cycle States
- **FETCH1 (18)**: Start of instruction fetch, set up memory access
- **FETCH2 (33)**: Continue fetch operation  
- **FETCH3 (35)**: Complete fetch, load instruction register
- **DECODE (32)**: Decode instruction and determine execution path

#### 2. Execution States
Each instruction type has dedicated execution states:

**Arithmetic/Logic:**
- ADD_STATE (1): Add operation
- AND_STATE (5): Bitwise AND operation  
- NOT_STATE (9): Bitwise complement

**Control Flow:**
- BR_STATE (0): Conditional branch
- JMP_STATE (12): Unconditional jump
- JSR_STATE (21): Jump to subroutine
- JSRR_STATE (20): Jump to subroutine register
- RTI_STATE (8): Return from interrupt

**Memory Access:**
- LD_STATE1/2/3: Load operations (multiple cycles)
- LDI_STATE1/2/3/4: Load indirect (multiple cycles)
- LDR_STATE1/2/3: Load register (multiple cycles)
- ST_STATE1/2: Store operations
- STI_STATE1/2: Store indirect
- STR_STATE1/2: Store register
- LEA_STATE (14): Load effective address

**System Operations:**
- TRAP_STATE1/2/3/4: TRAP instruction handling (multiple cycles)

### State Transition Logic

#### Fetch Transitions
```cpp
FETCH1 → check_interrupts() → FETCH2 or INTERRUPT_STATE
FETCH2 → FETCH3 (always)
FETCH3 → DECODE (always)
```

#### Decode Transitions
```cpp
DECODE → instruction_opcode → appropriate_execution_state
```

#### Execution Transitions
- Simple instructions: return to FETCH1
- Multi-cycle operations: proceed to next state in sequence
- Conditional branches: check BEN flag

## Control Signals

### Primary Signals
- **INT**: Interrupt request
- **R**: Memory ready signal
- **BEN**: Branch enable (computed from condition codes)
- **PSR_15**: Privilege mode (0=user, 1=supervisor)
- **ACV**: Access control violation

### Condition Codes
- **N**: Negative flag (MSB set)
- **Z**: Zero flag (result = 0)
- **P**: Positive flag (result > 0 and MSB clear)

### Signal Functions
- **SET_CC(value)**: Update condition codes based on result
- **SET_BEN()**: Compute branch enable from instruction and condition codes
- **SET_ACV()**: Check for memory access violations

## Key Improvements

### 1. Readability Enhancements
```cpp
// Before: Magic numbers
case 18: // FETCH1
    current_state = 33; // FETCH2

// After: Named constants  
case FETCH1:
    return FETCH2;
```

### 2. Function Decomposition
```cpp
// Before: One large switch statement
void state_machine() {
    switch(current_state) {
        // 50+ cases in one function
    }
}

// After: Specialized functions
uint8_t get_next_state() {
    switch(current_state) {
        case FETCH1: return handle_fetch_transition();
        case DECODE: return handle_decode_transition();
        default: return handle_execution_transition();
    }
}
```

### 3. Error Handling
```cpp
// Validation
if (!is_valid_state(current_state)) {
    machine_error = true;
    return;
}

// Bounds checking
if (pointer_counter > UINT16_MAX) {
    machine_error = true;
    break;
}
```

### 4. Debugging Support
```cpp
// State name resolution
const char* state_name = get_state_name(current_state);

// Transition logging
log_state_transition(old_state, new_state);

// State classification
bool is_fetch = is_fetch_state(current_state);
```

## Usage Examples

### Basic Execution
```cpp
// Initialize
pointer_count_t pc = 0x3000;
word_t memory[UINT16_MAX];
register_t registers[8];

// Execute program
state_machine(pc, memory, registers);

// Check results
if (machine_error) {
    printf("Execution error at PC: 0x%04X\n", pc);
}
```

### Debug Mode
```cpp
// Enable state transition logging
#define DEBUG_STATE_MACHINE

// Run with monitoring
while (!machine_halted) {
    uint8_t old_state = current_state;
    execute_current_state();
    uint8_t new_state = get_next_state();
    log_state_transition(old_state, new_state);
    current_state = new_state;
}
```

## Performance Considerations

### Optimizations
1. **Inline Functions**: Critical path functions marked inline
2. **Lookup Tables**: State names stored in hash map for O(1) access
3. **Branch Prediction**: Most common transitions (fetch cycle) handled first
4. **Minimal Function Calls**: Core execution loop optimized for speed

### Memory Usage
- State machine variables: ~50 bytes
- State name lookup table: ~500 bytes
- No dynamic allocation in critical path

## Testing Integration

The improved state machine integrates seamlessly with the pytest test suite:

```python
# Test state transitions
def test_fetch_cycle(simulator):
    simulator.step()  # FETCH1 → FETCH2
    simulator.step()  # FETCH2 → FETCH3  
    simulator.step()  # FETCH3 → DECODE
    
# Test error conditions
def test_invalid_instruction(simulator):
    simulator.set_memory(0x3000, 0xD000)  # Invalid opcode
    simulator.step()
    assert simulator.machine_error == True
```

## Future Enhancements

### Planned Improvements
1. **Interrupt Handling**: Complete interrupt processing implementation
2. **Exception Handling**: Privilege violations and illegal instructions
3. **Performance Monitoring**: Cycle counting and instruction statistics
4. **State Machine Visualization**: Graphical state transition display
5. **Hot Path Optimization**: Profile-guided optimization for common instruction sequences

### Extensibility
The modular design allows easy addition of:
- New instructions
- Additional debugging features  
- Performance counters
- Alternative execution modes

## Conclusion

The refactored state machine provides a clean, maintainable, and well-documented implementation of the LC-3 processor control unit. The separation of concerns, comprehensive error handling, and debugging support make it suitable for both educational use and further development.

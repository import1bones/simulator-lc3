# LC-3 Simulator Condition Coverage Report

**Total Tests**: 90
**Passed Tests**: 82 (91.1%)
**Failed Tests**: [{'name': 'test_loop_with_data', 'category': 'Integration', 'issue': 'PC-relative addressing calculation', 'expected': 'R0 = 6', 'actual': 'R0 = 12290', 'root_cause': 'Sample program offset calculation incorrect'}, {'name': 'test_subroutine_call_and_return', 'category': 'Integration', 'issue': 'JSR/RET instruction sequence', 'expected': 'R0 = 1', 'actual': 'R0 = 0', 'root_cause': 'Return address/stack management'}, {'name': 'test_factorial_program', 'category': 'Integration', 'issue': 'Complex program infinite loop', 'expected': 'Halted = True', 'actual': 'Halted = False', 'root_cause': 'Branch instruction addressing'}, {'name': 'test_fibonacci_program', 'category': 'Integration', 'issue': 'Complex program infinite loop', 'expected': 'Halted = True', 'actual': 'Halted = False', 'root_cause': 'Branch instruction addressing'}, {'name': 'test_string_processing', 'category': 'Integration', 'issue': 'String processing logic', 'expected': 'R1 = 5', 'actual': 'R1 = 0', 'root_cause': 'Indirect addressing in string processing'}, {'name': 'test_negative_offset_addressing', 'category': 'Memory', 'issue': "2's complement sign extension", 'expected': 'R0 = 0xDEAD', 'actual': 'R0 = 0', 'root_cause': 'Negative offset calculation in LDR'}, {'name': 'test_load_store_cycle', 'category': 'Memory', 'issue': 'PC-relative addressing base', 'expected': 'R0 = 0x1234', 'actual': 'R0 = 0', 'root_cause': 'PC increment timing in LD/ST'}, {'name': 'test_indirect_load_store', 'category': 'Memory', 'issue': 'Indirect addressing chain', 'expected': 'Memory[0x5000] = 0xBEEF', 'actual': 'Memory[0x5000] = 0', 'root_cause': 'STI instruction implementation'}]
**Condition Coverage**: 61/75 (81.3%)

## Instruction-Level Condition Coverage

| Instruction | Conditions | Covered | Rate | Status |
|-------------|------------|---------|------|---------|
| **ADD** | 8 | 8 | 100% | ✅ Complete |
| **AND** | 6 | 6 | 100% | ✅ Complete |
| **NOT** | 2 | 2 | 100% | ✅ Complete |
| **BR** | 7 | 7 | 100% | ✅ Complete |
| **JMP** | 2 | 2 | 100% | ✅ Complete |
| **JSR** | 4 | 2 | 50% | ⚠️ Partial |
| **LD** | 6 | 4 | 67% | ⚠️ Partial |
| **LDI** | 6 | 3 | 50% | ⚠️ Partial |
| **LDR** | 6 | 4 | 67% | ⚠️ Partial |
| **LEA** | 2 | 2 | 100% | ✅ Complete |
| **ST** | 6 | 4 | 67% | ⚠️ Partial |
| **STI** | 6 | 3 | 50% | ⚠️ Partial |
| **STR** | 6 | 6 | 100% | ✅ Complete |
| **TRAP** | 8 | 8 | 100% | ✅ Complete |

## Test Category Coverage

| Category | Tests | Passed | Failed | Rate | Status |
|----------|-------|--------|--------|------|---------|
| **Basic Functionality** | 16 | 16 | 0 | 100.0% | ✅ Excellent |
| **Instruction Execution** | 26 | 26 | 0 | 100.0% | ✅ Excellent |
| **I/O Operations** | 16 | 16 | 0 | 100.0% | ✅ Excellent |
| **Memory Operations** | 24 | 21 | 3 | 87.5% | ⚠️ Good |
| **Integration Tests** | 8 | 3 | 5 | 37.5% | ❌ Needs Work |

## Failed Tests by Category

### Integration Test Failures

**test_loop_with_data**:
- Issue: PC-relative addressing calculation
- Expected: `R0 = 6`
- Actual: `R0 = 12290`
- Root Cause: Sample program offset calculation incorrect

**test_subroutine_call_and_return**:
- Issue: JSR/RET instruction sequence
- Expected: `R0 = 1`
- Actual: `R0 = 0`
- Root Cause: Return address/stack management

**test_factorial_program**:
- Issue: Complex program infinite loop
- Expected: `Halted = True`
- Actual: `Halted = False`
- Root Cause: Branch instruction addressing

**test_fibonacci_program**:
- Issue: Complex program infinite loop
- Expected: `Halted = True`
- Actual: `Halted = False`
- Root Cause: Branch instruction addressing

**test_string_processing**:
- Issue: String processing logic
- Expected: `R1 = 5`
- Actual: `R1 = 0`
- Root Cause: Indirect addressing in string processing

### Memory Test Failures

**test_negative_offset_addressing**:
- Issue: 2's complement sign extension
- Expected: `R0 = 0xDEAD`
- Actual: `R0 = 0`
- Root Cause: Negative offset calculation in LDR

**test_load_store_cycle**:
- Issue: PC-relative addressing base
- Expected: `R0 = 0x1234`
- Actual: `R0 = 0`
- Root Cause: PC increment timing in LD/ST

**test_indirect_load_store**:
- Issue: Indirect addressing chain
- Expected: `Memory[0x5000] = 0xBEEF`
- Actual: `Memory[0x5000] = 0`
- Root Cause: STI instruction implementation

## Coverage Gaps Analysis

### Instructions with Incomplete Condition Coverage

- **JSR**: 2 conditions not tested (50% coverage)
- **LD**: 2 conditions not tested (67% coverage)
- **LDI**: 3 conditions not tested (50% coverage)
- **LDR**: 2 conditions not tested (67% coverage)
- **ST**: 2 conditions not tested (67% coverage)
- **STI**: 3 conditions not tested (50% coverage)

## Recommendations

### Priority 1: Critical Fixes
1. Fix PC-relative addressing (affects 4 tests)
2. Fix negative offset sign extension (affects 1 test)

### Priority 2: Instruction Coverage
1. Complete JSR/RET sequence testing
2. Add negative offset tests for LD/LDR/ST/STR
3. Complete indirect addressing tests for LDI/STI

### Priority 3: Integration Testing
1. Create simpler integration tests that pass
2. Fix complex program sample code
3. Add more realistic program examples
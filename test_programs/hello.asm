.ORIG x3000

; Simple test program for LC-3 simulator
; Loads some values and performs basic operations

MAIN    AND R0, R0, #0     ; Clear R0
        ADD R0, R0, #5     ; R0 = 5
        ADD R1, R0, #3     ; R1 = 8 (5 + 3)
        AND R2, R1, R0     ; R2 = R1 & R0 = 8 & 5 = 0
        NOT R3, R0         ; R3 = ~R0 = ~5
        ADD R4, R1, R0     ; R4 = R1 + R0 = 8 + 5 = 13
        
        ; Test branching
        ADD R0, R0, #0     ; Set condition codes for R0
        BRp POSITIVE       ; Branch if positive
        BRnzp END         ; Should not execute
        
POSITIVE ADD R5, R0, #10   ; R5 = R0 + 10 = 15

END     HALT              ; End program

.END

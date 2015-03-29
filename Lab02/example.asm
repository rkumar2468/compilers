 .globl main

 .data
 str4: .asciiz "\n" 
 memory: .word 0 1 2 3 4

 .text
main:
 li $t0, 10
 li $t1, 11
 add $t1, $t0, $t1

## Reading input from stdin ##
 li $v0, 5
 syscall

 ori $t2, $v0, 0
 ori $a0, $t1, 0

 ## Adding New Line ##
 ori $t8, $a0, 0
 la $a0, str4
 li $v0, 4
 syscall

 ## Printing Integer ##
 ori $a0, $t8, 0
 li $v0, 1
 syscall

 ori $a0, $t2, 0

 ## Adding New Line ##
 ori $t8, $a0, 0
 la $a0, str4
 li $v0, 4
 syscall

 ## Printing Integer ##
 ori $a0, $t8, 0
 li $v0, 1
 syscall

 add $t2, $t0, $t1
 ori $a0, $t2, 0

 ## Adding New Line ##
 ori $t8, $a0, 0
 la $a0, str4
 li $v0, 4
 syscall

 ## Printing Integer ##
 ori $a0, $t8, 0
 li $v0, 1
 syscall

 li $t1, 10
 add $t0, $t1, $t2
 mult $t1, $t0
 mflo $a0

 ## Adding New Line ##
 ori $t8, $a0, 0
 la $a0, str4
 li $v0, 4
 syscall

 ## Printing Integer ##
 ori $a0, $t8, 0
 li $v0, 1
 syscall


 ## Exit ##
 la $a0, str4
 li $v0, 4
 syscall

 li $v0, 10
 syscall


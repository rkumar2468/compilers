 .globl main

 .data
 str4: .asciiz "\n" 
 memory: .word 0 1 2 3 4

 .text
main:

## Reading input from stdin ##
 li $v0, 5
 syscall


 ori $t2, $v0, $zero

 
 li $t8, 5
 
 ori $t1, $t8, $zero

 
 ori $t8, $t1, $zero

 li $t9, 1
 sub $v0, $t8, $t9

 ori $t1, $v0, $zero

 
 ori $t8, $t0, $zero

 mult $t8, $t1

 ori $t0, $LO, $zero

 
 ori $t8, $t1, $zero

 add $v0, $t8, $t0

 ori $t0, $v0, $zero

 
 ori $t8, $t2, $zero

 add $v0, $t8, $t0

 ori $t1, $v0, $zero

 
 ori $t8, $t1, $zero

 addi $v0, $t8, 1

 ori $a0, $v0, $zero

 
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


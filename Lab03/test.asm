 .globl main

 .data
 str4: .asciiz "\n" 
 memory: .word 0 1 2 3 4

 .text
main:

  LABEL0:

 li $t8, 1
 
 beq $t8, $zero,  LABEL1

 
 li $t8, 1
 
 ori $t1, $t8, $zero

 
 beq $zero, $zero,  LABEL0
  LABEL1:

## Reading input from stdin ##
 li $v0, 5
 syscall


 ori $t1, $v0, $zero

 
 ori $t8, $t1, 0

 sub $t9, $zero, $t8

 ori $t2, $t9, $zero

 
## Reading input from stdin ##
 li $v0, 5
 syscall


 ori $t0, $v0, $zero

 
 ori $t8, $t1, 0

 sub $t9, $zero, $t8

 ori $t8, $t1, $zero

 add $v0, $t8, $t9

 ori $t2, $v0, $zero

 
 ori $t8, $t1, $zero

 div $t8, $t2

 ori $t8, $LO, $zero

 mult $t8, $t0

 ori $t8, $LO, $zero

 li $t9, 10
 div $t8, $t9

 ori $t8, $t1, $zero

 sub $v0, $t8, $LO

 ori $t0, $v0, $zero

 
 ori $a0, $t2, $zero

 
 ## Adding New Line ##
 ori $t8, $a0, 0
 la $a0, str4
 li $v0, 4
 syscall

 ## Printing Integer ##
 ori $a0, $t8, 0
 li $v0, 1
 syscall


 ori $t8, $t1, $zero

 add $v0, $t8, $t1

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


 ori $t8, $t1, $zero

 sub $v0, $t8, $t1

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


 ori $t8, $t1, 0

 sub $t9, $zero, $t8

 ori $t8, $t1, $zero

 add $v0, $t8, $t9

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


 ori $t8, $t1, $zero

 mult $t8, $t1

 ori $a0, $LO, $zero

 
 ## Adding New Line ##
 ori $t8, $a0, 0
 la $a0, str4
 li $v0, 4
 syscall

 ## Printing Integer ##
 ori $a0, $t8, 0
 li $v0, 1
 syscall


 ori $t8, $t1, $zero

 div $t8, $t1

 ori $a0, $LO, $zero

 
 ## Adding New Line ##
 ori $t8, $a0, 0
 la $a0, str4
 li $v0, 4
 syscall

 ## Printing Integer ##
 ori $a0, $t8, 0
 li $v0, 1
 syscall


 ori $t8, $t1, $zero

 div $t8, $t1

 ori $a0, $HI, $zero

 
 ## Adding New Line ##
 ori $t8, $a0, 0
 la $a0, str4
 li $v0, 4
 syscall

 ## Printing Integer ##
 ori $a0, $t8, 0
 li $v0, 1
 syscall


 ori $t8, $t1, $zero

 sgt $t9, $t8, $zero
 blez $t8, LABEL2
 sgt $t9, $t1, $zero

LABEL2:

 ori $a0, $t9, $zero

 
 ## Adding New Line ##
 ori $t8, $a0, 0
 la $a0, str4
 li $v0, 4
 syscall

 ## Printing Integer ##
 ori $a0, $t8, 0
 li $v0, 1
 syscall


 li $t8, 0

 sgt $t9, $t8, $zero
 blez $t8, LABEL3
 sgt $t9, $t1, $zero

LABEL3:

 ori $a0, $t9, $zero

 
 ## Adding New Line ##
 ori $t8, $a0, 0
 la $a0, str4
 li $v0, 4
 syscall

 ## Printing Integer ##
 ori $a0, $t8, 0
 li $v0, 1
 syscall


 ori $t8, $t1, $zero

 sgt $t9, $t8, $zero
 bgtz $t8, LABEL4
 sgt $t9, $t1, $zero

LABEL4:

 ori $a0, $t9, $zero

 
 ## Adding New Line ##
 ori $t8, $a0, 0
 la $a0, str4
 li $v0, 4
 syscall

 ## Printing Integer ##
 ori $a0, $t8, 0
 li $v0, 1
 syscall


 li $t8, 0

 sgt $t9, $t8, $zero
 bgtz $t8, LABEL5

 sgt $t9, $t1, $zero

LABEL5:

 ori $a0, $t9, $zero

 
 ## Adding New Line ##
 ori $t8, $a0, 0
 la $a0, str4
 li $v0, 4
 syscall

 ## Printing Integer ##
 ori $a0, $t8, 0
 li $v0, 1
 syscall


 ori $t8, $t1 $zero

 seq $v0, $t1, $t8


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


 ori $t8, $t1 $zero

 li $t9, 4
 seq $v0, $t9, $t8


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


 ori $t8, $t1 $zero

 sne $v0, $t1, $t8


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


 ori $t8, $t1 $zero

 li $t9, 4
 sne $v0, $t9, $t8


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


 ori $t8, $t1 $zero

 sgt $v0, $t1, $t8


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


 ori $t8, $t1 $zero

 sge $v0, $t1, $t8


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


 ori $t8, $t1 $zero

 slt $v0, $t1, $t8


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


 ori $t8, $t1 $zero

 sle $v0, $t1, $t8


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


 ori $t8, $t1, 0

 sub $t9, $zero, $t8

 ori $a0, $t9, $zero

 
 ## Adding New Line ##
 ori $t8, $a0, 0
 la $a0, str4
 li $v0, 4
 syscall

 ## Printing Integer ##
 ori $a0, $t8, 0
 li $v0, 1
 syscall


 ori $t8, $t1, 0

 seq $t9, $t8, $zero

 ori $a0, $t9, $zero

 
 ## Adding New Line ##
 ori $t8, $a0, 0
 la $a0, str4
 li $v0, 4
 syscall

 ## Printing Integer ##
 ori $a0, $t8, 0
 li $v0, 1
 syscall


 li $t8, $0

 seq $t9, $t8, $zero

 ori $a0, $t9, $zero

 
 ## Adding New Line ##
 ori $t8, $a0, 0
 la $a0, str4
 li $v0, 4
 syscall

 ## Printing Integer ##
 ori $a0, $t8, 0
 li $v0, 1
 syscall


 li $t8, 100
 
 ori $t0, $t8, $zero

 
 blez $t1,  LABEL6

 
 li $t8, 10
 
 ori $a0, $t8, $zero

 
 ## Adding New Line ##
 ori $t8, $a0, 0
 la $a0, str4
 li $v0, 4
 syscall

 ## Printing Integer ##
 ori $a0, $t8, 0
 li $v0, 1
 syscall

 LABEL6:

 ori $t8, $t1, 0

 seq $t9, $t8, $zero

 beq $t9, $zero,  LABEL7

 
 li $t8, 20
 
 ori $a0, $t8, $zero

 
 ## Adding New Line ##
 ori $t8, $a0, 0
 la $a0, str4
 li $v0, 4
 syscall

 ## Printing Integer ##
 ori $a0, $t8, 0
 li $v0, 1
 syscall


 li $t8, 1
 
 ori $t0, $t8, $zero

 
 beq $zero, $zero,  LABEL8

  LABEL7:

 li $t8, 30
 
 ori $a0, $t8, $zero

 
 ## Adding New Line ##
 ori $t8, $a0, 0
 la $a0, str4
 li $v0, 4
 syscall

 ## Printing Integer ##
 ori $a0, $t8, 0
 li $v0, 1
 syscall

 LABEL8:

 li $t8, 10
 
 ori $t1, $t8, $zero

 
  LABEL9:

 ori $t8, $t1 $zero

 li $t9, 120
 sgt $v0, $t9, $t8


 beq $v0, $zero,  LABEL10

 
 ori $a0, $t1, $zero

 
 ## Adding New Line ##
 ori $t8, $a0, 0
 la $a0, str4
 li $v0, 4
 syscall

 ## Printing Integer ##
 ori $a0, $t8, 0
 li $v0, 1
 syscall


 ori $t8, $t1, $zero

 li $t9, 1
 sub $v0, $t8, $t9

 ori $t1, $v0, $zero

 
 beq $zero, $zero,  LABEL9
  LABEL10:

 ori $a0, $t0, $zero

 
 ## Adding New Line ##
 ori $t8, $a0, 0
 la $a0, str4
 li $v0, 4
 syscall

 ## Printing Integer ##
 ori $a0, $t8, 0
 li $v0, 1
 syscall


 li $t8, 2
 
 ori $t1, $t8, $zero

 
 blez $t1,  LABEL11

 
 blez $t1,  LABEL12

 
 ori $t8, $t1, $zero

 li $t9, 2
 sub $v0, $t8, $t9

 beq $v0, $zero,  LABEL13

 
 li $t8, 111
 
 ori $a0, $t8, $zero

 
 ## Adding New Line ##
 ori $t8, $a0, 0
 la $a0, str4
 li $v0, 4
 syscall

 ## Printing Integer ##
 ori $a0, $t8, 0
 li $v0, 1
 syscall


 beq $zero, $zero,  LABEL14

  LABEL13:

 li $t8, 11
 
 ori $a0, $t8, $zero

 
 ## Adding New Line ##
 ori $t8, $a0, 0
 la $a0, str4
 li $v0, 4
 syscall

 ## Printing Integer ##
 ori $a0, $t8, 0
 li $v0, 1
 syscall

 LABEL14:
 LABEL12:
 LABEL11:

 ## Exit ##
 la $a0, str4
 li $v0, 4
 syscall

 li $v0, 10
 syscall


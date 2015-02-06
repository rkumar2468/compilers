## Question 1: Hailstone Sequence in MIPS ##

.globl	main

.data
## Basic message strings ##
str1: .asciiz "\nEnter a number: "
str2: .asciiz "\nSequence: "
str3: .asciiz ", "
str4: .asciiz "\n"
str5: .asciiz "-------Hailstone Sequence Generator.!-------\n"

.text

hailstone:
	la $a0, str5
	li $v0, 4 # print_string syscall number
	syscall
	jr $ra

main:
	jal hailstone	# Prints a description about the MIPS program.

## Reading input
	la $a0, str1
	li $v0, 4 # print_string syscall number
	syscall
	li $v0, 5	# read_int syscall number
	syscall
	ori $t0, $v0, 0	# Storing the entered value into $t0

## Generating hailstone sequence	##
	blez $t0, exit	# Initial condition check for negative numbers.
	la $a0, str2
	li $v0, 4 # print_string syscall number - for printing Sequence message.
	syscall

loop:
	li $t1, 1
	beq $t0, $t1, end
	jal printnum
	jal printCommaSpace
	li $t2, 2
	div $t0, $t2
	mfhi $t3	# Cannot use HI directly -- reason ??
	beq $t3, $t1, odd # Odd num check.
	b even
odd:
	li $t4, 3
	multu $t0, $t4
	mflo $t0
	addi $t0, $t0, 1
	b loop
even:
	mflo $t0
	b loop

printCommaSpace:
	la $a0, str3
	li $v0, 4 # print_string syscall number
	syscall
	jr $ra	# To return back to the caller.

printnum:
	move $a0, $t0
	li $v0, 1 # print_number syscall number
	syscall
	jr $ra	# To return back to the caller.
	
end:
	li $a0, 1
	li $v0, 1 # print_number syscall number
	syscall
	nop

exit:
#Calling Exit System Call - This is mandatory
	la $a0, str4
	li $v0, 4 # print_string syscall number
	syscall
	li $v0, 10
	syscall

## End of the Program ##

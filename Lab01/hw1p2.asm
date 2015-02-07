##############################################################
## Question 2: GCD in MIPS				    ##
## Input: Two positive integers.			    ##
## Output: GCD of the two numbers.	  		    ##
##############################################################

.globl	main

.data
## Basic message strings ##
str1: .asciiz "\nEnter two numbers: "
str2: .asciiz "\nGCD: "
str3: .asciiz "\n"
str5: .asciiz "-------GCD in MIPS.!-------\n"

.text

programText:
	la $a0, str5
	li $v0, 4 # print_string syscall number
	syscall
	jr $ra

main:
	jal programText	# Prints a description about the MIPS program.

## Reading input
	la $a0, str1
	li $v0, 4	# print_string syscall number
	syscall
	li $v0, 5	# read_int syscall number
	syscall
	ori $t0, $v0, 0	# Storing the first number into $t0
	li $v0, 5
	syscall
	ori $t1, $v0, 0	# Storing the second number into $t1
	

## Computing GCD of the two numbers	##
	bltz $t0, exit	# Initial condition check for negative numbers.
	bltz $t1, exit	# Initial condition check for negative numbers.

	## Either of the numbers is a non-zero positive number ##
	la $a0, str2
	li $v0, 4 	# print_string syscall number - for printing the message.
	syscall

gcd:
	li $zero, 0
	beq $t0, $zero,	first	# If first number is "0" - print second number.
	beq $t1, $zero,	second	# If second number is "0" - print second number.
		
	slt $t4, $t1, $t0	# Check for the greater number.
	beq $t4, $zero, next
## If a > b
	sub $t0, $t0, $t1
	j gcd
## Else 
next:
	ori $t5, $t0, 0	# Copying a to $t5 register
	ori $t0, $t1, 0	# Copying b to a
	sub $t1, $t1, $t5
	j gcd

first:
	move $t3, $t1
	j end
second:
	move $t3, $t0

end:
	ori $a0, $t3, 0
	li $v0, 1 # print_number syscall number
	syscall

exit:
#Calling Exit System Call - This is mandatory
	la $a0, str3	# A new line character.
	li $v0, 4 # print_string syscall number 
	syscall

	li $v0, 10
	syscall

## End of the Program ##

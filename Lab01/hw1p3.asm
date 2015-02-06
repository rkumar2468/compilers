## Question 3: Find maximum k value for which n*(2^k) >= (k!) holds for a given "n" in MIPS ##

.globl	main

.data
## Basic message strings ##
str1: .asciiz "\nEnter a number: "
str2: .asciiz "\n The highest value of k satisfying n*2^k >= k!: "
str3: .asciiz "\n"
# str4: .asciiz "Factorial: "
# str5: .asciiz "Powers of 2: "
str6: .asciiz "-------Computing the least k satisfying n*2^k < k!.!-------\n"

.text

programText:
	la $a0, str6
	li $v0, 4 # print_string syscall number
	syscall
	jr $ra

## The below computes the factorial of a number present in $t7	##
## The return value will stored in $v0	##
factorial:
	li $zero, 0
	li $t8, 1
	li $t9, 1
floop:
	beq $t7, $zero, felse
## if a != 0
	multu $t8, $t7
	mflo $t8
	subu $t7, $t7, $t9
	j floop
## Else if a == 0
felse:
	ori $v0, $t8, 0
	jr $ra

## Computing Powers of 2 ##
power:
	li $s1, 2
	li $zero, 0
	li $t8, 1
	li $t9, 1
ploop:
	beq $s0, $zero, pelse	## $s0 contains the exponent value ##
## if exp != 0
	multu $t8, $s1
	mflo $t8
	subu $s0, $s0, $t9
	j ploop
	
## else 
pelse:
	ori $v0, $t8, 0
	jr $ra

main:
	jal programText	# Prints a description about the MIPS program.

## Reading input
	la $a0, str1
	li $v0, 4	# print_string syscall number
	syscall
	li $v0, 5	# read_int syscall number
	syscall
	ori $t0, $v0, 0	# Storing the number "n" into $t0

## Finding suitable k for which the expression holds	##
	bltz $t0, exit	# Initial condition check for negative numbers.

	## Either of the numbers is a non-zero positive number ##
	la $a0, str2
	li $v0, 4 # print_string syscall number - for printing the message.
	syscall
	
	li $t1, 0	# Initializing k to 0
	li $zero, 0
	li $s2, 1
	beq $t0, $zero, inputzero
loop:
	move $s0, $t1
	jal power	# Computing 2^k
	ori $t2, $v0, 0
	move $t7, $t1
	jal factorial	# Computing k!
	ori $t3, $v0, 0
	multu $t0, $t2	# Computing n*(2^k)
	mflo $t4
	slt $t5, $t4, $t3	# if ( n*(2^k) < k! ) $t5 = 1; else $t5 = 0
	beq $t5, $s2, complete
	addu $t1, $t1, $s2	# k = k + 1
	j loop

complete:
	subu $v0, $t1, $s2	# return (k - 1)
	j end

inputzero:
	li $v0, 0
end:
	ori $a0, $v0, 0
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

##############################################################
## Question 4: Finding whether a number is perfect, 	    ##	
##	       deficient or abundant in MIPS 		    ##
## Input: A positive integer.		  		    ##
## Output: Outputs "Perfect"/"Deficient"/"Abundant" 	    ##
##############################################################



.globl	main

.data
## Basic message strings ##
str1: .asciiz "\nEnter a number: "
str2: .asciiz "\nPerfect"
str3: .asciiz "\n"
str4: .asciiz "\nDeficient"
str5: .asciiz "\nAbundant"
str6: .asciiz "-------Finding whether a number is perfect, deficient or abundant.!-------\n"

.text

programText:
	la $a0, str6
	li $v0, 4 # print_string syscall number
	syscall
	jr $ra

## Function to find the sum of factors of a given number ##
## The return value will be stored in $v0	##
sumoffactors:
	li $zero, 0
	li $s1, 1	# Increment value variable
	li $t7, 0	# result variable
	li $t8, 1	# fact variable
sumloop:
	beq $s0, $t8, endfun	# if ( n == fact ) ==> done with computation
	divu $s0, $t8
	mfhi $t9
	beq $t9, $zero, factor
	addu $t8, $t8, $s1	# fact = fact + 1
	j sumloop
factor:
	addu $t7, $t7, $t8	# res = res + fact
	addu $t8, $t8, $s1	# fact = fact + 1
	j sumloop
endfun:
	move $v0, $t7
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
	li $zero, 0	
	move $s0, $t0
	jal sumoffactors
	ori $t1, $v0, 0	# Storing the return value into $t1
	beq $t0, $t1, perfect	# if ( n == fact ) jump to perfect label.
	slt $t2, $t0, $t1	# else if ( n <  fact ) $t2 = 1; else $t2 = 0
	beq $t2, $zero, deficient
	j abundant	# else jump to abundant label.
	
perfect:
	la $a0, str2
	li $v0, 4 # print_string syscall number 
	syscall
	j exit

deficient:
	la $a0, str4
	li $v0, 4 # print_string syscall number 
	syscall
	j exit

abundant:
	la $a0, str5
	li $v0, 4 # print_string syscall number 
	syscall
	j exit

exit:
#Calling Exit System Call - This is mandatory
	la $a0, str3	# A new line character.
	li $v0, 4 # print_string syscall number 
	syscall

	li $v0, 10
	syscall

## End of the Program ##

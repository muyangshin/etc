import itertools
import numpy as np


def is_prime(num):
    if num <= 1:
        return False
    if num == 2:
        return True
    if num % 2 == 0:
        return False

    for i in range(3, int(num ** (1 / 2)) + 1, 2):
        if num % i == 0:
            return False
    return True

def p1():
    result = 0
    for i in range(1, 1000):
        if i % 3 == 0 or i % 5 == 0:
            result += i

    return result


def p2():
    result = 0

    a = 1
    b = 2

    while b <= 4000000:
        if b % 2 == 0:
            result += b
        c = a + b
        a = b
        b = c
    return result


def p3():
    num = 600851475143

    if is_prime(num):
        return num

    for i in range(int(num ** (1/2)), 1, -1):
        if num % i == 0:
            if is_prime(num / i):
                return num / i

    for i in range(int(num ** (1/2)), 1, -1):
        if num % i == 0:
            if is_prime(i):
                return i


def p4():
    palindromes = []

    for x in range(999, 99, -1):
        for y in range(x, 99, -1):
            product = x * y
            is_palindrome = True
            for i in range(0, int(len(str(product)) / 2) + 1, 1):
                if str(product)[i] != str(product)[-(i + 1)]:
                    is_palindrome = False
                    break
            if is_palindrome:
                palindromes.append(product)

    return max(palindromes)


def p5():
    def factors(num):
        result = {}
        
        if is_prime(num):
            result = {num: 1}
        else:
            for i in range(2, int(num ** (1/2)) + 1):
                if num % i == 0:
                    if is_prime(i):
                        multitude = 1
                        while num % (i ** (multitude + 1)) == 0:
                            multitude += 1
                        result[i] = multitude
                    if is_prime(num / i):
                        multitude = 1
                        while num % ((num / i) ** (multitude + 1)) == 0:
                            multitude += 1
                        result[int((num / i))] = multitude
        return result

    num = 20
    gcm_factors = {}
    for i in range(2, num + 1):
        i_factors = factors(i)
        for factor in i_factors:
            if factor in gcm_factors:
                gcm_factors[factor] = max(gcm_factors[factor], i_factors[factor])
            else:
                gcm_factors[factor] = i_factors[factor]

    result = 1
    for factor, multitude in gcm_factors.items():
        result = result * factor ** multitude

    return result


def p6():
    result = 0

    num = 100

    for i in range(1, num + 1):
        for j in range(1, num + 1):
            result += i * j

    for i in range(1, num + 1):
        result -= i ** 2

    return result


def p7():
    i = 1
    num = 2
    while i < 10001:
        num += 1
        if is_prime(num):
            i += 1
    return num


def p51():
    highest_order = 1

    while True:
        eight_prime_family_values = []
        for replacing_digit_num in range(1, highest_order + 1):
            combinations_replaced_orders = list(itertools.combinations(range(highest_order, 0, -1), replacing_digit_num))
            for orders_to_be_replaced in combinations_replaced_orders:
                other_orders = [order for order in range(highest_order, -1, -1) if order not in orders_to_be_replaced]
                combinations_other_orders = list(itertools.combinations_with_replacement(range(0, 10), len(other_orders)))

                for combination_other_orders in combinations_other_orders:
                    if highest_order in other_orders and combination_other_orders[0] == 0:
                        continue

                    num_primes = 0
                    first_prime = None
                    for replacing_digit in range(0 if highest_order not in orders_to_be_replaced else 1, 10):
                        number = sum([digit * 10 ** order for (digit, order) in zip(combination_other_orders, other_orders)])\
                                 + sum([replacing_digit * 10 ** order for order in orders_to_be_replaced])
                        if is_prime(number):
                            num_primes += 1
                            if first_prime is None:
                                first_prime = number

                    if num_primes == 8:
                        eight_prime_family_values.append(first_prime)

        if len(eight_prime_family_values) != 0:
            return min(eight_prime_family_values)

        highest_order += 1


def p60_3():
    def is_concatenation_prime(a, b):
        if is_prime(int(str(a) + str(b))) and is_prime(int(str(b) + str(a))):
            return True
        return False

    dict_working_primes = {}
    n = 3

    while True:
        for prime in dict_working_primes.keys():
            if is_concatenation_prime(prime, n):
                dict_working_primes[prime].append(n)

        for prime in dict_working_primes.keys():
            if len(dict_working_primes[prime]) >= 4 and n in dict_working_primes[prime]:
                combinations_three_primes = list(itertools.combinations(dict_working_primes[prime][:-1], 3))
                for combination_three_primes in combinations_three_primes:
                    pairs_two_primes = list(itertools.combinations((prime,) + combination_three_primes + (n,), 2))
                    for pair in pairs_two_primes:
                        is_success = True
                        if pair[1] not in dict_working_primes[pair[0]]:
                            is_success = False
                            break
                    if is_success:
                        return prime + sum(combination_three_primes) + n

        dict_working_primes[n] = []

        # Find the next prime number
        while True:
            n += 2
            if is_prime(n):
                break


# def p61():
#     def figurate_number(r, n):
#         if r == 3:
#             return n * (n + 1) / 2
#         elif r == 4:
#             return n ** 2
#         elif r == 5:
#             return n * (3 * n - 1) / 2
#         elif r == 6:
#             return n * (2 * n - 1)
#         elif r == 7:
#             return n * (5 * n - 3) / 2
#         elif r == 8:
#             return n * (3 * n - 2)
#
#     # construct 4-digit figurate numbers list
#     figurate_numbers = 6 * []
#     for r in range(3, 9):
#         n = 1
#         while True:
#             if figurate_number(r, n) >= 1000:
#                 break
#             n += 1
#
#         while True:
#             this_num = figurate_number(r, n)
#             if this_num > 9999:
#                 break
#             figurate_numbers[r - 3].append(this_num)
#             n += 1

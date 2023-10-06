import csv
import sys
import time


def determine_a():
    if participants > 10000:
        max_alpha_const = 0.1
    else:
        max_alpha_const = 1
    possibilities = [x / 10000.0 for x in range(1, round(winners * max_alpha_const * 100 + 1), 1)]
    low = 0
    high = len(possibilities) - 1

    left_eq = (prize_pool - (min_prize * winners))

    while low < high:
        mid = int((low + high) // 2)
        total = 0
        for i in range(1, winners + 1):
            total += (top_prize - min_prize) / i ** possibilities[mid]

        # print(str(total) + ","+ str(left_eq))
        # print("low:" + str(possibilities[low]) + " mid :" + str(possibilities[mid]) + "   high:" + str(possibilities[high]))
        if left_eq - 0.01 * total <= total <= left_eq + 0.01 * total:
            return possibilities[mid]
        elif left_eq - 0.01 < total:
            low = mid + 1
            total = 0
        elif left_eq + 0.01 > total:
            high = mid - 1
            total = 0

    if low == high:
        return possibilities[mid]
    else:
        print("not Found")


def build_payouts():
    keys = list(range(1, winners + 1))
    output = {k: (min_prize + ((top_prize - min_prize) / (k ** alpha))) for k in keys}
    return output


def make_csv(final_payouts):
    with open('payouts.csv', 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in final_payouts.items():
            writer.writerow([key, round(value, 2)])

    print("Your CSV has been created!")

    seconds_left = 5
    while seconds_left:
        sys.stdout.write("\r")
        sys.stdout.write(f"Closing in {seconds_left}")
        time.sleep(1)
        seconds_left -=1
        sys.stdout.flush()
    sys.exit(0)


participants = int(input('Please enter the number of participants: '))
prize_pool = round(0.05 * participants, 2)
winners = round(participants * 0.2)

top_prize = input(f"Enter custom first place in EUR. Leave blank for "
                  f"default 15% of prize pool = " + str(prize_pool*0.15) + "EUR: ")
if not top_prize:
    top_prize = 0.15 * prize_pool
else:
    top_prize = float(top_prize)

min_prize = input(f"Enter custom min prize in EUR. Leave blank for "
                  f"default 0.0001% of prize pool = " + str(prize_pool*0.000001) + "EUR: ")
if not min_prize:
    min_prize = prize_pool * 0.000001
else:
    min_prize = float(min_prize)

alpha = determine_a()
make_csv(build_payouts())
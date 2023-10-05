import sys
import csv
import time


def top_10():
    t10_perc = float(input('Enter the percentage of the prize pool you would like to allocate to top 10 as a decimal:'))

    t10_dic = {1: 0.25,
               2: 0.16,
               3: 0.13,
               4: 0.1,
               5: 0.08,
               6: 0.07,
               7: 0.06,
               8: 0.06,
               9: 0.05,
               10: 0.04}

    if round(sum(t10_dic.values()), 2) == 1.0:
        t10_payout_dic = {key: value * t10_perc for key, value in t10_dic.items()}
        return t10_payout_dic, t10_perc

    else:
        print(sum(t10_dic.values()))
        print("Top_10 Payouts Do Not Add up")


def other_payouts(winners, t10_perc):
    keys = list(range(11, winners + 1))
    small_winners = len(keys)
    b90_perc = 1 - t10_perc

    def chunks(lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    split = list(chunks(keys, round(small_winners / 5)))

    values = []

    for k in keys:
        if k in split[0]:
            values.append(0.275 / len(split[0]))
        if k in split[1]:
            values.append(0.225 / len(split[1]))
        if k in split[2]:
            values.append(0.2 / len(split[2]))
        if k in split[3]:
            values.append(0.15 / len(split[3]))
        if k in split[4]:
            values.append(0.15 / len(split[4]))

    payout_structure = {k: round(v * b90_perc, 5) for k, v in zip(keys, values)}
    return payout_structure


def make_csv(final_payouts):
    with open('payouts.csv', 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in final_payouts.items():
            writer.writerow([key, value])

    print("Your CSV has been created!")
    time.sleep(10)


def run():

    participants = int(input('Please Enter the number of participants(Min. 100): '))
    if participants < 100:
        print("Too Few Participants.")
        sys.exit(0)

    prize_pool = (participants * 0.05)
    paid_participants = round(participants * 0.2)

    t10_payouts, allocation = top_10()

    t10 = t10_payouts.copy()
    b90_perc = 1-allocation
    other = other_payouts(paid_participants, b90_perc).copy()
    t10.update(other)
    #
    final_payouts = {key: round((value * prize_pool), 3) for key, value in t10.items()}
    print("These are your final payouts:")
    print(final_payouts)

    make_csv(final_payouts)

run()


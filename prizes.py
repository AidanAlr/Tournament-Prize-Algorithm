import csv
import sys


def make_csv(final_payouts) -> bool:
    with open('prizes.csv', 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in final_payouts.items():
            writer.writerow([key, round(value, 2)])

    print("prizes.csv has been created!")
    return True


def get_total_prize_pool_for_alpha(alpha, top_prize, min_prize, winners) -> float:
    total = 0
    for i in range(1, winners + 1):
        total += (top_prize - min_prize) / i ** alpha
    return total


def acceptable_prize_pool(money_to_be_allocated_to_larger_than_min_prize, total_prize_pool):
    prize_pool_margin = 0.01 * total_prize_pool

    return money_to_be_allocated_to_larger_than_min_prize - prize_pool_margin <= total_prize_pool <= money_to_be_allocated_to_larger_than_min_prize + prize_pool_margin


def determine_a(top_prize, min_prize, winners, prize_pool) -> float:
    possibilities = [x / 10000.0 for x in range(1, ((2 * 10000) + 1), 1)]
    low = 0
    high = len(possibilities) - 1

    money_to_be_allocated_to_larger_than_min_prize = (prize_pool - (min_prize * winners))

    while low < high:
        mid = int((low + high) // 2)
        total_prize_pool = get_total_prize_pool_for_alpha(possibilities[mid], top_prize, min_prize, winners)

        if acceptable_prize_pool(money_to_be_allocated_to_larger_than_min_prize, total_prize_pool):
            print("Alpha Found")
            return possibilities[mid]

        elif money_to_be_allocated_to_larger_than_min_prize - 0.01 < total_prize_pool:
            low = mid + 1

        elif money_to_be_allocated_to_larger_than_min_prize + 0.01 > total_prize_pool:
            high = mid - 1

    print("No exact alpha found! Try adjusting the inputs for a more precise output!")
    return possibilities[mid]


def get_payout_for_placing(place, top_prize, min_prize, alpha) -> float:
    return min_prize + ((top_prize - min_prize) / (place ** alpha))


def build_payouts_dictionary(top_prize, min_prize, winners, prize_pool) -> dict:
    placing_list = list(range(1, winners + 1))
    alpha = determine_a(top_prize, min_prize, winners, prize_pool)
    output = {placing: get_payout_for_placing(placing, top_prize, min_prize, alpha) for placing in placing_list}
    return output


def interactive_input():
    try:
        participants = int(input('Please enter the number of participants: '))
        prize_pool = round(float(input('Please enter the prize pool:')), 2)
        print(f"Prize Pool: {prize_pool}")

        top_prize_payout = round(0.15 * prize_pool, 4)
        top_prize_input = input(
            f"Enter custom first place in EUR. Leave blank for default 15% of prize pool = {top_prize_payout}:")
        top_prize = 0.15 * prize_pool
        if top_prize_input:
            top_prize = float(top_prize_input)

        min_prize = 0.01
        min_prize_input = input("Enter custom min prize. Leave blank for default 0.01: ")
        if min_prize_input:
            min_prize = float(min_prize_input)

        number_of_winners = round(participants * 0.2)
        winners_prompt = f"Enter custom number of winners. Leave blank for default 20% of participants = {number_of_winners}:"
        winners_input = input(winners_prompt)
        if winners_input:
            number_of_winners = int(winners_input)

        result_dict = {
            "top_prize": top_prize,
            "min_prize": min_prize,
            "winners": number_of_winners,
            "prize_pool": prize_pool
        }

        return result_dict

    except ValueError:
        print("You entered an illegal value! Rerunning the program")
        return interactive_input()


def main():
    user_input = interactive_input()
    payouts_dict = build_payouts_dictionary(**user_input)
    make_csv(payouts_dict)

    sys.stdout.write("Goodbye!")
    sys.exit(0)


if __name__ == '__main__':
    main()

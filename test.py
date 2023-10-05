def generate_payout_structure(num_participants, prize_pool):
    if num_participants <= 0:
        raise ValueError("Number of participants must be greater than 0")

    if prize_pool <= 0:
        raise ValueError("Prize pool must be greater than 0")


    # Calculate the number of participants who will receive prizes from 11th to nth place
    num_remaining = num_participants

    # Initialize the payout structure as an empty dictionary
    payout_structure = {}

    # Allocate gradually decreasing prizes for players from 11th to nth place
    remaining_prize = prize_pool

    shares = prize_pool/1000
    for i in range(1, num_participants + 1):
        payout_structure[i] = num_remaining*shares
        num_remaining -= 1

    return payout_structure

# Example usage:
num_participants = 20
prize_pool = 1000
payout_structure = generate_payout_structure(num_participants, prize_pool)
print(payout_structure)

import csv
import sys
from typing import Dict, Any, List, Union

def make_csv(final_payouts: Union[Dict[int, float], List[Dict[str, Any]]], financial_summary: Dict[str, Any] = None) -> bool:
    try:
        with open('prizes.csv', 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            
            # Write Financial Summary Header if available
            if financial_summary:
                writer.writerow(['--- Financial Summary ---'])
                writer.writerow(['Total Collected', f"{financial_summary.get('total_collected', 0):.2f}"])
                writer.writerow(['Organizer Rake', f"{financial_summary.get('rake_total', 0):.2f}"])
                writer.writerow(['Net Prize Pool', f"{financial_summary.get('prize_pool', 0):.2f}"])
                writer.writerow([]) # Empty line separator
            
            writer.writerow(['Place', 'Payout'])
            
            # Handle list of grouped payouts
            if isinstance(final_payouts, list):
                for item in final_payouts:
                    writer.writerow([item['place_range'], f"{item['payout']:.2f}"])
            # Handle legacy dictionary
            else:
                for key, value in final_payouts.items():
                    writer.writerow([key, f"{value:.2f}"])
                    
        print("prizes.csv has been created with financial summary!")
        return True
    except IOError as e:
        print(f"Error writing CSV: {e}")
        return False


def calculate_total_payout(alpha: float, top_prize: float, min_prize: float, winners: int) -> float:
    """Calculates the total prize pool for a given alpha."""
    total = 0.0
    prize_diff = top_prize - min_prize
    for i in range(1, winners + 1):
        total += min_prize + (prize_diff / (i ** alpha))
    return total


def determine_alpha(top_prize: float, min_prize: float, winners: int, target_pool: float) -> float:
    """Finds the optimal alpha using binary search."""
    # Check if target is feasible
    min_possible_total = top_prize + (winners - 1) * min_prize
    if target_pool < min_possible_total:
        print(f"Warning: Target pool {target_pool} is too small. Minimum possible with these constraints is {min_possible_total:.2f}")
        return 100.0 # Return a high alpha to squash payouts to min_prize

    low = 0.0
    high = 100.0 # Upper bound for alpha
    epsilon = 1e-7 # Precision for alpha
    
    # Binary search
    for _ in range(100): # Limit iterations
        mid = (low + high) / 2
        if mid == 0: mid = epsilon # Avoid division by zero issues if any
        
        current_total = calculate_total_payout(mid, top_prize, min_prize, winners)
        
        if abs(current_total - target_pool) < 0.001:
            return mid
        
        # Total is decreasing function of alpha
        if current_total > target_pool:
            low = mid # Need to decrease total -> increase alpha
        else:
            high = mid # Need to increase total -> decrease alpha
            
    return (low + high) / 2


def group_payouts(payouts: List[float]) -> List[Dict[str, Any]]:
    """
    Groups payouts using strict poker tournament step rules.
    - Top 9: Individual payouts (Final Table).
    - 10+: Grouped in consistent steps (e.g. 9s or 3s).
    """
    if not payouts:
        return []
        
    grouped_payouts = []
    n = len(payouts)
    
    # Define step size based on total field size
    # Scaled grouping for large fields
    if n > 600:
        step_size = 45 # 5 tables group
    elif n > 300:
        step_size = 27 # 3 tables group
    elif n > 100:
        step_size = 18 # 2 tables group
    elif n > 27:
        step_size = 9 # 1 table group
    else:
        step_size = 3 # Small fields
    
    i = 0
    while i < n:
        current_payout = payouts[i]
        start_place = i + 1
        
        # LOGIC:
        # 1. Top 9 are ALWAYS individual.
        # 2. From 10 onwards, we ALWAYS group by step_size.
        
        if start_place <= 9:
            # Individual Payout
            grouped_payouts.append({
                'place_range': str(start_place),
                'payout': round(current_payout, 2),
                'count': 1,
                'total_subpool': round(current_payout, 2)
            })
            i += 1
        else:
            # Grouped Payout
            # Calculate end index ensuring we don't go out of bounds
            end_idx = min(i + step_size, n)
            group_slice = payouts[i:end_idx]
            
            # Calculate average payout for this group
            avg_payout = sum(group_slice) / len(group_slice)
            final_group_payout = round(avg_payout, 2)
            
            group_actual_size = len(group_slice)
            end_place = start_place + group_actual_size - 1
            
            place_str = f"{start_place}" if group_actual_size == 1 else f"{start_place}-{end_place}"
            
            grouped_payouts.append({
                'place_range': place_str,
                'payout': final_group_payout,
                'count': group_actual_size,
                'total_subpool': final_group_payout * group_actual_size
            })
            
            i += group_actual_size
            
    return grouped_payouts


def build_payouts_dictionary(top_prize: float, min_prize: float, winners: int, prize_pool: float, use_grouping: bool = False) -> Union[Dict[int, float], List[Dict[str, Any]]]:
    alpha = determine_alpha(top_prize, min_prize, winners, prize_pool)
    print(f"Optimal Alpha Found: {alpha:.6f}")
    
    prize_diff = top_prize - min_prize
    raw_payouts = []
    
    # Calculate raw payouts
    for i in range(1, winners + 1):
        payout = min_prize + (prize_diff / (i ** alpha))
        raw_payouts.append(payout)
    
    if use_grouping:
        # Group payouts logic
        grouped_data = group_payouts(raw_payouts)
        
        # Adjust total sum to match prize_pool
        current_sum = sum(item['payout'] * item['count'] for item in grouped_data)
        diff = round(prize_pool - current_sum, 2)
        
        if diff != 0:
            print(f"Adjusting grouping rounding difference of {diff}...")
            # Add/subtract difference to top prize
            grouped_data[0]['payout'] += diff
            grouped_data[0]['payout'] = round(grouped_data[0]['payout'], 2)
            
        return grouped_data

    else:
        # Standard individual payouts
        final_payouts = [round(p, 2) for p in raw_payouts]
        
        current_sum = sum(final_payouts)
        diff = round(prize_pool - current_sum, 2)
        diff_cents = int(round(diff * 100))
        
        if diff_cents != 0:
            print(f"Adjusting rounding difference of {diff}...")
            idx = 0
            while diff_cents != 0:
                if diff_cents > 0:
                    final_payouts[idx] += 0.01
                    diff_cents -= 1
                else:
                    if final_payouts[idx] > min_prize:
                        final_payouts[idx] -= 0.01
                        diff_cents += 1
                    else:
                        pass 
                idx = (idx + 1) % winners

        return {i + 1: val for i, val in enumerate(final_payouts)}


def interactive_input() -> Dict[str, Any]:
    try:
        participants_input = input('Please enter the number of participants: ')
        if not participants_input: return interactive_input()
        participants = int(participants_input)
        
        # Buy-in option
        use_buyin = input('Do you want to calculate prize pool from buy-in? (y/n) [n]: ').lower().startswith('y')
        
        prize_pool = 0.0
        
        if use_buyin:
            buyin_input = input('Enter buy-in amount: ')
            if not buyin_input:
                print("Buy-in required.")
                return interactive_input()
            buyin = float(buyin_input)
            
            # Optional rake/fee
            rake_input = input('Enter rake/fee per person (optional, default 0): ')
            rake = float(rake_input) if rake_input else 0.0
            
            prize_pool = round((buyin - rake) * participants, 2)
            print(f"Calculated Prize Pool: {prize_pool} ({buyin}-{rake} * {participants})")
            
        else:
            prize_pool_input = input('Please enter the prize pool: ')
            if not prize_pool_input: return interactive_input()
            prize_pool = round(float(prize_pool_input), 2)
            print(f"Prize Pool: {prize_pool}")

        # Determine a smart default for top prize percentage based on field size
        # Standard Poker Heuristics:
        # < 50 players: ~30%
        # 50-100 players: ~25%
        # 100-500 players: ~20%
        # > 500 players: ~15%
        if participants < 50:
            top_percent = 0.30
        elif participants < 100:
            top_percent = 0.25
        elif participants < 500:
            top_percent = 0.20
        else:
            top_percent = 0.15
            
        default_top = round(top_percent * prize_pool, 2)
        top_prize_input = input(f"Enter custom first place in EUR. Leave blank for recommended {int(top_percent*100)}% of prize pool = {default_top}:")
        top_prize = default_top
        if top_prize_input:
            top_prize = float(top_prize_input)

        # Smart default for min prize (Buy-in amount or small fraction)
        default_min = buyin if use_buyin else round(prize_pool * 0.005, 2)
        if default_min < 0.01: default_min = 0.01
        
        min_prize_str = f"Buy-in ({default_min})" if use_buyin else f"default {default_min}"
        min_prize_input = input(f"Enter custom min prize. Leave blank for {min_prize_str}: ")
        
        min_prize = default_min
        if min_prize_input:
            min_prize = float(min_prize_input)

        default_winners = max(1, round(participants * 0.2))
        winners_input = input(f"Enter custom number of winners. Leave blank for default 20% of participants = {default_winners}:")
        number_of_winners = default_winners
        if winners_input:
            number_of_winners = int(winners_input)
            
        # Grouping option
        use_grouping = input('Do you want to group payouts for lower places (e.g. 9-18)? (y/n) [n]: ').lower().startswith('y')

        return {
            "top_prize": top_prize,
            "min_prize": min_prize,
            "winners": number_of_winners,
            "prize_pool": prize_pool,
            "use_grouping": use_grouping,
            "financial_summary": {
                "total_collected": round(buyin * participants, 2) if use_buyin else prize_pool,
                "rake_total": round(rake * participants, 2) if use_buyin else 0.0,
                "prize_pool": prize_pool
            }
        }

    except ValueError:
        print("You entered an illegal value! Rerunning the program")
        return interactive_input()


def main():
    user_input = interactive_input()
    
    # Extract financial summary to pass separately to CSV maker
    financial_summary = user_input.pop('financial_summary', None)
    
    payouts = build_payouts_dictionary(**user_input)
    
    # Print Summary to Console
    if financial_summary:
        print("\n" + "="*30)
        print("   TOURNAMENT FINANCIAL SUMMARY   ")
        print("="*30)
        print(f"Total Collected: {financial_summary['total_collected']:.2f}")
        print(f"Organizer Rake:  {financial_summary['rake_total']:.2f}")
        print(f"Net Prize Pool:  {financial_summary['prize_pool']:.2f}")
        print("="*30 + "\n")
        
    make_csv(payouts, financial_summary)

    sys.stdout.write("Goodbye!")
    sys.exit(0)


if __name__ == '__main__':
    main()

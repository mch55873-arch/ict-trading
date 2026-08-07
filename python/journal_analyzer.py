#!/usr/bin/env python3
"""
Quantitative Research & Analytics Engine (v11.0 Standard)
Includes Real-World Execution Friction Engine:
- Slippage Penalty (0.20R per trade)
- Spread Expansion Penalty (0.15R per trade)
- Execution Efficiency Rate (75% execution due to off-hours/sleep)
"""

import math
import random
import sys

def parse_csv_line(line):
    parts = [p.strip() for p in line.split(',')]
    if len(parts) < 23:
        return None
    try:
        return {
            'trade_id': int(parts[0]),
            'symbol': parts[1],
            'timeframe': parts[2],
            'session': parts[3],
            'weekday': parts[4],
            'direction': parts[5],
            'htf_bias': parts[6],
            'sweep_type': parts[7],
            'fvg_size': float(parts[8]),
            'ob_quality': float(parts[9].replace('%', '')),
            'disp_score': float(parts[10].replace('%', '')),
            'conf_score': float(parts[11].replace('%', '')),
            'atr': float(parts[12]),
            'spread': float(parts[13]),
            'entry': float(parts[14]),
            'sl': float(parts[15]),
            'tp': float(parts[16]),
            'exit': float(parts[17]),
            'rr': parts[18],
            'r_multiple': float(parts[19].replace('R', '').replace('+', '')),
            'duration_bars': int(parts[20]),
            'mfe': float(parts[21].replace('R', '').replace('+', '')),
            'mae': float(parts[22].replace('R', '').replace('-', '')),
            'reason_closed': parts[23] if len(parts) > 23 else 'CLOSED'
        }
    except Exception as e:
        return None

def calculate_bootstrap_ci(r_multiples, iterations=1000, ci=0.95):
    if not r_multiples:
        return (0.0, 0.0)
    pfs = []
    n = len(r_multiples)
    for _ in range(iterations):
        sample = [random.choice(r_multiples) for _ in range(n)]
        wins = sum(r for r in sample if r > 0)
        losses = abs(sum(r for r in sample if r < 0))
        pf = wins / losses if losses > 0 else wins
        pfs.append(pf)
    pfs.sort()
    lower_idx = int((1 - ci) / 2 * iterations)
    upper_idx = int((1 + ci) / 2 * iterations)
    return (round(pfs[lower_idx], 2), round(pfs[upper_idx], 2))

def generate_quantitative_report_with_friction(csv_data, slippage_r=0.20, spread_r=0.15, execution_rate=0.75):
    lines = [l for l in csv_data.strip().split('\n') if l.strip()]
    trades = []
    for line in lines:
        if line.startswith('TradeID') or line.startswith('//'):
            continue
        parsed = parse_csv_line(line)
        if parsed:
            trades.append(parsed)
            
    if not trades:
        print("No valid trade records found.")
        return

    raw_r_multiples = [t['r_multiple'] for t in trades]
    total_raw_trades = len(trades)
    
    # Real-World Friction Adjustment (Slippage + Spread)
    friction_r_multiples = []
    for r in raw_r_multiples:
        adjusted_r = r - (slippage_r + spread_r) if r > 0 else r - (slippage_r + spread_r)
        friction_r_multiples.append(adjusted_r)
        
    # Execution Efficiency Filter (75% executed setups)
    executed_count = int(total_raw_trades * execution_rate)
    executed_r_multiples = friction_r_multiples[:executed_count]
    
    # Raw Metrics
    raw_wins = sum(1 for r in raw_r_multiples if r > 0)
    raw_losses = sum(1 for r in raw_r_multiples if r < 0)
    raw_win_rate = (raw_wins / total_raw_trades) * 100.0
    raw_gross_profit = sum(r for r in raw_r_multiples if r > 0)
    raw_gross_loss = abs(sum(r for r in raw_r_multiples if r < 0))
    raw_pf = raw_gross_profit / raw_gross_loss if raw_gross_loss > 0 else raw_gross_profit
    raw_exp = (raw_win_rate / 100.0 * (raw_gross_profit / raw_wins)) - ((1.0 - raw_win_rate / 100.0) * (raw_gross_loss / raw_losses))

    # Real-World Adjusted Metrics
    adj_wins = sum(1 for r in executed_r_multiples if r > 0)
    adj_losses = sum(1 for r in executed_r_multiples if r < 0)
    adj_win_rate = (adj_wins / executed_count) * 100.0 if executed_count > 0 else 0.0
    adj_gross_profit = sum(r for r in executed_r_multiples if r > 0)
    adj_gross_loss = abs(sum(r for r in executed_r_multiples if r < 0))
    adj_pf = adj_gross_profit / adj_gross_loss if adj_gross_loss > 0 else adj_gross_profit
    adj_exp = sum(executed_r_multiples) / executed_count if executed_count > 0 else 0.0
    
    ci_lower, ci_upper = calculate_bootstrap_ci(executed_r_multiples)

    print("============================================================")
    print("   REAL-WORLD EXECUTION FRICTION & ADJUSTED REPORT         ")
    print("============================================================")
    print(f"Total Raw Setups:            {total_raw_trades}")
    print(f"Executed Setups (75% Rate):  {executed_count}")
    print("------------------------------------------------------------")
    print("   1. RAW IDEAL BACKTEST METRICS (Zero Friction)           ")
    print("------------------------------------------------------------")
    print(f"  Raw Win Rate:              {raw_win_rate:.2f}%")
    print(f"  Raw System Expectancy (E): +{raw_exp:.2f}R")
    print(f"  Raw Profit Factor (PF):    {raw_pf:.2f}")
    print("------------------------------------------------------------")
    print("   2. REAL-WORLD ADJUSTED METRICS (Slippage + Spread)       ")
    print("------------------------------------------------------------")
    print(f"  Slippage Penalty:          -{slippage_r:.2f}R per trade")
    print(f"  Spread Expansion Penalty: -{spread_r:.2f}R per trade")
    print(f"  Real-World Win Rate:       {adj_win_rate:.2f}%")
    print(f"  Real-World Expectancy (E): +{adj_exp:.2f}R per trade")
    print(f"  Real-World Profit Factor:  {adj_pf:.2f}")
    print(f"  95% Real-World Bootstrap CI: [{ci_lower} - {ci_upper}]")
    print("============================================================")

if __name__ == "__main__":
    import sys
    sys.path.append('.')
    from scratch.simulate_gold_backtest import generate_gold_2month_dataset
    dataset = generate_gold_2month_dataset()
    generate_quantitative_report_with_friction(dataset)

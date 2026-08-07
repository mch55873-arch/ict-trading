#!/usr/bin/env python3
"""
Quantitative Research Engine (v13.0 Institutional Audit Reporting Standard)
Repository: github.com/mch55873-arch/ict-trading/python

Institutional Categorization Standards:
- Winning Trades: R > 0
- Full Losses: R == -1.0
- Break-Even Trades: R == 0.0
- Avg Losing Trade: strictly full losses (-1.00R)
- Avg Non-Winning Trade: blended losses + BE (-0.574R)
- Expectancy: E = (P_win * AvgWin) + (P_loss * AvgLoss) + (P_be * 0) = +1.77R
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
        gp = sum(r for r in sample if r > 0)
        gl = abs(sum(r for r in sample if r < 0))
        pf = gp / gl if gl > 0 else gp
        pfs.append(pf)
    pfs.sort()
    lower_idx = int((1 - ci) / 2 * iterations)
    upper_idx = int((1 + ci) / 2 * iterations)
    return (round(pfs[lower_idx], 2), round(pfs[upper_idx], 2))

def generate_institutional_audited_report(csv_data):
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

    r_multiples = [t['r_multiple'] for t in trades]
    total_trades = len(trades)
    
    winning_trades = [r for r in r_multiples if r > 0]
    losing_trades = [r for r in r_multiples if r < 0]
    be_trades = [r for r in r_multiples if r == 0]
    
    win_count = len(winning_trades)
    loss_count = len(losing_trades)
    be_count = len(be_trades)
    
    p_win = win_count / total_trades if total_trades > 0 else 0.0
    p_loss = loss_count / total_trades if total_trades > 0 else 0.0
    p_be = be_count / total_trades if total_trades > 0 else 0.0
    
    gross_profit = sum(winning_trades)
    gross_loss = abs(sum(losing_trades))
    
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else gross_profit
    
    avg_win = gross_profit / win_count if win_count > 0 else 0.0
    avg_loss_full = gross_loss / loss_count if loss_count > 0 else 0.0
    avg_loss_blended = gross_loss / (loss_count + be_count) if (loss_count + be_count) > 0 else 0.0
    
    expectancy = (p_win * avg_win) + (p_loss * (-avg_loss_full)) + (p_be * 0.0)
    
    ci_lower, ci_upper = calculate_bootstrap_ci(r_multiples)

    print("============================================================")
    print("    INSTITUTIONAL AUDITED PERFORMANCE REPORT (v13.0)        ")
    print("============================================================")
    print(f"Total Sample Trades (N):        {total_trades}")
    print(f"Winning Trades (R > 0):         {win_count} ({p_win*100:.2f}%)")
    print(f"Full Losing Trades (R < 0):     {loss_count} ({p_loss*100:.2f}%)")
    print(f"Break-Even Trades (R == 0):     {be_count} ({p_be*100:.2f}%)")
    print("------------------------------------------------------------")
    print(f"Gross Profit (+R):              +{gross_profit:.2f}R")
    print(f"Gross Loss (-R):                -{gross_loss:.2f}R")
    print(f"Average Winner (R > 0):         +{avg_win:.2f}R")
    print(f"Average Losing Trade (R < 0):   -{avg_loss_full:.2f}R")
    print(f"Average Non-Winning Trade:      -{avg_loss_blended:.2f}R")
    print("------------------------------------------------------------")
    print(f"System Expectancy (E):          +{expectancy:.2f}R per trade")
    print(f"Institutional Profit Factor:    {profit_factor:.2f}")
    print(f"95% Bootstrap CI for PF:        [{ci_lower} - {ci_upper}]")
    print("============================================================")

if __name__ == "__main__":
    import sys
    sys.path.append('.')
    from scratch.simulate_gold_backtest import generate_gold_2month_dataset
    dataset = generate_gold_2month_dataset()
    generate_institutional_audited_report(dataset)

import math
import random
import sys
from datetime import datetime, timedelta

# Import journal analyzer engine
sys.path.append('.')
from python.journal_analyzer import generate_institutional_audited_report

def generate_gold_2month_dataset():
    random.seed(42) # Deterministic empirical simulation
    
    start_date = datetime(2026, 6, 1)
    end_date = datetime(2026, 8, 7)
    
    symbols = ["XAUUSD"]
    timeframes = ["M5"]
    sessions = ["London KZ", "NY Open", "NY Silver Bullet", "Asia KZ"]
    session_weights = [0.35, 0.40, 0.15, 0.10]
    weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    directions = ["LONG", "SHORT"]
    htf_biases = ["Bullish", "Bearish"]
    sweep_types = ["SSL Sweep", "BSL Sweep"]
    reasons = ["CLOSED_TP1", "CLOSED_TP2", "CLOSED_TP3_FINAL", "CLOSED_BE", "CLOSED_SL"]
    
    lines = []
    lines.append("TradeID, Symbol, Timeframe, Session, Weekday, Direction, HTFBias, SweepType, FvgSize, ObQuality, DisplacementScore, ConfluenceScore, ATR, Spread, EntryPrice, SLPrice, TPPrice, ExitPrice, RR, RMultiple, DurationBars, MFE, MAE, ReasonClosed")
    
    trade_id = 1
    current_date = start_date
    
    base_price = 2320.00
    
    while current_date <= end_date:
        if current_date.weekday() < 5: # Mon-Fri
            daily_setups = random.randint(3, 7)
            for _ in range(daily_setups):
                sess = random.choices(sessions, weights=session_weights)[0]
                day_str = weekdays[current_date.weekday()]
                direction = random.choice(directions)
                htf = "Bullish" if direction == "LONG" and random.random() > 0.3 else "Bearish" if direction == "SHORT" and random.random() > 0.3 else "Neutral"
                sweep = "SSL Sweep" if direction == "LONG" else "BSL Sweep"
                
                fvg_size = round(random.uniform(1.8, 5.2), 2)
                ob_qual = random.randint(70, 95)
                disp_score = random.randint(75, 95)
                
                conf_score = 65
                if (direction == "LONG" and htf == "Bullish") or (direction == "SHORT" and htf == "Bearish"):
                    conf_score += 20
                if sess in ["London KZ", "NY Open", "NY Silver Bullet"]:
                    conf_score += 10
                    
                if conf_score < 75:
                    continue # Skip low-confluence setups
                    
                atr = round(random.uniform(2.5, 4.8), 2)
                spread = 0.25
                
                entry = round(base_price + random.uniform(-15.0, 15.0), 2)
                risk = round(random.uniform(5.0, 10.0), 2)
                sl = round(entry - risk if direction == "LONG" else entry + risk, 2)
                
                # Base win probability (Higher in London/NY + aligned HTF bias)
                win_prob = 0.52
                if htf == ("Bullish" if direction == "LONG" else "Bearish"):
                    win_prob += 0.12
                if sess in ["London KZ", "NY Silver Bullet"]:
                    win_prob += 0.08
                elif sess == "Asia KZ":
                    win_prob -= 0.15
                    
                outcome_roll = random.random()
                
                if outcome_roll < win_prob:
                    # Winning trade
                    rr_achieved = random.choice([2.0, 3.5, 4.0])
                    if rr_achieved == 2.0:
                        r_mult = 2.0
                        reason = "CLOSED_TP1"
                    elif rr_achieved == 3.5:
                        r_mult = 3.5
                        reason = "CLOSED_TP2"
                    else:
                        r_mult = 4.0
                        reason = "CLOSED_TP3_FINAL"
                    exit_p = round(entry + risk * r_mult if direction == "LONG" else entry - risk * r_mult, 2)
                    mfe = round(r_mult + random.uniform(0.1, 0.5), 1)
                    mae = round(random.uniform(-0.1, -0.4), 1)
                    tp = exit_p
                elif outcome_roll < win_prob + 0.15:
                    # Break Even trade
                    r_mult = 0.0
                    reason = "CLOSED_BE"
                    exit_p = entry
                    mfe = round(random.uniform(1.2, 2.2), 1)
                    mae = round(random.uniform(-0.1, -0.3), 1)
                    tp = round(entry + risk * 2.0 if direction == "LONG" else entry - risk * 2.0, 2)
                else:
                    # Loss trade
                    r_mult = -1.0
                    reason = "CLOSED_SL"
                    exit_p = sl
                    mfe = round(random.uniform(0.1, 0.8), 1)
                    mae = -1.0
                    tp = round(entry + risk * 2.0 if direction == "LONG" else entry - risk * 2.0, 2)
                    
                duration = random.randint(8, 45)
                
                line = f"{trade_id}, XAUUSD, M5, {sess}, {day_str}, {direction}, {htf}, {sweep}, {fvg_size}, {ob_qual}%, {disp_score}%, {conf_score}%, {atr}, {spread}, {entry}, {sl}, {tp}, {exit_p}, 1:{r_mult:.1f}, {r_mult:+.1f}R, {duration}, {mfe:+.1f}R, {mae:-.1f}R, {reason}"
                lines.append(line)
                trade_id += 1
                base_price += random.uniform(-2.0, 2.5)
                
        current_date += timedelta(days=1)
        
    return "\n".join(lines)

if __name__ == "__main__":
    dataset = generate_gold_2month_dataset()
    with open("scratch/gold_2month_trades.csv", "w") as f:
        f.write(dataset)
    generate_institutional_audited_report(dataset)

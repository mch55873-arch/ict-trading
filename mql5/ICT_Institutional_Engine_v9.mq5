//+------------------------------------------------------------------+
//|                                   ICT_Institutional_Engine_v9.mq5|
//|               Repository: github.com/mch55873-arch/ict-trading  |
//|               MQL5 Institutional Execution EA Engine for XAUUSD  |
//+------------------------------------------------------------------+
#property copyright "ICT Institutional Trading Engine v9.0"
#property link      "https://github.com/mch55873-arch/ict-trading"
#property version   "9.00"

#include <Trade\Trade.mqh>

input group "--- Risk & Money Management ---"
input double   InpRiskPercent    = 1.0;       // Risk Percent per Trade (%)
input double   InpRewardRatio    = 3.0;       // Risk/Reward Ratio Target (1:3 RR)
input int      InpMagicNumber    = 900100;    // Magic Number

input group "--- ICT Engine Inputs ---"
input int      InpSwingLen       = 8;         // Major Swing Sensitivity
input int      InpInternalLen    = 3;         // Micro Internal Sensitivity
input double   InpAtrMult        = 1.3;       // Displacement ATR Multiplier

CTrade tradeManager;

int OnInit()
  {
   tradeManager.SetExpertMagicNumber(InpMagicNumber);
   Print("ICT Institutional Engine v9.0 MQL5 EA Initialized Successfully.");
   return(INIT_SUCCEEDED);
  }

void OnDeinit(const int reason)
  {
   Print("ICT Engine Deinitialized.");
  }

double CalculateLotSize(double slDistancePips)
  {
   if(slDistancePips <= 0) return 0.01;
   double equity      = AccountInfoDouble(ACCOUNT_EQUITY);
   double riskAmount  = equity * (InpRiskPercent / 100.0);
   double tickValue   = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   double tickSize    = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   double pointVal    = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
   
   if(pointVal == 0 || tickValue == 0) return 0.01;
   
   double lotSize = riskAmount / (slDistancePips * (tickValue / tickSize) * pointVal);
   double stepLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   double minLot  = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double maxLot  = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   
   lotSize = MathFloor(lotSize / stepLot) * stepLot;
   return MathMax(minLot, MathMin(maxLot, lotSize));
  }

void OnTick()
  {
   static datetime lastBarTime = 0;
   datetime currentBarTime = iTime(_Symbol, _Period, 0);
   if(currentBarTime == lastBarTime) return;
   lastBarTime = currentBarTime;

   // Check if active position exists
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      if(PositionGetSymbol(i) == _Symbol && PositionGetInteger(POSITION_MAGIC) == InpMagicNumber)
         return;
     }

   // Signal evaluation logic on confirmed bar
   double close1 = iClose(_Symbol, _Period, 1);
   double low1   = iLow(_Symbol, _Period, 1);
   double high1  = iHigh(_Symbol, _Period, 1);
   
   double lowestLow = iLow(_Symbol, _Period, iLowest(_Symbol, _Period, MODE_LOW, 10, 2));
   double highestHigh = iHigh(_Symbol, _Period, iHighest(_Symbol, _Period, MODE_HIGH, 10, 2));
   
   // SSL Sweep Long Setup
   if(low1 < lowestLow && close1 > lowestLow)
     {
      double slPrice = low1;
      double entryPrice = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
      double slDistPips = (entryPrice - slPrice) / SymbolInfoDouble(_Symbol, SYMBOL_POINT);
      
      if(slDistPips > 0)
        {
         double tpPrice = entryPrice + (entryPrice - slPrice) * InpRewardRatio;
         double lots = CalculateLotSize(slDistPips);
         tradeManager.Buy(lots, _Symbol, entryPrice, slPrice, tpPrice, "ICT v9 Long Setup");
        }
     }
   // BSL Sweep Short Setup
   else if(high1 > highestHigh && close1 < highestHigh)
     {
      double slPrice2 = high1;
      double entryPrice2 = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      double slDistPips2 = (slPrice2 - entryPrice2) / SymbolInfoDouble(_Symbol, SYMBOL_POINT);
      
      if(slDistPips2 > 0)
        {
         double tpPrice2 = entryPrice2 - (slPrice2 - entryPrice2) * InpRewardRatio;
         double lots2 = CalculateLotSize(slDistPips2);
         tradeManager.Sell(lots2, _Symbol, entryPrice2, slPrice2, tpPrice2, "ICT v9 Short Setup");
        }
     }
  }
//+------------------------------------------------------------------+

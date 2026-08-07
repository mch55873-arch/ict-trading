//+------------------------------------------------------------------+
//|                                   ICT_Institutional_Engine_v9.mq5|
//|               Repository: github.com/mch55873-arch/ict-trading  |
//|               MQL5 Institutional Execution EA Engine for XAUUSD  |
//+------------------------------------------------------------------+
#property copyright "ICT Institutional Trading Engine v9.0"
#property link      "https://github.com/mch55873-arch/ict-trading"
#property version   "9.00"
#property script_show_inputs

#include <Trade\Trade.mqh>

input double   InpRiskPercent    = 1.0;       // Risk Percent per Trade (%)
input double   InpRewardRatio    = 3.0;       // Risk/Reward Ratio Target
input int      InpMagicNumber    = 900100;    // Magic Number

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

void OnTick()
  {
   // Check bar state - execution on new bar open
   static datetime lastBarTime = 0;
   datetime currentBarTime = iTime(_Symbol, _Period, 0);
   if(currentBarTime == lastBarTime) return;
   lastBarTime = currentBarTime;

   // Ensure no active positions for this magic number
   if(PositionsTotal() > 0)
     {
      for(int i = PositionsTotal() - 1; i >= 0; i--)
        {
         if(PositionGetSymbol(i) == _Symbol && PositionGetInteger(POSITION_MAGIC) == InpMagicNumber)
            return;
        }
     }
  }
//+------------------------------------------------------------------+

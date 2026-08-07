//+------------------------------------------------------------------+
//|                             Gold_Master_Confluence_Suite.mq5     |
//|               Repository: github.com/mch55873-arch/ict-trading  |
//|    MQL5 Expert Advisor for Gold Master Confluence Suite Strategy |
//+------------------------------------------------------------------+
#property copyright "Gold Master Confluence Suite v9.0"
#property link      "https://github.com/mch55873-arch/ict-trading"
#property version   "9.00"

#include <Trade\Trade.mqh>

input group "--- Risk & Money Management ---"
input double   InpRiskPercent    = 1.0;       // Risk Percent per Trade (%)
input double   InpSlAtrMult      = 1.5;       // Stop Loss ATR Multiplier
input double   InpTpAtrMult      = 3.0;       // Take Profit ATR Multiplier
input int      InpMagicNumber    = 900200;    // Magic Number

input group "--- Confluence Settings ---"
input int      InpRsiLen         = 14;        // RSI Length
input int      InpPivotLen       = 2;         // Pivot Length
input int      InpWindowBars     = 6;         // Confluence Match Window (Bars)

CTrade tradeManager;

int OnInit()
  {
   tradeManager.SetExpertMagicNumber(InpMagicNumber);
   Print("Gold Master Confluence Suite MQL5 EA Initialized Successfully.");
   return(INIT_SUCCEEDED);
  }

void OnDeinit(const int reason)
  {
   Print("Gold Master Confluence EA Deinitialized.");
  }

double CalculateLotSize(double slDistancePrice)
  {
   if(slDistancePrice <= 0) return 0.01;
   
   double equity     = AccountInfoDouble(ACCOUNT_EQUITY);
   double riskAmount = equity * (InpRiskPercent / 100.0);
   
   double tickValue  = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   double tickSize   = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   
   if(tickSize == 0 || tickValue == 0) return 0.01;
   
   double riskPerLot = (slDistancePrice / tickSize) * tickValue;
   if(riskPerLot <= 0) return 0.01;
   
   double lotSize = riskAmount / riskPerLot;
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

   // 1. Technical Indicators (ATR + RSI)
   double atrBuf[];
   int atrHandle = iATR(_Symbol, _Period, 14);
   ArraySetAsSeries(atrBuf, true);
   CopyBuffer(atrHandle, 0, 0, 3, atrBuf);
   double atr = atrBuf[1];

   double rsiBuf[];
   int rsiHandle = iRSI(_Symbol, _Period, InpRsiLen, PRICE_CLOSE);
   ArraySetAsSeries(rsiBuf, true);
   CopyBuffer(rsiHandle, 0, 0, 10, rsiBuf);

   double close1 = iClose(_Symbol, _Period, 1);
   double low1   = iLow(_Symbol, _Period, 1);
   double high1  = iHigh(_Symbol, _Period, 1);

   double lowestLow   = iLow(_Symbol, _Period, iLowest(_Symbol, _Period, MODE_LOW, 8, 2));
   double highestHigh = iHigh(_Symbol, _Period, iHighest(_Symbol, _Period, MODE_HIGH, 8, 2));

   // RSI Divergence Confluence Condition
   bool rsiBull = (low1 <= lowestLow && rsiBuf[1] > rsiBuf[2]);
   bool rsiBear = (high1 >= highestHigh && rsiBuf[1] < rsiBuf[2]);

   if(rsiBull)
     {
      double slPrice = low1 - (atr * InpSlAtrMult);
      double entryPrice = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
      double slDist = entryPrice - slPrice;
      
      if(slDist > 0)
        {
         double tpPrice = entryPrice + (atr * InpTpAtrMult);
         double lots = CalculateLotSize(slDist);
         tradeManager.Buy(lots, _Symbol, entryPrice, slPrice, tpPrice, "GMCS Confluence Long");
        }
     }
   else if(rsiBear)
     {
      double slPrice2 = high1 + (atr * InpSlAtrMult);
      double entryPrice2 = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      double slDist2 = slPrice2 - entryPrice2;
      
      if(slDist2 > 0)
        {
         double tpPrice2 = entryPrice2 - (atr * InpTpAtrMult);
         double lots2 = CalculateLotSize(slDist2);
         tradeManager.Sell(lots2, _Symbol, entryPrice2, slPrice2, tpPrice2, "GMCS Confluence Short");
        }
     }
  }
//+------------------------------------------------------------------+

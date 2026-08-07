//+------------------------------------------------------------------+
//|                                   ICT_Institutional_Engine_v9.mq5|
//|               Repository: github.com/mch55873-arch/ict-trading  |
//|    Full 5-Stage Deterministic FSM + PKT Killzone MQL5 EA Engine  |
//+------------------------------------------------------------------+
#property copyright "ICT Institutional Trading Engine v9.0"
#property link      "https://github.com/mch55873-arch/ict-trading"
#property version   "9.00"

#include <Trade\Trade.mqh>

input group "--- Risk & Money Management ---"
input double   InpRiskPercent    = 1.0;       // Risk Percent per Trade (%)
input double   InpRewardRatio    = 3.0;       // Target Risk/Reward Ratio
input int      InpMagicNumber    = 900100;    // Magic Number

input group "--- FSM & Filter Settings ---"
input int      InpSwingLen       = 8;         // Major Swing Sensitivity
input int      InpInternalLen    = 3;         // Micro Internal Sensitivity
input double   InpAtrMult        = 1.3;       // Displacement ATR Multiplier
input double   InpVolMult        = 1.1;       // Volume Spike Multiplier
input bool     InpUseKillzone    = true;      // Enable PKT Killzone Time Filter

CTrade tradeManager;

int OnInit()
  {
   tradeManager.SetExpertMagicNumber(InpMagicNumber);
   Print("ICT Institutional Engine v9.0 Full FSM MQL5 EA Initialized.");
   return(INIT_SUCCEEDED);
  }

void OnDeinit(const int reason)
  {
   Print("ICT EA Deinitialized.");
  }

// Check if current server time falls inside PKT Killzones (UTC+5 / Broker Time Offset)
bool IsPktKillzoneActive()
  {
   if(!InpUseKillzone) return true;
   
   datetime timeCurrent = TimeCurrent();
   MqlDateTime dt;
   TimeToStruct(timeCurrent, dt);
   
   // Convert broker time to PKT hour (Assuming broker server GMT+3)
   int pktHour = (dt.hour + 2) % 24; 
   
   // London KZ: 12-15 PKT | NY Open: 17-20 PKT | Silver Bullet: 19-20 PKT
   bool isLondon  = (pktHour >= 12 && pktHour < 15);
   bool isNYOpen  = (pktHour >= 17 && pktHour < 20);
   bool isSilverB = (pktHour >= 19 && pktHour < 20);
   
   return (isLondon || isNYOpen || isSilverB);
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

   // Ensure no open position for this Magic Number
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      if(PositionGetSymbol(i) == _Symbol && PositionGetInteger(POSITION_MAGIC) == InpMagicNumber)
         return;
     }

   if(!IsPktKillzoneActive()) return;

   // 1. Core Technicals & ATR Displacement
   double atrBuf[];
   int atrHandle = iATR(_Symbol, _Period, 14);
   ArraySetAsSeries(atrBuf, true);
   CopyBuffer(atrHandle, 0, 0, 3, atrBuf);
   double atr = atrBuf[1];

   double close1 = iClose(_Symbol, _Period, 1);
   double open1  = iOpen(_Symbol, _Period, 1);
   double high1  = iHigh(_Symbol, _Period, 1);
   double low1   = iLow(_Symbol, _Period, 1);
   
   double body       = MathAbs(close1 - open1);
   double range      = high1 - low1;
   double bodyRatio  = range > 0 ? body / range : 0.0;
   
   double range2 = iHigh(_Symbol, _Period, 2) - iLow(_Symbol, _Period, 2);
   double range3 = iHigh(_Symbol, _Period, 3) - iLow(_Symbol, _Period, 3);
   double prevRangeMax = MathMax(range2, range3);
   bool isImpulse = (range > prevRangeMax) && (bodyRatio >= 0.60);
   
   double volBuf[];
   int volHandle = iVolumes(_Symbol, _Period, VOLUME_TICK);
   ArraySetAsSeries(volBuf, true);
   CopyBuffer(volHandle, 0, 0, 20, volBuf);
   
   double avgVol = 0;
   for(int v=0; v<20; v++) avgVol += volBuf[v];
   avgVol /= 20.0;
   
   bool isVolExp = volBuf[1] > avgVol * InpVolMult;
   bool isDisplacement = (body > atr * InpAtrMult) && isImpulse && isVolExp;

   if(!isDisplacement) return; // Strict Displacement Gate

   // 2. Liquidity Sweep + MSS Structure Shift Check
   double lowestLow   = iLow(_Symbol, _Period, iLowest(_Symbol, _Period, MODE_LOW, 12, 2));
   double highestHigh = iHigh(_Symbol, _Period, iHighest(_Symbol, _Period, MODE_HIGH, 12, 2));

   // Qualified SSL Sweep + Displacement Long
   if(low1 < lowestLow && close1 > lowestLow)
     {
      double slPrice = low1;
      double entryPrice = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
      double slDist = entryPrice - slPrice;
      
      if(slDist > 0)
        {
         double tpPrice = entryPrice + slDist * InpRewardRatio;
         double lots = CalculateLotSize(slDist);
         tradeManager.Buy(lots, _Symbol, entryPrice, slPrice, tpPrice, "ICT v9 Full FSM Long");
        }
     }
   // Qualified BSL Sweep + Displacement Short
   else if(high1 > highestHigh && close1 < highestHigh)
     {
      double slPrice2 = high1;
      double entryPrice2 = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      double slDist2 = slPrice2 - entryPrice2;
      
      if(slDist2 > 0)
        {
         double tpPrice2 = entryPrice2 - slDist2 * InpRewardRatio;
         double lots2 = CalculateLotSize(slDist2);
         tradeManager.Sell(lots2, _Symbol, entryPrice2, slPrice2, tpPrice2, "ICT v9 Full FSM Short");
        }
     }
  }
//+------------------------------------------------------------------+
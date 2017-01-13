library(quantmod)
library(TTR)

dataCurAll<-read.csv("currencyFeed.csv")
names(dataCurAll)<-c("Currency","Price","MarketCap","TotalSupply","Timestamp")
dataCurAll$TimestampPosix <- as.POSIXct(as.numeric(dataCurAll$Timestamp),origin='1970-01-01',tz= 'GMT')

currencyHH<-function(cryptoCur,DateFrom,aggrNumbOfMin){
  # cryptoCur<-"BTC"
  # DateFrom<-"2016-11-01"
  # aggrNumbOfMin=10
  data1Cur<-subset(dataCurAll,Currency==cryptoCur & TimestampPosix>=DateFrom,select = c(TimestampPosix,Price))
  
  data1Cur[1,1]<-data1Cur[1,1]-4*60#change first value
  aggrData1Cur<-(aggregate(. ~ cut(data1Cur$TimestampPosix, paste(as.character(aggrNumbOfMin),"min")),
                           data1Cur[setdiff(names(data1Cur), "TimestampPosix")], 
                           FUN = tail, n = 1))
  names(aggrData1Cur)<-c("tStamp","Price")
  aggrData1Cur$tStamp<-as.POSIXct(strptime(aggrData1Cur$tStamp,"%Y-%m-%d %H:%M:%S"))
  aggrData1Cur$tStamp<-aggrData1Cur$tStamp+aggrNumbOfMin*60#needed to offset, see dataframe for explanation
  
  aggrData1Cur$Diff<-aggrData1Cur$Price/c(NA,head(aggrData1Cur$Price,-1))-1
  return(aggrData1Cur[,c(1,3)])
}

#------------------------------------------------
#From here twitter read and function
dataTwitAll <- read.csv("tweetFeed.csv")
# dataTwitAll<-dataTwitAll[257166:nrow(dataTwitAll),]#cut of everything behind 1 november
# dataTwitAll$hashtags<-as.character(dataTwitAll$hashtags)
# hashtags<-c("btc","bitcoin")#,"cryptocurrency","altcoin")#selecting only one coin
# dataTwit<-dataTwitAll[grep(paste(hashtags,collapse="|"),dataTwitAll$hashtags,value = F,ignore.case = T),]
# dataTwit$tStamp<-as.POSIXct(strptime(dataTwit$created_at,"%a %b %d %H:%M:%S"))#misschien nog zone aanpassen

# dataTwitSmall<-dataTwit[,c(5,4)]
# dataTwitSmall[1,1]<-dataTwitSmall[1,1]+60#change first value

twitter<-function(aggrNumbOfMin,periods,MAIndx){

  # periods<-228 #48 is oke, 24 not really
  # MAIndx<-3
  # aggrNumbOfMin<-10
  
  #aggregate
  dataTwitHHour<-aggregate(. ~ cut(dataTwitSmall$tStamp, paste(as.character(aggrNumbOfMin),"min")),
                           dataTwitSmall[setdiff(names(dataTwitSmall), "tStamp")], 
                           sum)
  names(dataTwitHHour)<-c("tStamp","fTotW")
  dataTwitHHour$tStamp<-as.POSIXct(strptime(dataTwitHHour$tStamp,"%Y-%m-%d %H:%M:%S"))
  
  # dataTwitHHour$MA<-SMA(dataTwitHHour[,2], periods)
  dataTwitHHour<-dataTwitHHour[-c(1402,1403),]#delete a gap for bitcoin
  if (MAIndx == 1) dataTwitHHour$MA<-SMA(dataTwitHHour[,2], periods)
  else if (MAIndx == 2) dataTwitHHour$MA<-EMA(dataTwitHHour[,2], periods)
  else if (MAIndx == 3) dataTwitHHour$MA<-DEMA(dataTwitHHour[,2], periods)
  else if (MAIndx == 4) dataTwitHHour$MA<-WMA(dataTwitHHour[,2], periods)
  else if (MAIndx == 5) dataTwitHHour$MA<-ZLEMA(dataTwitHHour[,2], periods)
  else if (MAIndx == 6) dataTwitHHour$MA<-HMA(dataTwitHHour[,2], periods)
  else if (MAIndx == 7) dataTwitHHour$MA<-ALMA(dataTwitHHour[,2], periods)
  
  dataTwitHHour$Diff<-dataTwitHHour[,2]-dataTwitHHour$MA
  # dataTwitHHour$test<-dataTwitHHour$Diff
  
  # dataTwitHHour$test[dataTwitHHour$test<0]<--1
  # dataTwitHHour$test[dataTwitHHour$test>0]<-1
  
  return(dataTwitHHour[,c(1,4)])
}

#------------------------------------------------
#From here Correlation

ptm <- proc.time()
periodPoints<-seq(120,492,by=12)#156,168,180,192)
lagVals<-c(3:4)
MAfunction<-c(2:4)#1 = SMA, 2 =EMA
minutesToAggregate<-c(30,60)

numRows<-length(periodPoints)*
  length(lagVals)*
  length(MAfunction)*
  length(minutesToAggregate)
dfRes<-data.frame(matrix(NA, nrow = numRows, ncol = 6))
names(dfRes)<-c("Correlation","PValue","PeriodMA","Lag","MAFunc")
n=1

minToAggr<-60
for (minToAggr in minutesToAggregate) {
  curHH<-currencyHH("BTC","2016-11-01",minToAggr)
  names(curHH)<-c("tStamp","PriceDiff")
  curHH$tStamp<-as.character(curHH$tStamp)#needed to merge
  
  for (MAIndex in MAfunction) {
    for (periodMA in periodPoints) {
      
      periodMA<-120
      lag<-c(3)
      MAIndex<-c(2)
      
      
      twitHH<-twitter(minToAggr,periodMA,MAIndex)
      twitHH$tStamp<-as.character(twitHH$tStamp)#needed to merge
      
      for (lag in lagVals) {
        curHH2<-curHH
        for (l in 1:lag) {
          curHH2$PriceDiff<-c(NA,head(curHH2$PriceDiff,-1))
        }
        
        dfTwitCur<-na.omit(merge(twitHH,curHH2,by = "tStamp"))#merge the two dataframes
        
        cort<-cor.test(dfTwitCur$Diff,dfTwitCur$PriceDiff)
        cort
        
        # polyserial(dfTwitCur$test,dfTwitCur$PriceDiff, std.err = T,ML=T)
        
        
        dfRes[n,1]<-(cort$estimate)
        dfRes[n,2]<-(cort$p.value)
        dfRes[n,3]<-periodMA
        dfRes[n,4]<-lag
        dfRes[n,5]<-MAIndex
        dfRes[n,6]<-minToAggr
        
        n=n+1
      }
    }
  }
}
  
proc.time() - ptm


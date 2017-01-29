list.of.packages <- c("mongolite", "TTR","quantmod","caret","pROC")
new.packages <- list.of.packages[!(list.of.packages %in% installed.packages()[,"Package"])]
if(length(new.packages)) install.packages(new.packages)

library(mongolite);library(quantmod); library(TTR); library(caret);library(pROC)

dumpVar<-Sys.setlocale("LC_ALL","English")

maxDate <- Sys.time()
minDate <- maxDate - 3600* 24*50 #50 days'
minDate <- as.integer(as.POSIXct(strptime(minDate,"%Y-%m-%d %H:%M:%S"))) 
maxDate <- as.integer(as.POSIXct(strptime(maxDate,"%Y-%m-%d %H:%M:%S"))) 

#connect to mongodb
dbCon <- mongo(collection = "testDb", db = "test", url = "mongodb://145.24.222.182:8001") 

#dataframe to continue with data processing
currencyResult <- dbCon$find(paste0('{"tags":"Ethereum","ticks.last_updated": {"$gte": "', minDate, '" , "$lte": "',maxDate,'"}}'))

currencyDF <- do.call(rbind.data.frame, currencyResult$ticks)
#remove database connection
rm(dbCon)

#========================
currencyDF2<-data.frame(currencyDF$last_updated,currencyDF$price_usd)
names(currencyDF2)=c("last_updated","price_usd")
currencyDF2$last_updated <- as.POSIXct(as.numeric(as.character(currencyDF2$last_updated)),origin='1970-01-01',tz= 'GMT')
currencyDF2$price_usd<-as.numeric(as.character(currencyDF2$price_usd))

aggrData<-(aggregate(. ~ cut(currencyDF2$last_updated, paste(as.character(36*24),"min")),
                     currencyDF2[setdiff(names(currencyDF2), "last_updated")], 
                     FUN = tail, n = 1))
aggrData2<-(aggregate(. ~ cut(currencyDF2$last_updated, paste(as.character(36*24),"min")),
                      currencyDF2[setdiff(names(currencyDF2), "last_updated")], 
                      FUN = max))
aggrData3<-(aggregate(. ~ cut(currencyDF2$last_updated, paste(as.character(36*24),"min")),
                      currencyDF2[setdiff(names(currencyDF2), "last_updated")], 
                      FUN = min))
aggrData$High<-aggrData2$price_usd
aggrData$Low<-aggrData3$price_usd
names(aggrData)<-c("tStamp","Last","High","Low")
df_stock<-aggrData

# Compute the various technical indicators that will be used 
RSI40 <- RSI(df_stock$Last, n = 40,maType="WMA") ;RSI40 <- c(NA,head(RSI40,-1)) ;
RSI50 <- RSI(df_stock$Last, n = 50,maType="WMA") ;RSI50 <- c(NA,head(RSI50,-1)) ;
ADX40 <- ADX(df_stock[,c("High","Low","Last")], n = 40, maType="WMA")[,1] ; ADX40 <- c(NA,head(ADX40,-1)) 
WillR24 <- WPR(df_stock[,c("High","Low","Last")], n = 24) ; WillR24 <- c(NA,head(WillR24,-1)) ;
MOM12 <- momentum(df_stock$Last, n = 12, na.pad = TRUE) ; MOM12 <- c(NA,head(MOM12,-1)) ;
MOM30 <- momentum(df_stock$Last, n = 30, na.pad = TRUE) ; MOM30 <- c(NA,head(MOM30,-1)) ;
MOM24 <- momentum(df_stock$Last, n = 24, na.pad = TRUE) ; MOM24 <- c(NA,head(MOM24,-1)) ;
ROC24 <- ROC(df_stock$Last, n = 24,type ="discrete")*100 ; ROC24 <- c(NA,head(ROC24,-1)) ;
ROC12 <- ROC(df_stock$Last, n = 12,type ="discrete")*100 ; ROC12 <- c(NA,head(ROC12,-1)) ;
WillR12 <- WPR(df_stock[,c("High","Low","Last")], n = 12) ; WillR12 <- c(NA,head(WillR12,-1)) ;
ROC50 <- ROC(df_stock$Last, n = 50,type ="discrete")*100 ; ROC50 <- c(NA,head(ROC50,-1)) ;

dataset <- data.frame(RSI40,RSI50,ADX40,WillR24,MOM12,MOM30,MOM24,ROC24,ROC12,WillR12,ROC50)
dataset <- na.omit(dataset)

#==================
svmModel<-readRDS(file='svmModel.rds')

#1 for up 0 for down
write.csv(if (predict(svmModel,newdata=dataset[nrow(dataset),]) == "UP") 1 else 0,"TAPredict.csv")

rm(list = ls())

list.of.packages <- c("mongolite", "xts","quantmod","TTR")
new.packages <- list.of.packages[!(list.of.packages %in% installed.packages()[,"Package"])]
if(length(new.packages)) install.packages(new.packages)

library(mongolite)
library(xts)
library(quantmod)
library(TTR)

dumpVar<-Sys.setlocale("LC_ALL","English")

maxDate <- Sys.time()
minDate <- maxDate - 3600*26
minDate <- as.integer(as.POSIXct(strptime(minDate,"%Y-%m-%d %H:%M:%S"))) * 1000
maxDate <- as.integer(as.POSIXct(strptime(maxDate,"%Y-%m-%d %H:%M:%S"))) * 1000

#connect to mongodb
dbCon <- mongo(collection = "tweetFeed", db = "TwitterData", url = "mongodb://145.24.222.182:8001") 

#dataframe to continue with data processing
tweetFeed <- dbCon$find(paste0('{"created_at": {"$gte": { "$date" : { "$numberLong" : "', minDate, '" } }, "$lte": { "$date" : { "$numberLong" : "', maxDate, '" } }}}'),paste0('{"text": 1, "created_at": 1, "followers_count": 1}'))

#remove database connection
rm(dbCon)


#========================================================================

score_twitter <- function(data, hashtags){
  # data<-tweetFeed
  # hashtags<-c("eth", "ethereum", "blockchain")
  
  length <- nrow(data)
  data$text<-as.character(data$text)
  data<-data[grep(paste(hashtags,collapse="|"),data[,4],value = F,ignore.case = T),]
  data<-data[,c(2,3)]
  data$followers_count<-1
  dataAgg<-aggregate(. ~ cut(data$created_at, paste(as.character(60),"min")), 
                     data[setdiff(names(data), "created_at")], sum)
  
  period<-4
  lag<-4
  names(dataAgg)<-c("tStamp","fTotW")
  dataAgg$tStamp<-as.POSIXct(strptime(dataAgg$tStamp,"%Y-%m-%d %H:%M:%S"))
  dataAgg$MA<-ZLEMA(dataAgg[,2], period) #quantmod package
  dataAgg$Diff<-abs(dataAgg[,2]-dataAgg$MA)
  for (i in period:(nrow(dataAgg)-period)) {
    dataAgg[(i+period),5]<-sd(dataAgg[i:(period+i),4],na.rm=T)
  }
  
  for (i in (nrow(dataAgg)-(12+lag+1)):nrow(dataAgg)){
    dataAgg[i,6] <- score(dataAgg[i,2], dataAgg[i,3], dataAgg[i,5])
  }
  names(dataAgg)<-c("tStamp","fTotW","MA","Diff","SD","score")
  for (l in 1:lag) {
    dataAgg$score<-c(NA,head(dataAgg$score,-1))
  }
  
  dataAgg$tStamp<-as.numeric(dataAgg$tStamp)#back to unix time
  dataAgg$score<-round(dataAgg$score,2)
  dataAgg[(nrow(dataAgg)-(13-1)):nrow(dataAgg),c(1,6)]
}

score<-function(value, mean, sd){
  if (value <= mean - 3*sd) {
    1
  }
  else if(value>= mean+ 3*sd){
    10 
  }
  else {
    ((value-mean)/sd)*(9/6) + 5.5
  }
}

write.csv(score_twitter(tweetFeed, c("eth", "ethereum", "blockchain")),"resultsTwitterScore.csv")

rm(tweetFeed,minDate,maxDate,score,score_twitter,list.of.packages,new.packages,dumpVar)
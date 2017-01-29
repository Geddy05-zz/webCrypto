list.of.packages <- c("mongolite", "xts","quantmod","TTR","stringr","rjson","tm")
new.packages <- list.of.packages[!(list.of.packages %in% installed.packages()[,"Package"])]
if(length(new.packages)) install.packages(new.packages)


library(stringr);library(rjson);library(tm);library(SnowballC);library(mongolite);
library(xts);library(quantmod);library(TTR)

#rm(list = ls())
Sys.setlocale("LC_ALL","English")
maxDate <- Sys.time()
minDate <- maxDate - 3600*30
time_to_unix <- function(times) minDate <- as.integer(as.POSIXct(strptime(times,"%Y-%m-%d %H:%M:%S"))) * 1000
minDate <- time_to_unix(minDate)
maxDate <- time_to_unix(maxDate)

#connect to mongodb
dbCon <- mongo(collection = "tweetFeed", db = "TwitterData", url = "mongodb://145.24.222.182:8001") 

#dataframe to continue with data processing
tweetFeed <- dbCon$find(paste0('{"created_at": {"$gte": { "$date" : { "$numberLong" : "', minDate, '" } }, "$lte": { "$date" : { "$numberLong" : "', maxDate, '" } }}}'),paste0('{"text": 1, "created_at": 1, "lang":1, "followers_count": 1}'))

#remove database connection
rm(dbCon)

#===============================================================================================

score_twitter <- function(data, hashtags){
  # data<-tweetFeed
  # hashtags<-c("xmr", "monero", "blockchain")
  
  length <- nrow(data)
  data$text<-as.character(data$text)
  data<-data[grep(paste(hashtags,collapse="|"),data[,4],value = F,ignore.case = T),]
  data<-data[,c(2,3)]
  data$followers_count<-1
  dataAgg<-aggregate(. ~ cut(data$created_at, paste(as.character(10),"min")), 
                     data[setdiff(names(data), "created_at")], sum)
  
  period<-48
  lag<-3
  names(dataAgg)<-c("tStamp","fTotW")
  dataAgg$tStamp<-as.POSIXct(strptime(dataAgg$tStamp,"%Y-%m-%d %H:%M:%S"))
  dataAgg$MA<-SMA(dataAgg[,2], period) #quantmod package
  dataAgg$Diff<-abs(dataAgg[,2]-dataAgg$MA)
  for (i in period:(nrow(dataAgg)-period)) {
    dataAgg[(i+period),5]<-sd(dataAgg[i:(period+i),4],na.rm=T)
  }
  
  for (i in (nrow(dataAgg)-(72+lag+1)):nrow(dataAgg)){
    dataAgg[i,6] <- score(dataAgg[i,2], dataAgg[i,3], dataAgg[i,5])
  }
  names(dataAgg)<-c("tStamp","fTotW","MA","Diff","SD","score")
  for (l in 1:lag) {
    dataAgg$score<-c(NA,head(dataAgg$score,-1))
  }
  
  dataAgg$tStamp<-as.numeric(dataAgg$tStamp)#back to unix time
  dataAgg$score<-round(dataAgg$score,2)
  dataAgg[(nrow(dataAgg)-(72-1)):nrow(dataAgg),c(1,6)]
}

#also used by sentiment
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


dfResults<-score_twitter(tweetFeed, c("xmr", "monero", "blockchain"))








#===============================================================================================

tweetFeed2 <- subset(tweetFeed, tweetFeed$lang == "en")
tweetFeed2[,4] <- sapply(tweetFeed2[,4],function(row) iconv(row, "latin1", "ASCII", sub=""))

twittersentiment <- function(twitterdata){
  hackedExchangeCorpus <- Corpus(VectorSource(twitterdata[,4]))
  hackedExchangeCorpus <- tm_map(hackedExchangeCorpus, removePunctuation)
  hackedExchangeCorpus <- tm_map(hackedExchangeCorpus, removeWords, stopwords (kind = "en"))
  badWords <- c("follow","will","You","you","use","can","use","reddit","free","subscribe","Subscribe","news","News","guest","bitfinex","Bitfinex","bitstamp", "Bitstamp", "The", "the", "bitcurex", "Bitcurex","coindesk","Coindesk","COINDESK","China","china","email","newsletter")
  hackedExchangeCorpus <- tm_map(hackedExchangeCorpus, removeWords, badWords)
  hackedExchangeCorpus <- tm_map(hackedExchangeCorpus, stemDocument)
  
  for (i in 1:nrow(twitterdata)) {
    hackedExchangeCorpus[[i]]$content <- gsub("&amp", "", hackedExchangeCorpus[[i]]$content)
    hackedExchangeCorpus[[i]]$content <- gsub("(RT|via)((?:\\b\\W*@\\w+)+)", "", hackedExchangeCorpus[[i]]$content)
    hackedExchangeCorpus[[i]]$content <- gsub("@\\w+", "", hackedExchangeCorpus[[i]]$content)
    hackedExchangeCorpus[[i]]$content <- gsub("[[:digit:]]", "", hackedExchangeCorpus[[i]]$content)
    hackedExchangeCorpus[[i]]$content <- gsub("http\\w+", "", hackedExchangeCorpus[[i]]$content)
    hackedExchangeCorpus[[i]]$content <- gsub("[ \t]{2,}", "", hackedExchangeCorpus[[i]]$content)
    hackedExchangeCorpus[[i]]$content <- gsub("^\\s+|\\s+$", "", hackedExchangeCorpus[[i]]$content)
    hackedExchangeCorpus[[i]]$content <- gsub("?(f|ht)tp(s?)://(.*)[.][a-z]+", "", hackedExchangeCorpus[[i]]$content)
  }
  
  hackedExchangeCorpus <- tm_map(hackedExchangeCorpus, tolower)
  hackedExchangeCorpus <- tm_map(hackedExchangeCorpus, PlainTextDocument)
  mydata.dtm <- DocumentTermMatrix(hackedExchangeCorpus)
  sparse_DTM <- removeSparseTerms(mydata.dtm, 0.9980)
  tweetsSparse <- as.data.frame(as.matrix(sparse_DTM))
  colnames(tweetsSparse) <- make.names(colnames(tweetsSparse))
  
  keywords <- read.csv("Keywords.csv", sep=",")
  keywords <- keywords[,2:3]
  words_per_tweet <- rowSums(tweetsSparse)
  columns <- colnames(tweetsSparse) %in% keywords[,1]
  tweetsSparse <- tweetsSparse[,columns]
  keywords_per_tweet <- rowSums(tweetsSparse)
  fraction <- keywords_per_tweet/words_per_tweet
  mean_fraction <- round(mean(fraction, na.rm = T), digits = 1)
  tweetsSparse <- tweetsSparse[fraction>=mean_fraction,]
  tweetsSparse <- tweetsSparse[complete.cases(tweetsSparse),]
  
  used_keywords <- data.frame(colnames(tweetsSparse))
  colnames(used_keywords) <- "term"
  used_keywords <- merge(used_keywords, keywords, by="term")
  used_keywords$pos.neg <- as.character(used_keywords$pos.neg)
  used_keywords[used_keywords$pos.neg=="negative",2] <- as.character(-1)
  used_keywords[used_keywords$pos.neg=="positive",2] <- as.character(1)
  used_keywords$pos.neg <- as.numeric(used_keywords$pos.neg)
  
  tweetsSparse <- sweep(tweetsSparse,MARGIN=2,used_keywords[,2],`*`)
  total_sentiment <- rowSums(tweetsSparse)
  return(mean(total_sentiment))
}


sentiment <- numeric(12)
time <- Sys.time()
current_time <- Sys.time()

for (l in 1:12) {
  value1 <- 3600*(l-1)
  value2 <- 3600*(l)
  rows <- tweetFeed2$created_at < (current_time - value1) & tweetFeed2$created_at > (current_time - value2)
  time[l] <- (current_time-value1)
  tweetFeed3 <- tweetFeed2[rows,]
  sentiment[l] <- twittersentiment(tweetFeed3)    
}    

scores <- data.frame()
for (d in 1:length(sentiment)) {
  scores[d,1] <- time_to_unix(time[d])
  scores[d,2] <- round(score(sentiment[d], 1.58, 0.209), digits = 2)
}

colnames(scores) <- c("tStamp", "score")
dfResults$scoreSentiment<-"NA"
for (i in 1:12){
  dfResults$scoreSentiment[i*6]<-scores$score[i]
}

write.csv(dfResults, file = "twitterScore.csv")

rm(list = ls())


list.of.packages <- c("mongolite", "rjson","tm","SnowballC", "plyr")
new.packages <- list.of.packages[!(list.of.packages %in% installed.packages()[,"Package"])]
if(length(new.packages)) install.packages(new.packages)

library(mongolite)
library(rjson)
library(tm)
library(SnowballC)
library(plyr)

Sys.setlocale("LC_ALL","English")
maxDate <- Sys.time()
minDate <- maxDate - 3600 * 12 # hours
minDate <- as.integer(as.POSIXct(strptime(minDate,"%Y-%m-%d %H:%M:%S"))) * 1000
maxDate <- as.integer(as.POSIXct(strptime(maxDate,"%Y-%m-%d %H:%M:%S"))) * 1000

#connect to mongodb
dbCon <- mongo(collection = "CryptoNews", db = "RssFeed", url = "mongodb://145.24.222.55:8001")
#dataframe
crypto_news <- dbCon$find(paste0('{"published": {"$gte": { "$date" : { "$numberLong" : "', minDate, '" } }, "$lte": { "$date" : { "$numberLong" : "', maxDate, '" } }}}'))
#remove database connection
rm(dbCon)
#connect again to mongodb
dbCon <- mongo(collection = "FinNews", db = "RssFeed", url = "mongodb://145.24.222.55:8001")
#dataframe
fin_news <- dbCon$find(paste0('{"published": {"$gte": { "$date" : { "$numberLong" : "', minDate, '" } }, "$lte": { "$date" : { "$numberLong" : "', maxDate, '" } }}}'))
#remove database connection
rm(dbCon)
#merge dataframe
rss_feeds <- rbind(crypto_news,fin_news)

#========================  Word Processing  =============================
removeHtmlTags <- function(htmlString) {
  return(gsub("<.*?>", "", htmlString))
}

trim <- function (x) gsub("^\\s+|\\s+$", "", x)

processWords <- function(x,name){
  hackedExchangeCorpus <- Corpus(VectorSource(x))
  hackedExchangeCorpus <- tm_map(hackedExchangeCorpus, PlainTextDocument)
  hackedExchangeCorpus <- tm_map(hackedExchangeCorpus, removePunctuation)
  hackedExchangeCorpus <- tm_map(hackedExchangeCorpus, removeWords, stopwords (kind = "en"))
  badWords <-  c("follow","will","You","you","use","can","use","reddit","free","subscribe","Subscribe","news","News","guest","bitfinex","Bitfinex","bitstamp", "Bitstamp", "The", "the", "bitcurex", "Bitcurex","coindesk","Coindesk","COINDESK","China","china","email","newsletter")
  hackedExchangeCorpus <- tm_map(hackedExchangeCorpus, removeWords, badWords)
  hackedExchangeCorpus <- tm_map(hackedExchangeCorpus, stemDocument)
  hackedExchangeCorpus <- tm_map(hackedExchangeCorpus, tolower)
  hackedExchangeCorpus <- tm_map(hackedExchangeCorpus, PlainTextDocument)
  hackedExchangeDTM <- DocumentTermMatrix(hackedExchangeCorpus)
  hackedExchangeTermFreq <- colSums(as.matrix(hackedExchangeDTM))
  hackedExchangeKeyWords <- data.frame(term = names(hackedExchangeTermFreq), freq = hackedExchangeTermFreq)
  hackedExchangeKeyWords <- hackedExchangeKeyWords[order(-hackedExchangeKeyWords[,2]),]
  hackedExchangeKeyWords[,3] <- c(hackedExchangeKeyWords$freq/sum(hackedExchangeKeyWords$freq))
  hackedExchangeKeyWords <- hackedExchangeKeyWords[1:nrow(hackedExchangeKeyWords),]
  coinNameDatabase <-  name
  coinNamesFound <- coinNameDatabase %in% hackedExchangeKeyWords$term
  if(coinNamesFound==T){
    hackedExchangeKeyWords[,4]<-as.character(name)
  }
  if(coinNamesFound==F){
    hackedExchangeKeyWords[,4]<-NA
  }
  colnames(hackedExchangeKeyWords) <- c("term","freq","percentage","subject")
  rownames(hackedExchangeKeyWords) <- NULL
  return(hackedExchangeKeyWords)
}

i<-0
r <- list()
currency_name <- "litecoin"

for(detail in rss_feeds$description) {
  tagless_detail <- removeHtmlTags(detail)
  tagless_detail <- trim(tagless_detail)
  i <-i+1
  r[[i]] <- (processWords(tagless_detail, currency_name))
}

if (i>1) r2 <- rbind(r[[1]], r[[2]])
if (i==1) r2 <- r[[1]]
if (i==0) r2 <- data.frame()
if (nrow(rss_feeds)>2) {
  for(i in 3:nrow(rss_feeds)) {
    r2 <- rbind(r2, r[[i]])
  }
}

data_processor <- function(data, name){
  data <- subset(data, data$subject == name)
  data
}

if(nrow(r2)>0){
  r2 <- data_processor(r2, currency_name)
  r3 <- aggregate(r2$percentage, by=list(r2$term), FUN = sum)
  colnames(r3) <- c("term", "percentage")
  r2 <- aggregate(r2$freq, by=list(r2$term), FUN = sum)
  colnames(r2) <- c("term", "freq")
  r3 <- merge(r2,r3, by="term")
  r3 <- r3[order(r3[,3], decreasing = T),]
  unique_words <- length(unique(r3$term))
  unique_words <- as.integer(0.10*unique_words)
  
  data_text <- r3[1:unique_words,1:2]
  data_text <- tolower(rep(data_text[,1], data_text[,2]))
  
  data_keywords <- read.csv("eventKeyWords.csv", sep = ";")
  
  j <- 20
  rows <- j + (c(1:9)-1)*100
  rows2 <- 1 + (c(1:9)-1)*100
  rows3 <- numeric(9*j)
  for (i in 1:9) {
    first <- (i-1)*j+1
    second <- i*j
    rows3[first:second] <- rows2[i]:rows[i]
  }
  data_keywords <- data_keywords[rows3,]
  
  freq_per_event <- aggregate(data_keywords$freq, by=list(data_keywords$event), FUN=sum)
  colnames(freq_per_event) <- c("event", "tot_frequency")
  data_keywords <- merge(data_keywords, freq_per_event, by = "event")
  data_keywords$percentage <- data_keywords$freq/data_keywords$tot_frequency
  
  log_to_percentage <- function(log_values){
    log <- aggregate(as.numeric(log_values[,1]), by=list(log_values[,2]), FUN=sum)
    log <- log[order(log[,2], decreasing = T),]
    
    log[1,3] <- 1
    for(i in 2:nrow(log)){
      #log[i,3] <- (log[i,2]/log[1,2]) #fraction
      log[i,3] <- 1/(log[i,2]/log[1,2]) #log-value
    }
    log[,4] <- log[,3]/sum(log[,3])
    log[,c(1,4)]
  }
  
  bayes_keywords_event <- function(data_keyword, data_text, rows_per_event, number_of_events){
    chance_matrix <- matrix("", nrow = length(data_text)+1, ncol = number_of_events)
    number_of_words <- length(data_text)
    freq_per_class <- aggregate(data_keyword$freq, by=list(data_keyword$event), FUN=sum)
    chance_matrix[1,] <- freq_per_class[,2]/sum(freq_per_class[,2])
    colnames(chance_matrix)<- sort(unique(data_keyword$event), decreasing = F)
    events <- as.data.frame(sort(unique(data_keyword$event), decreasing = F))
    events$number_event <- c(1:nrow(events))
    colnames(events) <- c("event", "number_event")
    data_keyword <- subset(data_keyword, data_keyword$term %in% data_text)
    
    distinct_words <- length(unique(data_keywords$term))
    
    chances <- 1/(freq_per_class[,2]+distinct_words)
    
    data_text <- as.data.frame(data_text)
    data_text$number_term <- c(1:nrow(data_text))
    colnames(data_text) <- c("term", "number_term")
    
    data_keyword <- merge(data_keyword, data_text, by = "term")
    data_keyword <- merge(data_keyword, events, by = "event")
    
    for(i in 2:(nrow(data_text)+1)){
      chance_matrix[i,] <- chances
    }
    
    for(i in 1:nrow(data_keyword)){
      chance_matrix[data_keyword[i,8]+1, data_keyword[i,9]] <- data_keyword[i,5]
    }
    
    chance_matrix <- as.data.frame(log(as.numeric(chance_matrix)))
    #chance_matrix <- as.data.frame((as.numeric(chance_matrix)))
    
    chance_matrix$number_event <- ""
    for(i in 1:number_of_events){
      first <- (i-1)*(number_of_words+1)+1
      second <- i*(number_of_words+1)
      chance_matrix[first:second,2] <- rep(events[i,1], number_of_words+1)
    }
    chance_matrix <- merge(chance_matrix, events, by= "number_event", all=T)
    chance_matrix[,2:3]
  }
  
  log_matrix <- bayes_keywords_event(data_keywords,data_text, rows_per_event, 9)
  sentiment_percentages <- log_to_percentage(log_matrix)
  sentiment_percentages[,2] <- sentiment_percentages[,2]*100
}

if(nrow(r2)==0){
  sentiment_percentages <- as.data.frame(c("bailout", "bannedFromCountry", "coinAcception",
                                           "hackedExchange", "halvingDay", "marketplaceAcceptance", "pricedrop", "priceIncrease", "taxation"))
  sentiment_percentages[,2] <- rep(100/9, 9)
}

colnames(sentiment_percentages) <- c("event", "percentage")
sentiment_percentages[,2] <- round(sentiment_percentages[,2], digits = 1)
event <- c("bannedFromCountry", "hackedExchange", "halvingDay", "marketplaceAcceptance",
           "pricedrop", "priceIncrease", "taxation", "bailout", "coinAcception")
pos.neg <- c("p","n", "p", "p", "n", "p", "n", "p", "p")
sentiment_event <- data.frame(event, pos.neg)
sentiment_percentages <- merge(sentiment_percentages, sentiment_event, by="event")
sentiment_percentages <- sentiment_percentages[order(sentiment_percentages[,2], decreasing = T),]

write.csv(sentiment_percentages, file = "sentimentEventScore.csv")
rm(list = ls())


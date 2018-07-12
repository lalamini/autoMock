#for log
GZIP_LIST = ['oauth_login_smsLogin_htm','followStockService_query','securityFinanceService_queryHoldPositionOverview','dynamicConfiguration_queryMyConditionConfiguration']
#action that will be dynmatic, "r" means just read, "+" means status add 1, "-" means status minus 1
STATUS_NODE=[
   {"followstock":{
        "/cg/followStockService.query":"r",
        "/cg/followStockService.follow":"+",
        "/cg/followStockService.unfollow":"-",
        },
    },
   {"stockhold":{
        "/cg/orderService.queryEntrustRecordsWithPage":"r",
        "/cg/securityExchangeController.securitiesTrading":"+",
        "/cg/orderService.revoke":"+",
        "/cg/securityExchangeController.entrustSecurities":"+",
        "/cg/orderService.queryEntrustRecordsWithPage":"r",
        "/cg/orderService.queryRevokingRecordByType":"r"
        }
   },
   {"queryentruststates":{
        "/cg/securityExchangeController.securitiesTrading":"+",
        "/cg/securityExchangeController.entrustSecurities":"+",
        "/cg/orderService.queryEntrustStates":"r"
       }
   },
   {"conditionmonitor":{
        "/conditionTradeService.pause":"+",
        "/conditionTradeService.resume":"-",
        "/v2/condition.monitoring":"r"
       }
   }
]
#request body used to match
NEED_REQUESTBODY=['/cg/gradedFundDetailQueryController.queryFundTypeList','/cg/stockService.queryConstituentStocks']

#the key that response header don't need
REMOVE_RESPONSE_HEADER_KEY=["DATA",]

#the key that request header don't need
REMOVE_REQUEST_HEAD_KEY=['USER_AGENT','TOKEN','HID','HOST','COOKIE','CONTENT_LENGTH','t']

#the url which shoud use 443, https way
HTTPS_RE_MATCH=['^api','static']

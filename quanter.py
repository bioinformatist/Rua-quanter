#!/usr/bin/env python3
import tushare as ts
import pandas as pd
from optparse import OptionParser

TOKEN = '8fd2c84fb61b1303b5b39aaabd671b75a1c5a0ea4d43dbc1a3e03e7a'
pro = ts.pro_api(TOKEN)

def main():
    usage = """
                                               ,---,    ,---,    ,---,  
                                        ,`--.' | ,`--.' | ,`--.' |  
,-.----.                    ,---,       |   :  : |   :  : |   :  :  
\    /  \           ,--,   '  .' \      '   '  ; '   '  ; '   '  ;  
;   :    \        ,'_ /|  /  ;    '.    |   |  | |   |  | |   |  |  
|   | .\ :   .--. |  | : :  :       \   '   :  ; '   :  ; '   :  ;  
.   : |: | ,'_ /| :  . | :  |   /\   \  |   |  ' |   |  ' |   |  '  
|   |  \ : |  ' | |  . . |  :  ' ;.   : '   :  | '   :  | '   :  |  
|   : .  / |  | ' |  | | |  |  ;/  \   \;   |  ; ;   |  ; ;   |  ;  
;   | |  \ :  | | :  ' ; '  :  | \  \ ,'`---'. | `---'. | `---'. |  
|   | ;\  \|  ; ' |  | ' |  |  '  '--'   `--..`;  `--..`;  `--..`;  
:   ' | \.':  | : ;  ; | |  :  :        .--,_    .--,_    .--,_     
:   : :-'  '  :  `--'   \|  | ,'        |    |`. |    |`. |    |`.  
|   |.'    :  ,      .-./`--''          `-- -`, ;`-- -`, ;`-- -`, ; 
`---'       `--`----'                     '---`"   '---`"   '---`"                                                                                                               
     .;|$$$$$$$%%|!;:.      `
   :||$&&&&&&&&&&@&$%$|`    `
 `|$%%%$$&@@@@@@@@@@@$$$!   `
'$&$$$&&&&@@@@@@@@@@@&&$%;  `
:$&&&&$&@&&&@@@@@@@@@@&&&$: `
!@@@@&%%$@@&&@@@@@@@@@@@&&%``
|@@#@&&$%|%&&$&&@@@##@@@@@&:`
!@##&%%%%%|!!||!|%&&$$@@@@@;'
:&#@$!;!||%$$|!!|%$$%!::%@@;'
 :@&!:;!!||||!::;!!!;:'':%&'`
  ;$;``'::::;:'''::::''':||.`
   ;;``':::;:'::::;||;;;:;` `
     `:;!!|||%%|!:::!||;:`  `
     .:!|||||%%|!;;|%!;;'.  `
       :!!!|%$%%%||!;;;:'   `
        `;!!!!!;;;;;;;;:.   `
          ';;!!|||!;:;:     `   
    usage: %prog [options] arg
    """
    parser = OptionParser(usage)
    parser.add_option("--date", dest = "date",
                      help = "很感兴趣的某一天，比如20200402")
    parser.add_option("--start_date", dest = "start_date",
                      help = "感兴趣的起始日期，比如20200324")
    parser.add_option("--end_date", dest = "end_date",
                      help = "感兴趣的终止日期，比如20200407")
    parser.add_option("--min_ratio", dest = "min_ratio",
                      help = "交易量比值的最小允许取值")
    parser.add_option("--max_ratio", dest = "max_ratio",
                      help = "交易量比值的最大允许取值")                  
    parser.add_option("-f", "--file", dest = "filename", default = "out.xlsx",
                      help="输出的Excel文件名")

    (options, args) = parser.parse_args()

    def get_date_list(start_date, end_date):
        date_list = [x.strftime('%Y%m%d') for x in list(pd.date_range(start = start_date, end = end_date))]
        return date_list

    stock_list = pro.stock_basic(fields='ts_code, name')

    trade_date_range = get_date_list(options.start_date, options.end_date)

    range_data = pd.DataFrame()
    
    for day in trade_date_range:
        df = pro.daily(trade_date = day, fields = 'ts_code, vol')
        if not df.empty: range_data = range_data.append(df)
    
    day_data = pro.daily(trade_date = options.date, fields = 'ts_code, vol')

    mean_vol = range_data.groupby('ts_code')['vol'].mean()

    merged_df = pd.merge(mean_vol, day_data, on = 'ts_code', how = 'inner')
    merged_df = pd.merge(merged_df, stock_list, on = 'ts_code', how = 'inner')
    merged_df['vol_ratio'] = merged_df['vol_y'] / merged_df['vol_x']
    merged_df.loc[(merged_df['vol_ratio'] > float(options.min_ratio)) & (merged_df['vol_ratio'] < float(options.max_ratio))][['ts_code', 'name', 'vol_ratio']].to_excel(options.filename, index = False)

if __name__ == "__main__":
    main()
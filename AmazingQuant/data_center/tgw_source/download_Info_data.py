# -*- coding: utf-8 -*-

# ------------------------------
# @Time    : 2023/6/20
# @Author  : gao
# @File    : download_Info_data.py
# @Project : AmazingQuant 
# ------------------------------
import os
import time

import pandas as pd
import numpy as np
import tgw

from AmazingQuant.data_center.tgw_source.tgw_login import tgw_login
from AmazingQuant.data_center.tgw_source.tgw_api import TgwApiData
from AmazingQuant.data_center.update_local_data.save_data import save_data_to_hdf5
from AmazingQuant.data_center.api_data.get_data import get_local_data
from AmazingQuant.config.local_data_path import LocalDataPath
from AmazingQuant.constant import LocalDataFolderName, AdjustmentFactor


class DownloadInfoData(object):
    def __init__(self, code_list_hist, index_list):
        self.code_list_hist = code_list_hist
        self.index_list = index_list

    def download_info_data(self, id, para_code_list='stock_list', para_date=False):
        result_df = None
        num = 1
        error_code_list = []
        code_list = []
        if para_code_list == 'stock_list':
            code_list = self.code_list_hist
        elif para_code_list == 'index_list':
            code_list = self.index_list
        # print('code_list', code_list)
        for code in code_list:
            print(id, code, num)
            num += 1
            code_isalpha=False
            for i in code[:-3]:
                if i.isalpha():
                    code_isalpha = True
                    break
            if code_isalpha:
                continue
            task_id = tgw.GetTaskID()
            tgw.SetThirdInfoParam(task_id, "function_id", id)
            if para_code_list == 'stock_list':
                tgw.SetThirdInfoParam(task_id, "market_code", code)
            elif para_code_list == 'index_list':
                tgw.SetThirdInfoParam(task_id, "index_code", code)

            if para_date:
                tgw.SetThirdInfoParam(task_id, "start_date", "19900101")
                tgw.SetThirdInfoParam(task_id, "end_date", "20991231")

            df, error = tgw.QueryThirdInfo(task_id)
            if result_df is None:
                result_df = df
            else:
                result_df = pd.concat([result_df, df])
            if error != '':
                error_code_list.append(code)
                print('error', type(error), error, error_code_list)
        return result_df, error_code_list

    def download_industry_class(self):
        """
        行业分类 A010010002
        """
        industry_class_df, error_code_list = self.download_info_data('A010010002')
        folder_name = LocalDataFolderName.INDUSTRY_CLASS.value
        path = LocalDataPath.path + folder_name + '/'
        save_data_to_hdf5(path, 'industry_class', industry_class_df)
        return industry_class_df

    def download_index_member(self):
        """
        指数成分股 A010200001
        """
        index_member_df, error_code_list = self.download_info_data('A010200001', para_code_list='index_list')
        print('index_member_df', index_member_df)
        folder_name = LocalDataFolderName.INDEX_MEMBER.value
        path = LocalDataPath.path + folder_name + '/'
        save_data_to_hdf5(path, 'index_member', index_member_df)
        return index_member_df

    def download_stock_struction(self):
        """
        股本结构 A010010004
        """
        stock_struction_df, error_code_list = self.download_info_data('A010010004', para_date=True)

        folder_name = LocalDataFolderName.FINANCE.value
        path = LocalDataPath.path + folder_name + '/'
        save_data_to_hdf5(path, 'stock_struction', stock_struction_df)
        return stock_struction_df

    def download_finance_data(self):
        """
        A股一般企业资产负债表  A010050001
        A股一般企业利润表     A010050002
        A股一般企业现金流表   A010050003
        """
        data_dict = {"A010050001": "balance", "A010050002": "income", "A010050003": "cash_flow"}
        result = {}
        for key, value in data_dict.items():
            result[value], error_code_list = self.download_info_data(key, para_date=True)
            folder_name = LocalDataFolderName.FINANCE.value
            path = LocalDataPath.path + folder_name + '/'
            save_data_to_hdf5(path, value, result[value])
        return result

    def download_longhubang(self):
        """
        交易异动营业部买卖信息 A010070002
        """
        longhubang_df, error_code_list = self.download_info_data('A010070002', para_date=True)

        folder_name = LocalDataFolderName.FINANCE.value
        path = LocalDataPath.path + folder_name + '/'
        save_data_to_hdf5(path, 'longhubang', longhubang_df)
        return longhubang_df


if __name__ == '__main__':
    tgw_login(server_mode=True)

    tgw_api_object = TgwApiData(20991231)
    index_list = tgw_api_object.get_code_list(add_market=True, all_code=True, index=True)
    code_list_hist = tgw_api_object.get_code_list_hist()
    calendar_index = tgw_api_object.get_calendar()
    info_data_object = DownloadInfoData(code_list_hist, index_list)
    # industry_class_df = info_data_object.download_industry_class()
    index_member_df = info_data_object.download_index_member()
    # info_data_object.download_stock_struction()
    # result = info_data_object.download_finance_data()

    # folder_name = LocalDataFolderName.INDUSTRY_CLASS.value
    # path = LocalDataPath.path + folder_name + '/'
    # a = get_local_data(path, folder_name + '.h5')


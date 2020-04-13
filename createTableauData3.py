import pandas as pd
import numpy as np
import re

from math import atan, degrees
from datetime import datetime


class CreateTableauData(object):
    #################################################### Global Namespace
    global total_cases3, total_deaths3, total_recovery3, total_critical3, total_quarantine3
    global index, quantileFrame

    #################################################### Import existing files
    total_cases3 = pd.read_excel(r'data/nuts3/featureTables/total_cases_nuts3.xlsx', index=False)
    total_deaths3 = pd.read_excel(r'data/nuts3/featureTables/total_deaths_nuts3.xlsx', index=False)
    total_recovery3 = pd.read_excel(r'data/nuts3/featureTables/total_recovery_nuts3.xlsx', index=False)
    total_critical3 = pd.read_excel(r'data/nuts3/featureTables/total_critical_nuts3.xlsx', index=False)
    total_quarantine3 = pd.read_excel(r'data/nuts3/featureTables/total_quarantine_nuts3.xlsx', index=False)

    ################################################### Clean the column names+
    columns = total_cases3.columns
    newCols = [re.sub('[' + re.escape(''.join(['(', '\'', ')', ','])) + ']', '', col) for col in columns]
    total_cases3.columns = newCols
    total_deaths3.columns = newCols
    total_recovery3.columns = newCols
    total_critical3.columns = newCols
    total_quarantine3.columns = newCols


    def computeQuantiles(self, days, requireIndex):

        global index
        ################################################ Subset the dataframe based on last "how many hours"
        bottomRowCounts = 0  # depends on diffDays
        timeBW = total_cases3['District']
        try:
            timeBW = [datetime.strptime('2020' + str(time), "%Y%d%m%H%M") if len(str(time))==8 else datetime.strptime('20200' + str(time), "%Y%d%m%H%M")for time in timeBW ]
        except :
            pass
        total_cases3['District'] = timeBW
        lastUpdateTime = list(timeBW)[-1]
        ################################################# Selects the bottom rows based on past number of days
        for row in reversed(timeBW):
            diff = (lastUpdateTime - row).total_seconds()  # 3 days have : 86400 *3
            if diff <= 86400 * days:
                bottomRowCounts += 1

        subsetFrame = total_cases3[len(total_cases3) - bottomRowCounts:len(total_cases3)]
        subsetFrame['Deutschland Total'] = subsetFrame.drop('District', axis=1).sum(axis=1)
        # subsetFrame.District = [datetime.strptime('20200' + str(time), "%Y%d%m%H%M") for time in
        #                           subsetFrame.District]
        subsetFrame.District = [time.strftime('%d %B %H:%M') for time in subsetFrame.District]

        ################################################# Compute the quantiles to split aggregate data growth on a common scale.
        #min = subsetFrame['Deutschland Total'][len(total_cases3) - bottomRowCounts]
        q1 = round(np.quantile(subsetFrame['Deutschland Total'], .25))
        q2 = round(np.quantile(subsetFrame['Deutschland Total'], .50))
        q3 = round(np.quantile(subsetFrame['Deutschland Total'], .75))
        #max = np.quantile(subsetFrame['Deutschland Total'], 1)

        q = [q1, q2, q3]
        q_index = 0
        cell_index = len(total_cases3) - bottomRowCounts
        index = [cell_index]

        for element in subsetFrame['Deutschland Total']:
            if q[q_index] - element <= 0:
                index.append(cell_index)
                q_index += 1
            cell_index += 1
            if q_index == 3:
                break
        index.append(len(total_cases3) - 1)  # use this to subset other featureTables

        # Index value to finally subset
        quantileFrame = subsetFrame[subsetFrame.index.isin(index)].T
        quantileFrame.reset_index(level=0, inplace=True)
        quantileFrame.columns = quantileFrame.iloc[0]
        quantileFrame = quantileFrame.iloc[1:]
        if requireIndex:
            return index
        return quantileFrame

    def featureEngineering(self, quantileFrame):
        ##################################################### create all extra columns here
        column = quantileFrame.columns
        l = len(column)
        growth_rate = []

        for row in range(len(quantileFrame)):
            first = quantileFrame[column[1]][row + 1]
            if first == 0:
                divide = 1
            else:
                divide = first
            last = quantileFrame[column[l - 1]][row + 1]
            growth_rate.append(round(((last - first) / divide) * 100, 1))
        quantileFrame['Growth Rate'] = growth_rate

        column = quantileFrame.columns
        l = len(column)
        quantileFrame['new_cases (1 hour)'] = [
            round(((quantileFrame[column[l - 2]][row + 1] - quantileFrame[column[1]][row + 1]) / 24),1) for row in
            range(len(quantileFrame))]
        column = quantileFrame.columns
        l = len(column)

        quantileFrame['growth_slope_24 (Degrees)'] = [round(degrees(atan((quantileFrame[column[l - 3]][row + 1] - quantileFrame[column[1]][row + 1]) / 24)), 2)
            for row in range(len(quantileFrame))]

        quantileFrame['last_update'] = column[5]
        quantileFrame['Total Cases'] = quantileFrame[column[5]]
        quantileFrame['total_new_cases (24 hours)'] = quantileFrame['new_cases (1 hour)'] * 24
        return quantileFrame
    
    def totalDeathCalculate(self,days):
        index = self.computeQuantiles(days,True)
        subset2 = total_deaths3.iloc[index[:len(index)]]
        subset2['Deutschland Total'] = subset2.drop('District', axis=1).sum(axis=1)
        subset2.District = [datetime.strptime('2020' + str(time), "%Y%d%m%H%M") for time in
                              subset2.District]
        subset2.District = [time.strftime('%d %b %H:%M') for time in subset2.District]
        subset2 = subset2.T
        subset2.reset_index(level=0, inplace=True)
        subset2.columns = subset2.iloc[0]
        subset2 = subset2.iloc[1:]
        column = subset2.columns
        try:
            new_death = subset2[column[5]] - subset2[column[1]]
        except:
            new_death = subset2[column[5]] - subset2[column[3]]

        total_death = subset2[column[5]]

        return [new_death, total_death]
    
    def totalRecoveryCalculate(self, days):
        index = self.computeQuantiles(days,True)
        subset2 = total_recovery3.iloc[index[:len(index)]]
        subset2['Deutschland Total'] = subset2.drop('District', axis=1).sum(axis=1)
        subset2.District = [datetime.strptime('2020' + str(time), "%Y%d%m%H%M") for time in
                              subset2.District]
        subset2.District = [time.strftime('%d %b %H:%M') for time in subset2.District]
        subset2 = subset2.T
        subset2.reset_index(level=0, inplace=True)
        subset2.columns = subset2.iloc[0]
        subset2 = subset2.iloc[1:]
        column = subset2.columns
        try:
            new_recovery = subset2[column[5]] - subset2[column[1]]
        except:
            new_recovery = subset2[column[5]] - subset2[column[3]]

        total_recovery = subset2[column[5]]

        return [new_recovery, total_recovery]

    def totalCriticalCalculate(self, days):
        index = self.computeQuantiles(days,True)
        subset2 = total_critical3.iloc[index[:len(index)]]
        subset2['Deutschland Total'] = subset2.drop('District', axis=1).sum(axis=1)
        subset2.District = [datetime.strptime('2020' + str(time), "%Y%d%m%H%M") for time in
                              subset2.District]
        subset2.District = [time.strftime('%d %b %H:%M') for time in subset2.District]
        subset2 = subset2.T
        subset2.reset_index(level=0, inplace=True)
        subset2.columns = subset2.iloc[0]
        subset2 = subset2.iloc[1:]
        column = subset2.columns
        try:
            new_critical = subset2[column[5]] - subset2[column[1]]
        except:
            new_critical = subset2[column[5]] - subset2[column[3]]

        total_critical = subset2[column[5]]

        return [new_critical, total_critical]

    def totalQuarantineCalculate(self, days):
        index = self.computeQuantiles(days,True)
        subset2 = total_quarantine3.iloc[index[:len(index)]]
        subset2['Deutschland Total'] = subset2.drop('District', axis=1).sum(axis=1)
        subset2.District = [datetime.strptime('2020' + str(time), "%Y%d%m%H%M") for time in
                              subset2.District]
        subset2.District = [time.strftime('%d %b %H:%M') for time in subset2.District]
        subset2 = subset2.T
        subset2.reset_index(level=0, inplace=True)
        subset2.columns = subset2.iloc[0]
        subset2 = subset2.iloc[1:]
        column = subset2.columns
        try:
            new_quarantine = subset2[column[5]] - subset2[column[1]]
        except:
            new_quarantine = subset2[column[5]] - subset2[column[3]]

        total_quarantine = subset2[column[5]]

        return [new_quarantine, total_quarantine]






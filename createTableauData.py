import pandas as pd
import numpy as np
from math import atan, degrees
from datetime import datetime


class CreateTableauData(object):
    #################################################### Global Namespace
    global total_cases1, total_deaths1, total_recovery1
    global index, quantileFrame

    #################################################### Import existing files
    total_cases1 = pd.read_excel(r'data/nuts1/featureTables/total_cases_nuts1.xlsx', index=False)
    total_deaths1 = pd.read_excel(r'data/nuts1/featureTables/total_deaths_nuts1.xlsx', index=False)
    total_recovery1 = pd.read_excel(r'data/nuts1/featureTables/total_recovery_nuts1.xlsx', index=False)

    def computeQuantiles(self, days, requireIndex):

        global index
        ################################################ Subset the dataframe based on last "how many hours"
        bottomRowCounts = 0  # depends on diffDays
        #now = datetime.now()
        timeBW = total_cases1['Bundesland']
        timeBW = [datetime.strptime('2020' + str(time), "%Y%d%m%H%M") for time in timeBW]
        lastUpdateTime = timeBW[-1]
        ################################################# Selects the bottom rows based on past number of days
        for row in reversed(timeBW):
            diff = (lastUpdateTime - row).total_seconds()  # 3 days have : 86400
            if diff <= 86400 * days:
                bottomRowCounts += 1

        subsetFrame = total_cases1[len(total_cases1) - bottomRowCounts:len(total_cases1)]
        subsetFrame['Deutschland Total'] = subsetFrame.drop('Bundesland', axis=1).sum(axis=1)
        subsetFrame.Bundesland = [datetime.strptime('2020' + str(time), "%Y%d%m%H%M") for time in
                                  subsetFrame.Bundesland]
        subsetFrame.Bundesland = [time.strftime('%d %B %H:%M') for time in subsetFrame.Bundesland]

        ################################################# Compute the quantiles to split aggregate data growth on a common scale.
        #min = subsetFrame['Deutschland Total'][len(total_cases1) - bottomRowCounts]
        q1 = round(np.quantile(subsetFrame['Deutschland Total'], .25))
        q2 = round(np.quantile(subsetFrame['Deutschland Total'], .50))
        q3 = round(np.quantile(subsetFrame['Deutschland Total'], .75))
        #max = np.quantile(subsetFrame['Deutschland Total'], 1)

        q = [q1, q2, q3]
        q_index = 0
        cell_index = len(total_cases1) - bottomRowCounts
        index = [cell_index]

        for element in subsetFrame['Deutschland Total']:
            if q[q_index] - element <= 0:
                index.append(cell_index)
                q_index += 1
            cell_index += 1
            if q_index == 3:
                break
        index.append(len(total_cases1) - 1)  # use this to subset other featureTables

        if requireIndex:
            return index
        # Index value to finally subset

        quantileFrame = subsetFrame[subsetFrame.index.isin(index)].T
        quantileFrame.reset_index(level=0, inplace=True)
        quantileFrame.columns = quantileFrame.iloc[0]
        quantileFrame = quantileFrame.iloc[1:]
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
            round(((quantileFrame[column[l - 2]][row + 1] - quantileFrame[column[1]][row + 1]) / 24), 2) for row in
            range(len(quantileFrame))]
        column = quantileFrame.columns
        l = len(column)
        quantileFrame['total_new_cases (24 hours)'] = quantileFrame['new_cases (1 hour)'] * 24

        quantileFrame['growth_slope_24 (Degrees)'] = [round(degrees(atan((quantileFrame[column[l - 3]][row + 1] - quantileFrame[column[1]][row + 1]) / 24)), 2)
            for row in range(len(quantileFrame))]

        quantileFrame['last_update'] = column[5]
        quantileFrame['Total Cases'] = quantileFrame[column[5]]

        # quantileFrame['total_new_cases (24 hours)'] = [round((quantileFrame[column[6]][row + 1] - quantileFrame[column[1]][row + 1]) / 24) for row in
        #     range(len(quantileFrame))]


        return quantileFrame

    def totalDeathCalculate(self,days):
        index = self.computeQuantiles(days,True)
        subset2 = total_deaths1.iloc[index[:len(index)]]
        subset2['Deutschland Total'] = subset2.drop('Bundesland', axis=1).sum(axis=1)
        subset2.Bundesland = [datetime.strptime('2020' + str(time), "%Y%d%m%H%M") for time in
                              subset2.Bundesland]
        subset2.Bundesland = [time.strftime('%d %B %H:%M') for time in subset2.Bundesland]
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
        subset2 = total_recovery1.iloc[index[:len(index)]]
        subset2['Deutschland Total'] = subset2.drop('Bundesland', axis=1).sum(axis=1)
        subset2.Bundesland = [datetime.strptime('2020' + str(time), "%Y%d%m%H%M") for time in
                              subset2.Bundesland]
        subset2.Bundesland = [time.strftime('%d %B %H:%M') for time in subset2.Bundesland]
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


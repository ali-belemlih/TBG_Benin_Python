#################################
######## Incomplete File ########
### Refer cum_data_import.py ####
#################################

from collections import defaultdict

class CumulativeCalculation:
    def __init__(self):
        self.total_actual1_value = 0
        self.total_actual2_value = 0
        self.total_actual3_value = 0

        self.total_real_value = 0
        self.total_budget_value = 0
        self.total_last_year_real_value = 0
        
    def calculate_actual(self, real_value_dict, monthly_data_df, month):
        if month in ["jan", "feb", "mar", "annual"]:
            return

        if("actual1_value" in monthly_data_df.keys()):
            self.total_actual1_value += monthly_data_df["actual1_value"]
        if("actual2_value" in monthly_data_df.keys()):
            self.total_actual2_value += monthly_data_df["actual2_value"]
        if("actual3_value" in monthly_data_df.keys()):
            self.total_actual3_value += monthly_data_df["actual3_value"]

        first_quarter_real = real_value_dict["jan"] + real_value_dict["feb"] + real_value_dict["mar"]
        second_quarter_real = real_value_dict["apr"] + real_value_dict["may"] + real_value_dict["jun"]

        if month in ["apr", "may", "jun"]:
            return first_quarter_real + self.total_actual1_value

        if month in ["jul", "aug", "sep"]:
            return first_quarter_real + real_value_dict["apr"] + real_value_dict["may"] + self.total_actual2_value

        if month in ["oct", "nov", "dec"]:
            return first_quarter_real + second_quarter_real + real_value_dict["jul"] + real_value_dict["aug"] + self.total_actual3_value


    def calculate(self, monthly_data_df, month, valueDict):
        cumulative_data = []
        arr =[]

        for index, row in monthly_data_df.iterrows():
            
            try:
                realDict = arr[index]
                budgetDict = arr[index]
                lastYearDict = arr[index]
            except IndexError:
                realDict = defaultdict(lambda: 0)
                budgetDict = defaultdict(lambda: 0)
                lastYearDict = defaultdict(lambda: 0)

            realDict[month] += row["real_value"]
            self.total_real_value += row["real_value"]
            self.total_budget_value += row["budget_value"]
            self.total_last_year_real_value += row["last_year_real_value"]
            self.real_value_dict[month] = self.total_real_value

            cumum_df = {
                "date": valueDict["date"],
                "real_value": self.total_real_value,
                "budget_value": self.total_budget_value,
                "last_year_real_value": self.total_last_year_real_value
            }
            
            if(valueDict["cumulative_actual"] != ""):
                cumum_df[valueDict["cumulative_actual"]] = self.calculate_actual(self.real_value_dict, monthly_data_df, month)

            cumulative_data.append(cumum_df)

        return cumulative_data

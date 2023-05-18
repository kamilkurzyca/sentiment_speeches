from prepare_financial_data import PrepareFinancialData
import seaborn as sns


def plot_speach(index_start, index_end, rates, bis_data_vis):
    
    financial_data_object = PrepareFinancialData('1d', '^GSPC', bis_data_vis)
    f = sns.lineplot(data=financial_data_object.rates_of_return, x='Date', y=rates)
    minimum = financial_data_object.rates_of_return[rates].min()
    maximum = financial_data_object.rates_of_return[rates].max()
    f.vlines(financial_data_object.bis_data.index.values, color='tab:orange',ymin=minimum,ymax=maximum, ls='--', lw=0.2)

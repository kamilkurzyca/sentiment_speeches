import yfinance as yf
import pandas as pd
import numpy as np


class PrepareFinancialData():

    def __init__(self, interval: str, index_name: str, bis_data):
        """


        Args:
            interval (str): granulation of data that we want to obtain  eg. 1h
            bis_data (PrepareBisData) instance of PrepareBisData class for preparing data from speeches
            index_name (str): shortcut of an finacial index or stock eg. ^GSPC

        Returns:
            None.

        """

        index_ticker = yf.Ticker(index_name)
        self.bis_data = bis_data.create_bis_data()
        self.data = index_ticker.history(start=self.bis_data.index[0], end=self.bis_data.index[-1], interval=interval)
        self.historical_data = self._change_data_format(self.data)
        self.rates_of_return = self.create_rates_of_return()
        self.create_normalized_rates_of_return()
        self.binary_returns = self.create_binary_returns()
        self.create_speech_variables()

    def create_rates_of_return(self, quantile_treshold: float = 0.9, window_of_moving_average: int = 5):
        """
        This function will create rates of return from historical data        

        Args:
            quantile_treshold (float, optional): parameter for outlier detection. Defaults to 0.9.
            window_of_moving_average (int, optional): Moving average window span. Defaults to 5.

        Returns:
            rates_of_return (DataFrame): Data freame with rates of returns. With following columns:
                rates_of_return- rates of return from each day 
                absolute_rates_of_return- absolute value of rates of return
                moving_average- value of moving average of lenght of window_of_moving_average
        """
        rates_of_return = pd.DataFrame()
        rates_of_return['rates_of_return'] = (self.historical_data['Close']/self.historical_data['Open'])-1
        rates_of_return['absolute_rates_of_return'] = rates_of_return['rates_of_return'].abs()
        rates_of_return['moving_average'] = rates_of_return['rates_of_return'].rolling(
            window=window_of_moving_average).mean()
        self.rates_of_return = rates_of_return
        return rates_of_return

    def create_normalized_rates_of_return(self):
        """
        This function will provide additional columns for rates_of_return data frame
            rates_of_return_diff- absolute diffrence between rates_of_return and moving average
            rates_of_return_norm- absolute ratio of rates_of_return and moving average

        """
        self.rates_of_return['rates_of_return_diff'] = self.rates_of_return['rates_of_return'] - \
            self.rates_of_return['moving_average']
        self.rates_of_return['rates_of_return_diff'] = self.rates_of_return['rates_of_return_diff'].abs()

        self.rates_of_return['rates_of_return_norm'] = self.rates_of_return['rates_of_return'] / \
            self.rates_of_return['moving_average']
        self.rates_of_return['rates_of_return_norm'] = self.rates_of_return['rates_of_return_norm'].abs()

    def create_binary_returns(self, quantile_treshold: float = 0.9):
        """
        This function will create binary variable for columns create in method
        create_normalized_rates_of_return. We will assume that if value is grater than quantile_treshold
        than we have some jump in price and it's not important when not
        Args:
            quantile_treshold (float, optional): parameter for outlier detection. Defaults to 0.9.

        Returns:
            binary_rates (DataFrame): data frame with binary flags from normalized rates of return.

        """
        binary_rates = pd.DataFrame()
        binary_rates['Date'] = self.rates_of_return.index
        binary_rates.set_index('Date', inplace=True)
        try:

            self._create_binary_rates(binary_rates, quantile_treshold, 'binary_diff',
                                      self.rates_of_return['rates_of_return_diff'])
            self._create_binary_rates(binary_rates, quantile_treshold, 'binary_norm',
                                      self.rates_of_return['rates_of_return_norm'])
            self._create_binary_rates(binary_rates, quantile_treshold, 'binary', self.rates_of_return['rates_of_return'])

        except Exception as ex:
            raise(f' An exception {ex} occured. Please try to run create_normalized_rates_of_return method first')
        return binary_rates

    def _create_binary_rates(self, df, quantile_treshold, name_of_new_column, column_for_quantization):
        """
        Method for creating binary rates

        Args:
            df (data_frame): data frame we will be adding column at.
            quantile_treshold (float): parameter for outlier detection.
            name_of_new_column (str): name of ne column
            column_for_quantization (DataFrame): column for processing.

        Returns:
            None.

        """
        quantile = column_for_quantization.quantile(quantile_treshold)
        df[name_of_new_column] = np.where(column_for_quantization > quantile, 1, 0)
        df[name_of_new_column].fillna(0, inplace=True)

    @staticmethod
    def _change_data_format(historical_data):
        """
        Changing date format

        Args:
            historical_data (DataFrame): Financial data.

        Returns:
            historical_data (DataFrame): Financial data..

        """
        historical_data.index = pd.to_datetime(historical_data.index.strftime('%Y-%m-%d'), format='%Y-%m-%d')
        return historical_data

    def _shift_speech_data_frame(self, column_to_shift, shift):
        """
        Method for shifting column

        Args:
            column_to_shift (DataFrame): column that we will be shifting.
            shift (int): shift parameter.

        Returns:
            new_column (DataFrame): shifted column.

        """
        new_column = column_to_shift.shift(shift)
        new_column.fillna(0, inplace=True)
        new_column.astype(int)
        return new_column

    def create_speech_variables(self):
        """
        This funtion is generating 1  when speech is present for specific day and 0 other way.
        We are also creating two additional columns with information about speech being yesterday and tommorow

        Returns:
            None.

        """
        self.binary_returns['is_speech'] = self.historical_data.index.map(lambda x: int(x in self.bis_data.index))
        self.binary_returns['speech_was_yeasterday'] = self._shift_speech_data_frame(self.binary_returns['is_speech'], 1)
        self.binary_returns['speech_will_be_tommorow'] = self._shift_speech_data_frame(self.binary_returns['is_speech'], -1)

    def create_one_hot_name(self):
        """
        Function generating data frame with speaker name coded as one hot encoding and binary return data

        Returns:
            DataFrame: speaker data and binary returns data.

        """
        one_hot_name = pd.get_dummies(self.bis_data['Name'])

        return self.binary_returns.merge(one_hot_name, on=['Date', 'Date'])

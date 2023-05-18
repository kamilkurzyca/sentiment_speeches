import PyPDF2
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import nltk
import os
import uuid
from numpy import nan
from nltk.sentiment.vader import SentimentIntensityAnalyzer


class SentimentAnalysis():

    nltk.download('vader_lexicon')

    def __init__(self):
        self.i = 0

    @staticmethod
    def _write_pdf(url: str, file_name: str):
        """
        Funtion for writing pdf form ulr

        Args:
            url (str): url to pdf file.
            file_name (str): name of pdf file.

        Returns:
            None.

        """
        s = requests.Session()
        retries = Retry(total=5,
                        backoff_factor=0.1,
                        status_forcelist=[500, 502, 503, 504])
        s.mount('http://', HTTPAdapter(max_retries=retries))

        with open(f'./bisCrawler/{file_name}.pdf', 'wb') as f:
            f.write(s.request('get', url).content)

    @staticmethod
    def _read_text_form_pdf(file_name: str) -> list:
        """
        Reading pdf from file

        Args:
            file_name (str): name of file to read.

        Returns:
            pdf_text (list): text from file.

        """
        f = open(f'./bisCrawler/{file_name}.pdf', 'rb')
        pdf_reader = PyPDF2.PdfReader(f)
        pdf_text = [p.extract_text() for p in pdf_reader.pages]
        f.close()
        os.remove(f'./bisCrawler/{file_name}.pdf',)
        if len(pdf_text) > 0:
            return pdf_text
        else:
            raise(Exception('Cant read pdf'))

    def __call__(self, url: str):
        """
        Function for sentiment analysis processing

        Args:
            url (str): url of pdf file.

        Returns:
            str: pos is sentiment of document is positive 
            and neg if document sentiment is negative.

        """
        self.i += 1

        try:
            if self.i % 500 == 0:
                print(f'This is {self.i} call of this function')
            if 'pdf' in url.split('.'):
                file_name = uuid.uuid4()
                self._write_pdf(url, file_name)
                pdf_text = self._read_text_form_pdf(file_name)
                sid = SentimentIntensityAnalyzer()
                scores = sid.polarity_scores(' '.join(pdf_text))
                if scores['compound'] > 0:
                    return ('pos',scores['compound'],1)
                else:
                    return ('neg',scores['compound'],0)
            else:
                raise(ValueError('Not a proper link'))
        except Exception as ex:
            print(f'An exception occured {ex}')
            return (nan,nan,nan)

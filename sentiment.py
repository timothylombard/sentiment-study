import csv
from vaderSentiment.vaderSentiment import sentiment as vaderSentiment
import sys
import cPickle as pickle
import os
from HTMLParser import HTMLParser
import re, string
import tableausdk.Extract as tde
import datetime

regex1 = re.compile('[%s]' % re.escape(string.punctuation))
regex2 = re.compile('[%s]' % re.escape(string.digits))
review_dict = {}

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ' '.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

class Review():
    def __init__(self, Id, ProductId, Userid, ProfileName, HelpNumerator, HelpDenominator, Score,Time, Summary, Text):
        self.Id = Id
        self.ProductId = ProductId
        self.Userid= Userid
        self.ProfileName= ProfileName
        self.HelpNumerator = HelpNumerator
        self.HelpDenominator = HelpDenominator
        self.Score = Score
        self.Time = Time
        self.Summary = Summary
        self.Text = Text


def write_sentiment_file(review_dict):
# TDE Createion
    if os.path.isfile("sentiment.tde"):
        os.remove("sentiment.tde")
    sentiment_file = tde.Extract("sentiment.tde")

    #create table def
    RKtableDef = tde.TableDefinition()
    RKtableDef.addColumn("Id", tde.Types.Type.CHAR_STRING) #0
    RKtableDef.addColumn("ProductId", tde.Types.Type.CHAR_STRING) #1
    RKtableDef.addColumn("Userid", tde.Types.Type.CHAR_STRING) #2
    RKtableDef.addColumn("Helpfulness Numerator", tde.Types.Type.DOUBLE) #3
    RKtableDef.addColumn("Helpfullness Denominator", tde.Types.Type.DOUBLE) #4
    RKtableDef.addColumn("Score", tde.Types.Type.DOUBLE) #5
    RKtableDef.addColumn('Date', tde.Types.Type.DATETIME) #21
    RKtableDef.addColumn("Summary", tde.Types.Type.CHAR_STRING) #6
    RKtableDef.addColumn("Text", tde.Types.Type.CHAR_STRING) #7
    RKtableDef.addColumn("Negative", tde.Types.Type.DOUBLE) #3
    RKtableDef.addColumn("Netural", tde.Types.Type.DOUBLE) #3
    RKtableDef.addColumn("Positive", tde.Types.Type.DOUBLE) #3
    RKtableDef.addColumn("Compound", tde.Types.Type.DOUBLE) #3
    RKtableDef.addColumn("c_Negative", tde.Types.Type.DOUBLE) #3
    RKtableDef.addColumn("c_Netural", tde.Types.Type.DOUBLE) #3
    RKtableDef.addColumn("c_Positive", tde.Types.Type.DOUBLE) #3
    RKtableDef.addColumn("c_Compound", tde.Types.Type.DOUBLE) #3

    #create the table
    RKtable = sentiment_file.addTable("Extract", RKtableDef)
    RKnewrow = tde.Row(RKtableDef)

    for review in review_dict.keys():

        try:

            time_str = datetime.datetime.fromtimestamp(int(review_dict[review].Time)).strftime("%Y,%m,%d,%H,%M,%S")
            time_tuple = time_str.split(',')
            # >>> time_tuple
            # ('2011', '04', '26', '17', '00', '00')

            RKnewrow.setCharString(0, review_dict[review].Id)
            RKnewrow.setCharString(1, review_dict[review].ProductId)
            RKnewrow.setCharString(2, review_dict[review].Userid )              
            RKnewrow.setDouble(3, float(review_dict[review].HelpNumerator) )
            RKnewrow.setDouble(4, float(review_dict[review].HelpDenominator))
            RKnewrow.setDouble(5, float(review_dict[review].Score))
            RKnewrow.setDateTime(6, int(time_tuple[0]), int(time_tuple[1]), int(time_tuple[2]), int(time_tuple[3]), int(time_tuple[4]), int(time_tuple[5]), 0)
            RKnewrow.setCharString(7, review_dict[review].Summary)
            RKnewrow.setCharString(8, review_dict[review].Text)
            RKnewrow.setDouble(9, float(review_dict[review].sentiment['neg']))
            RKnewrow.setDouble(10, float(review_dict[review].sentiment['neu']))
            RKnewrow.setDouble(11, float(review_dict[review].sentiment['pos']))
            RKnewrow.setDouble(12, float(review_dict[review].sentiment['compound']))
            RKnewrow.setDouble(13, float(review_dict[review].sentiment2['neg']))
            RKnewrow.setDouble(14, float(review_dict[review].sentiment2['neu']))
            RKnewrow.setDouble(15, float(review_dict[review].sentiment2['pos']))
            RKnewrow.setDouble(16, float(review_dict[review].sentiment2['compound']))           
            RKtable.insert(RKnewrow)
        except:
            print "Bogus Time"

    return sentiment_file


with open('/Volumes/microSD/CustomerSentiment/amazon-fine-foods/Reviews.csv', 'rb') as f:
    reader = csv.reader(f)
    for row in reader:
        Id = row[0]
        ProductId = row[1]
        Userid = row[2]
        ProfileName = row[3]
        HelpNumerator = row[4]
        HelpDenominator = row[5]
        Score = row[6]
        Time = row[7]
        Summary = row[8]
        Text = row[9]
        review_dict[Id] = Review(Id, ProductId, Userid, ProfileName, HelpNumerator, HelpDenominator, Score, Time, Summary, Text)
f.close()
        
for r in review_dict.keys():
    review_dict[str(r)].sentiment = vaderSentiment(review_dict[str(r)].Text)
    new_string = strip_tags(review_dict[r].Text) #remove HTML tags
    new_string = str(regex1.sub('',new_string).lower()) #remove punctation
    new_string = str(regex2.sub('',new_string).lower()) #remove digits
    review_dict[r].ctext = new_string
    review_dict[str(r)].sentiment2 = vaderSentiment(review_dict[str(r)].ctext)


sentiment_file = write_sentiment_file(review_dict)
sentiment_file.close()

# review_dict = pickle.load(open('/Volumes/microSD/CustomerSentiment/amazon-fine-foods/Reviews.p', "rb"))
pickle.dump(review_dict, open('/Volumes/microSD/CustomerSentiment/amazon-fine-foods/Reviews.p', "wb"))

    



        
        


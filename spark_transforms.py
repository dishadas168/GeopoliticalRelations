import findspark
findspark.init()
from pyspark import SparkContext
from pyspark.conf import SparkConf
from pyspark.sql import SparkSession

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.linalg import Vector

from pyspark.ml.feature import Tokenizer, RegexTokenizer, StopWordsRemover
from pyspark.ml.feature import CountVectorizer, IDF
from pyspark.ml import Pipeline
from pyspark.ml.clustering import KMeans
from pyspark.ml.evaluation import ClusteringEvaluator

import os
import time
from datetime import datetime
from functools import reduce
from typing import List

import nltk
from pandas import Series as pd_Series
from pyspark import SparkConf, keyword_only
from pyspark.ml import Pipeline, Transformer
from pyspark.ml.clustering import LDA
from pyspark.ml.feature import (
    CountVectorizer,
    CountVectorizerModel,
    IDF,
    RegexTokenizer,
    StopWordsRemover,
    Tokenizer,
    VectorAssembler,
)
from pyspark.sql import Column, SparkSession, functions as F, types as T
from pyspark.sql.dataframe import DataFrame as pdf
from pyspark.sql.window import Window

spark = SparkSession.builder.appName('News_Cluster').getOrCreate()

df = pd.read_csv('news.csv', index_col=0)
df_sub = df[['description','text']]

# convert pandas dataframe to pyspark dataframe
df_schema = StructType([
                        StructField("description", StringType(), True),
                        StructField("text", StringType(), True)
                       ])

data = spark.createDataFrame(df_sub, schema=df_schema)
data = data.select(concat(col('description'),lit(' '),col("text")).alias('article'))
# Clean special characters
data = data.withColumn('clean_article', (lower(regexp_replace('article', "[^a-zA-Z\\s]", " "))))
data = data.select('clean_article')
tokenizer = RegexTokenizer(inputCol='clean_article', outputCol='token_article')
tokenized_data = tokenizer.transform(data)
stopremove = StopWordsRemover(inputCol='token_article', outputCol='stop_token')
stopremoved_data = stopremove.transform(tokenized_data)


# Filter words which have more than 2 letters
filter_length_udf = udf(lambda row: [x for x in row if len(x) > 2], ArrayType(StringType()))
filtered_data = stopremoved_data.withColumn('words_filtered', filter_length_udf(col('stop_token')))

# CountVectorize
count_vec = CountVectorizer(inputCol='words_filtered', outputCol='c_vec')
cv_model = count_vec.fit(filtered_data)
cv_data = cv_model.transform(filtered_data)

# TF-IDF
idf = IDF(inputCol='c_vec', outputCol='tf_idf')
idf_model = idf.fit(cv_data)
idf_data = idf_model.transform(cv_data)


# Format the data
clean_up = VectorAssembler(inputCols=['tf_idf'],
                           outputCol='features')

cleaner = clean_up.transform(idf_data)

final_data = cleaner.select('features')

#TODO: Process stage_urls until this point and append to processed_data table
#This script is to be triggered by airflow. So run as is.
#Processed_data table is to be queried by end_users
#LDA is performed on articles containing keywords searched by users

num_topics = 3
lda_params_dict = dict(
    featuresCol="features",  # features or tokens_no_stopwords
    optimizer="em",  # 'online' or 'em'
    maxIter=85,
    k=num_topics,
    seed=88,
)
lda = LDA(**lda_params_dict)
model = lda.fit(final_data)

print("Learned topics, as distributions over a lexic of {} words".format(lda.vocabSize()))

topics = lda.describeTopics(20)

vocab = model.vocabulary

topics_words = topics.rdd.map(lambda row: row['termIndices'])\
                         .map(lambda idx_list: [vocab[idx] for idx in idx_list])\
                         .collect()

for idx, topic in enumerate(topics_words):
    print("--------------------------------------------------------------------------------------------------------")
    print(" TOPIC {}".format(idx))
    print("   ".join(topic[:10]))
    print("   ".join(topic[10:]))
    print("--------------------------------------------------------------------------------------------------------")


# lda = LDA(k=3, maxIter = 20)
#
# pipeline_analyse = Pipeline(stages=[count_vec, idf, lda])
# print("Fitting done")
# model = pipeline_analyse.fit(filtered_data)
#
# df_need = model.transform(filtered_data)

# import numpy as np
#
#
# round_vector_udf = F.udf(lambda v: [float(np.round(x,3)) for x in v], ArrayType(FloatType()))
# df_need = df_need.withColumn("topicDistribution",round_vector_udf(df_need.topicDistribution))
#
# argmax_udf = F.udf(lambda lst: float(np.argmax(lst)) if np.sum(lst)>0 else -1, FloatType())
# df_need = df_need.withColumn("max_topic", argmax_udf(df_need.topicDistribution))
#
# print("LDA is done", datetime.datetime.now())
#
# # Extract the model
# lda_model = model.stages[2]
#
# ll = lda_model.logLikelihood(df_need)
# lp = lda_model.logPerplexity(df_need)
# print("The lower bound on the log likelihood of the entire corpus: " + str(ll))
# print("The upper bound on perplexity: " + str(lp))
#
#
# # Output topics. We display the words that contribute the most to each topic
# print("Learned topics, as distributions over a lexic of {} words".format(lda_model.vocabSize()))
#
# topics = lda_model.describeTopics(20)
#
# vocab = model.stages[0].vocabulary
#
# topics_words = topics.rdd.map(lambda row: row['termIndices'])\
#                          .map(lambda idx_list: [vocab[idx] for idx in idx_list])\
#                          .collect()
#
# for idx, topic in enumerate(topics_words):
#     print("--------------------------------------------------------------------------------------------------------")
#     print(" TOPIC {}".format(idx))
#     print("   ".join(topic[:10]))
#     print("   ".join(topic[10:]))
#     print("--------------------------------------------------------------------------------------------------------")


